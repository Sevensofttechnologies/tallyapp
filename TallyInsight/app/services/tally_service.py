"""
Tally Service Module
====================
Handles HTTP/XML communication with Tally Gateway Server.

TALLY GATEWAY:
-------------
Tally exposes a local HTTP server (default port 9000) that accepts:
- XML requests in TDL (Tally Definition Language) format
- Returns XML responses with requested data

CONNECTION:
----------
- URL: http://localhost:9000 (configurable in config.yaml)
- Method: POST
- Content-Type: text/xml
- Encoding: UTF-16 (Tally requirement)

REQUEST TYPES:
-------------
1. Export Data: Fetch records from Tally collections
2. Company Info: Get company details (GUID, AlterID, etc.)
3. Company List: Get all open companies

RESPONSE HANDLING:
-----------------
- Responses are UTF-16 encoded XML
- May have BOM (Byte Order Mark) - must be stripped
- Parse with ElementTree after encoding conversion

SVCURRENTCOMPANY:
----------------
- XML tag to specify target company
- If empty/missing: uses currently active company in Tally
- Must match exact company name in Tally

DEVELOPER NOTES:
---------------
- Always handle connection errors gracefully
- Retry logic for transient failures
- Check company is open in Tally before sync
- AlterID from company_info used for incremental sync detection
"""

import httpx
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree as ET

from ..config import config
from ..utils.logger import logger
from ..utils.decorators import retry, timed
from ..utils.helpers import parse_tally_date, parse_tally_amount, parse_tally_boolean


class TallyService:
    """Service for communicating with Tally via XML"""
    
    def __init__(self):
        self.server = config.tally.server
        self.port = config.tally.port
        self.base_url = f"http://{self.server}:{self.port}"
        self.timeout = config.health.tally_timeout
    
    @property
    def url(self) -> str:
        return self.base_url
    
    @retry(max_attempts=3, initial_delay=2.0, exceptions=(httpx.RequestError, httpx.TimeoutException))
    @timed
    async def send_xml(self, xml_request: str) -> str:
        """Send XML request to Tally and get response"""
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Tally expects UTF-16 encoded XML
                response = await client.post(
                    self.base_url,
                    content=xml_request.encode('utf-16'),
                    headers={'Content-Type': 'text/xml; charset=utf-16'}
                )
                response.raise_for_status()
                
                # Try to decode response - Tally may return UTF-16 or UTF-8
                content = response.content
                try:
                    # Try UTF-16 first
                    return content.decode('utf-16')
                except UnicodeDecodeError:
                    try:
                        # Try UTF-16-LE (without BOM)
                        return content.decode('utf-16-le')
                    except UnicodeDecodeError:
                        try:
                            # Try UTF-8
                            return content.decode('utf-8')
                        except UnicodeDecodeError:
                            # Fallback to latin-1
                            return content.decode('latin-1')
        except httpx.RequestError as e:
            logger.error(f"Tally connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Tally request failed: {e}")
            raise
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Tally and get company info"""
        xml_request = '''<?xml version="1.0" encoding="UTF-16"?>
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Data</TYPE>
                <ID>List of Companies</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                    </STATICVARIABLES>
                </DESC>
            </BODY>
        </ENVELOPE>'''
        
        try:
            response = await self.send_xml(xml_request)
            # Parse response to get company info
            return {
                "connected": True,
                "server": self.server,
                "port": self.port,
                "response_length": len(response)
            }
        except Exception as e:
            return {
                "connected": False,
                "server": self.server,
                "port": self.port,
                "error": str(e)
            }
    
    async def get_open_companies(self) -> List[Dict[str, Any]]:
        """Get list of all open companies in Tally with their periods"""
        # Use TDL report to get company info with period
        xml_request = '''<?xml version="1.0" encoding="UTF-16"?>
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Data</TYPE>
                <ID>CompanyListWithPeriod</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>XML (Data Interchange)</SVEXPORTFORMAT>
                    </STATICVARIABLES>
                    <TDL>
                        <TDLMESSAGE>
                            <REPORT NAME="CompanyListWithPeriod">
                                <FORMS>CompanyListForm</FORMS>
                            </REPORT>
                            <FORM NAME="CompanyListForm">
                                <PARTS>CompanyListPart</PARTS>
                            </FORM>
                            <PART NAME="CompanyListPart">
                                <LINES>CompanyLine</LINES>
                                <REPEAT>CompanyLine : Company</REPEAT>
                                <SCROLLED>Vertical</SCROLLED>
                            </PART>
                            <LINE NAME="CompanyLine">
                                <FIELDS>FldName,FldBooksFrom,FldStartingFrom,FldNumber</FIELDS>
                            </LINE>
                            <FIELD NAME="FldName"><SET>$Name</SET></FIELD>
                            <FIELD NAME="FldBooksFrom"><SET>$BooksFrom</SET></FIELD>
                            <FIELD NAME="FldStartingFrom"><SET>$StartingFrom</SET></FIELD>
                            <FIELD NAME="FldNumber"><SET>$CompanyNumber</SET></FIELD>
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>'''
        
        try:
            response = await self.send_xml(xml_request)
            companies = self._parse_company_list_with_period(response)
            if companies:
                return companies
            # Fallback to simple parsing
            return self._parse_company_list_simple(response)
        except Exception as e:
            logger.error(f"Failed to get open companies: {e}")
            return []
    
    def _parse_company_list_with_period(self, xml_response: str) -> List[Dict[str, Any]]:
        """Parse company list with period from XML response
        
        DEVELOPER NOTE:
        ---------------
        TDL Report returns data in format:
        <FLDNAME>CompanyName</FLDNAME>
        <FLDBOOKSFROM>20180401</FLDBOOKSFROM>
        <FLDSTARTINGFROM>20180401</FLDSTARTINGFROM>
        <FLDNUMBER>100001</FLDNUMBER>
        
        Date format from Tally: YYYYMMDD
        """
        companies = []
        try:
            # Remove BOM if present
            if xml_response.startswith('\ufeff'):
                xml_response = xml_response[1:]
            
            # Debug: Log first 3000 chars of response
            logger.info(f"Tally company list response: {xml_response[:3000]}")
            
            root = ET.fromstring(xml_response)
            
            # Try new TDL format first - look for FLDNAME elements
            fld_names = root.findall(".//FLDNAME")
            if fld_names:
                # Parse TDL report format
                fld_books_from = root.findall(".//FLDBOOKSFROM")
                fld_starting_from = root.findall(".//FLDSTARTINGFROM")
                fld_numbers = root.findall(".//FLDNUMBER")
                
                for i, name_elem in enumerate(fld_names):
                    name = name_elem.text or ""
                    if not name:
                        continue
                    
                    books_from = fld_books_from[i].text if i < len(fld_books_from) and fld_books_from[i].text else ""
                    starting_from = fld_starting_from[i].text if i < len(fld_starting_from) and fld_starting_from[i].text else ""
                    company_number = fld_numbers[i].text if i < len(fld_numbers) and fld_numbers[i].text else ""
                    
                    # Use STARTINGFROM if BOOKSFROM is empty
                    period_from = books_from or starting_from
                    
                    # Convert Tally date format (1-Apr-25 or YYYYMMDD) to YYYY-MM-DD
                    period_from = self._convert_tally_date_to_iso(period_from)
                    
                    companies.append({
                        "name": name,
                        "number": company_number,
                        "books_from": period_from,
                        "books_to": ""
                    })
                
                logger.info(f"Found {len(companies)} open companies in Tally (TDL format)")
                return companies
            
            # Fallback: Try old COMPANY element format
            for company_elem in root.iter("COMPANY"):
                name = company_elem.get("NAME", "")
                if not name:
                    continue
                
                companies.append({
                    "name": name,
                    "number": "",
                    "books_from": "",
                    "books_to": ""
                })
            
            logger.info(f"Found {len(companies)} open companies in Tally (fallback format)")
            return companies
        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")
            return []
    
    def _convert_tally_date_to_iso(self, tally_date: str) -> str:
        """Convert Tally date format to ISO format (YYYY-MM-DD)
        
        Tally formats:
        - 1-Apr-25 (short year)
        - 1-Apr-2025 (full year)
        - 20250401 (YYYYMMDD)
        """
        if not tally_date:
            return ""
        
        tally_date = tally_date.strip()
        
        # Handle YYYYMMDD format
        if len(tally_date) == 8 and tally_date.isdigit():
            return f"{tally_date[:4]}-{tally_date[4:6]}-{tally_date[6:8]}"
        
        # Handle D-Mon-YY or D-Mon-YYYY format
        month_map = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        try:
            parts = tally_date.split('-')
            if len(parts) == 3:
                day = parts[0].zfill(2)
                month = month_map.get(parts[1].lower()[:3], '01')
                year = parts[2]
                
                # Handle 2-digit year
                if len(year) == 2:
                    year_int = int(year)
                    if year_int > 50:
                        year = f"19{year}"
                    else:
                        year = f"20{year}"
                
                return f"{year}-{month}-{day}"
        except:
            pass
        
        return tally_date
    
    def _parse_company_list_simple(self, xml_response: str) -> List[Dict[str, Any]]:
        """Parse company list from XML response
        
        Tally returns: <COMPANY NAME="CompanyName">...</COMPANY>
        """
        companies = []
        try:
            # Remove BOM if present
            if xml_response.startswith('\ufeff'):
                xml_response = xml_response[1:]
            
            root = ET.fromstring(xml_response)
            
            # Find all COMPANY elements - they have NAME attribute
            for company_elem in root.iter("COMPANY"):
                name = company_elem.get("NAME", "")
                if name:
                    companies.append({
                        "name": name,
                        "number": "",
                        "books_from": "",
                        "books_to": ""
                    })
            
            logger.info(f"Found {len(companies)} open companies in Tally")
            return companies
        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")
            return []
    
    async def get_company_info(self) -> Dict[str, Any]:
        """Get current company information from Tally"""
        xml_request = '''<?xml version="1.0" encoding="UTF-16"?>
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Data</TYPE>
                <ID>CurrentCompanyInfo</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <TDL>
                        <TDLMESSAGE>
                            <REPORT NAME="CurrentCompanyInfo">
                                <FORMS>CurrentCompanyInfo</FORMS>
                            </REPORT>
                            <FORM NAME="CurrentCompanyInfo">
                                <PARTS>CurrentCompanyInfo</PARTS>
                            </FORM>
                            <PART NAME="CurrentCompanyInfo">
                                <LINES>CurrentCompanyInfo</LINES>
                                <REPEAT>CurrentCompanyInfo : Company</REPEAT>
                                <SCROLLED>Vertical</SCROLLED>
                            </PART>
                            <LINE NAME="CurrentCompanyInfo">
                                <FIELDS>FldCompanyName,FldBooksFrom,FldLastVoucherDate,FldGUID,FldAlterID</FIELDS>
                            </LINE>
                            <FIELD NAME="FldCompanyName">
                                <SET>$Name</SET>
                            </FIELD>
                            <FIELD NAME="FldBooksFrom">
                                <SET>$BooksFrom</SET>
                            </FIELD>
                            <FIELD NAME="FldLastVoucherDate">
                                <SET>$LastVoucherDate</SET>
                            </FIELD>
                            <FIELD NAME="FldGUID">
                                <SET>$GUID</SET>
                            </FIELD>
                            <FIELD NAME="FldAlterID">
                                <SET>$AlterID</SET>
                            </FIELD>
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>'''
        
        try:
            response = await self.send_xml(xml_request)
            return self._parse_company_info(response)
        except Exception as e:
            logger.error(f"Failed to get company info: {e}")
            return {"error": str(e)}
    
    def _parse_company_info(self, xml_response: str) -> Dict[str, Any]:
        """Parse company info from XML response"""
        try:
            # Remove BOM if present
            if xml_response.startswith('\ufeff'):
                xml_response = xml_response[1:]
            
            root = ET.fromstring(xml_response)
            
            company_name = ""
            books_from = ""
            last_voucher_date = ""
            guid = ""
            alterid = 0
            
            # Find company info fields
            for elem in root.iter():
                if elem.tag == "FLDCOMPANYNAME":
                    company_name = elem.text or ""
                elif elem.tag == "FLDBOOKSFROM":
                    books_from = parse_tally_date(elem.text) or ""
                elif elem.tag == "FLDLASTVOUCHERDATE":
                    last_voucher_date = parse_tally_date(elem.text) or ""
                elif elem.tag == "FLDGUID":
                    guid = elem.text or ""
                elif elem.tag == "FLDALTERID":
                    try:
                        alterid = int(elem.text or 0)
                    except:
                        alterid = 0
            
            return {
                "company_name": company_name,
                "books_from": books_from,
                "last_voucher_date": last_voucher_date,
                "guid": guid,
                "alterid": alterid
            }
        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")
            return {"error": f"XML parse error: {e}"}
    
    async def export_data(self, report_name: str, tdl_xml: str) -> str:
        """Export data from Tally using TDL XML"""
        xml_request = f'''<?xml version="1.0" encoding="UTF-16"?>
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Data</TYPE>
                <ID>{report_name}</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                        <SVCURRENTCOMPANY>{config.tally.company}</SVCURRENTCOMPANY>
                        <SVFROMDATE>{config.tally.from_date.replace('-', '')}</SVFROMDATE>
                        <SVTODATE>{config.tally.to_date.replace('-', '')}</SVTODATE>
                    </STATICVARIABLES>
                    <TDL>
                        <TDLMESSAGE>
                            {tdl_xml}
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>'''
        
        return await self.send_xml(xml_request)
    
    def parse_tabular_response(self, xml_response: str, field_names: List[str]) -> List[Dict[str, Any]]:
        """Parse tabular XML response into list of dictionaries"""
        rows = []
        try:
            # Remove BOM if present
            if xml_response.startswith('\ufeff'):
                xml_response = xml_response[1:]
            
            # Split by newlines and parse each row
            lines = xml_response.strip().split('\r\n')
            
            for line in lines:
                if not line.strip():
                    continue
                
                values = line.split('\t')
                if len(values) >= len(field_names):
                    row = {}
                    for i, field in enumerate(field_names):
                        value = values[i] if i < len(values) else ""
                        # Handle null marker
                        if value == "ñ":
                            value = None
                        row[field] = value
                    rows.append(row)
        except Exception as e:
            logger.error(f"Error parsing tabular response: {e}")
        
        return rows


    async def get_last_alter_ids(self) -> Dict[str, int]:
        """Get last AlterID for Master and Transaction from Tally"""
        xml_request = '''<?xml version="1.0" encoding="UTF-16"?>
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Data</TYPE>
                <ID>GetAlterIDs</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>ASCII (Comma Delimited)</SVEXPORTFORMAT>
                    </STATICVARIABLES>
                    <TDL>
                        <TDLMESSAGE>
                            <REPORT NAME="GetAlterIDs">
                                <FORMS>GetAlterIDs</FORMS>
                            </REPORT>
                            <FORM NAME="GetAlterIDs">
                                <PARTS>GetAlterIDs</PARTS>
                            </FORM>
                            <PART NAME="GetAlterIDs">
                                <LINES>GetAlterIDs</LINES>
                                <REPEAT>GetAlterIDs : MyCollection</REPEAT>
                                <SCROLLED>Vertical</SCROLLED>
                            </PART>
                            <LINE NAME="GetAlterIDs">
                                <FIELDS>FldAlterMaster,FldAlterTransaction</FIELDS>
                            </LINE>
                            <FIELD NAME="FldAlterMaster">
                                <SET>$AltMstId</SET>
                            </FIELD>
                            <FIELD NAME="FldAlterTransaction">
                                <SET>$AltVchId</SET>
                            </FIELD>
                            <COLLECTION NAME="MyCollection">
                                <TYPE>Company</TYPE>
                                <FILTER>FilterActiveCompany</FILTER>
                            </COLLECTION>
                            <SYSTEM TYPE="Formulae" NAME="FilterActiveCompany">$$IsEqual:##SVCurrentCompany:$Name</SYSTEM>
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>'''
        
        try:
            response = await self.send_xml(xml_request)
            # Parse CSV response: "master_id,transaction_id"
            response = response.strip().replace('"', '')
            if response:
                parts = response.split(',')
                if len(parts) >= 2:
                    master = int(parts[0]) if parts[0].isdigit() else 0
                    transaction = int(parts[1]) if parts[1].isdigit() else 0
                    return {"master": master, "transaction": transaction}
            return {"master": 0, "transaction": 0}
        except Exception as e:
            logger.error(f"Failed to get AlterIDs: {e}")
            return {"master": 0, "transaction": 0}
    
    async def get_company_details(self, company_name: str = "") -> Dict[str, Any]:
        """Get complete company details from Tally including contact, address, statutory info"""
        xml_request = f'''<?xml version="1.0" encoding="UTF-16"?>
        <ENVELOPE>
            <HEADER>
                <VERSION>1</VERSION>
                <TALLYREQUEST>Export</TALLYREQUEST>
                <TYPE>Data</TYPE>
                <ID>Company Details Export</ID>
            </HEADER>
            <BODY>
                <DESC>
                    <STATICVARIABLES>
                        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                        {"<SVCURRENTCOMPANY>" + company_name + "</SVCURRENTCOMPANY>" if company_name else ""}
                    </STATICVARIABLES>
                    <TDL>
                        <TDLMESSAGE>
                            <REPORT NAME="Company Details Export">
                                <FORMS>Company Details Form</FORMS>
                            </REPORT>
                            <FORM NAME="Company Details Form">
                                <PARTS>Company Details Part</PARTS>
                            </FORM>
                            <PART NAME="Company Details Part">
                                <LINES>Company Details Line</LINES>
                                <REPEAT>Company Details Line : Company</REPEAT>
                                <SCROLLED>Vertical</SCROLLED>
                            </PART>
                            <LINE NAME="Company Details Line">
                                <FIELDS>FldName, FldMailingName, FldGUID, FldAlterID, FldEmail, FldTelephone, FldMobile, FldFax, FldWebsite, FldAddress, FldState, FldPincode, FldCountry, FldGSTIN, FldPAN, FldTAN, FldCIN, FldStartingFrom, FldBooksFrom, FldCurrencySymbol, FldCurrencyName, FldDecimalPlaces, FldMaintainInventory</FIELDS>
                            </LINE>
                            <FIELD NAME="FldName"><SET>$Name</SET></FIELD>
                            <FIELD NAME="FldMailingName"><SET>$MailingName</SET></FIELD>
                            <FIELD NAME="FldGUID"><SET>$GUID</SET></FIELD>
                            <FIELD NAME="FldAlterID"><SET>$AlterID</SET></FIELD>
                            <FIELD NAME="FldEmail"><SET>$Email</SET></FIELD>
                            <FIELD NAME="FldTelephone"><SET>$PhoneNumber</SET></FIELD>
                            <FIELD NAME="FldMobile"><SET>$MobileNo</SET></FIELD>
                            <FIELD NAME="FldFax"><SET>$FaxNo</SET></FIELD>
                            <FIELD NAME="FldWebsite"><SET>$Website</SET></FIELD>
                            <FIELD NAME="FldAddress"><SET>$Address</SET></FIELD>
                            <FIELD NAME="FldState"><SET>$StateName</SET></FIELD>
                            <FIELD NAME="FldPincode"><SET>$PinCode</SET></FIELD>
                            <FIELD NAME="FldCountry"><SET>$CountryName</SET></FIELD>
                            <FIELD NAME="FldGSTIN"><SET>$GSTIN</SET></FIELD>
                            <FIELD NAME="FldPAN"><SET>$IncomeTaxNumber</SET></FIELD>
                            <FIELD NAME="FldTAN"><SET>$TANNumber</SET></FIELD>
                            <FIELD NAME="FldCIN"><SET>$CINNumber</SET></FIELD>
                            <FIELD NAME="FldStartingFrom"><SET>$StartingFrom</SET></FIELD>
                            <FIELD NAME="FldBooksFrom"><SET>$BooksFrom</SET></FIELD>
                            <FIELD NAME="FldCurrencySymbol"><SET>$BaseCurrencySymbol</SET></FIELD>
                            <FIELD NAME="FldCurrencyName"><SET>$BaseCurrencyName</SET></FIELD>
                            <FIELD NAME="FldDecimalPlaces"><SET>$DecimalPlaces</SET></FIELD>
                            <FIELD NAME="FldMaintainInventory"><SET>$IsInventoryOn</SET></FIELD>
                        </TDLMESSAGE>
                    </TDL>
                </DESC>
            </BODY>
        </ENVELOPE>'''
        
        try:
            response = await self.send_xml(xml_request)
            return self._parse_company_details(response)
        except Exception as e:
            logger.error(f"Failed to get company details: {e}")
            return {"error": str(e)}
    
    def _parse_company_details(self, xml_response: str) -> Dict[str, Any]:
        """Parse company details from XML response"""
        try:
            if xml_response.startswith('\ufeff'):
                xml_response = xml_response[1:]
            
            root = ET.fromstring(xml_response)
            
            field_mapping = {
                "FLDNAME": "name",
                "FLDMAILINGNAME": "mailing_name",
                "FLDGUID": "guid",
                "FLDALTERID": "alter_id",
                "FLDEMAIL": "email",
                "FLDTELEPHONE": "telephone",
                "FLDMOBILE": "mobile",
                "FLDFAX": "fax",
                "FLDWEBSITE": "website",
                "FLDADDRESS": "address",
                "FLDSTATE": "state",
                "FLDPINCODE": "pincode",
                "FLDCOUNTRY": "country",
                "FLDGSTIN": "gstin",
                "FLDPAN": "pan",
                "FLDTAN": "tan",
                "FLDCIN": "cin",
                "FLDSTARTINGFROM": "starting_from",
                "FLDBOOKSFROM": "books_from",
                "FLDCURRENCYSYMBOL": "currency_symbol",
                "FLDCURRENCYNAME": "currency_name",
                "FLDDECIMALPLACES": "decimal_places",
                "FLDMAINTAININVENTORY": "maintain_inventory"
            }
            
            company = {}
            for elem in root.iter():
                tag = elem.tag.upper()
                text = elem.text.strip() if elem.text else ""
                if tag in field_mapping:
                    company[field_mapping[tag]] = text
            
            # Format into structured response
            return {
                "basic": {
                    "name": company.get("name", ""),
                    "mailing_name": company.get("mailing_name", ""),
                    "guid": company.get("guid", ""),
                    "alter_id": company.get("alter_id", "")
                },
                "contact": {
                    "email": company.get("email", ""),
                    "telephone": company.get("telephone", ""),
                    "mobile": company.get("mobile", ""),
                    "fax": company.get("fax", ""),
                    "website": company.get("website", "")
                },
                "address": {
                    "full_address": company.get("address", ""),
                    "state": company.get("state", ""),
                    "pincode": company.get("pincode", ""),
                    "country": company.get("country", "")
                },
                "statutory": {
                    "gstin": company.get("gstin", ""),
                    "pan": company.get("pan", ""),
                    "tan": company.get("tan", ""),
                    "cin": company.get("cin", "")
                },
                "financial_year": {
                    "starting_from": company.get("starting_from", ""),
                    "books_from": company.get("books_from", "")
                },
                "currency": {
                    "symbol": company.get("currency_symbol", ""),
                    "name": company.get("currency_name", ""),
                    "decimal_places": company.get("decimal_places", "")
                },
                "settings": {
                    "maintain_inventory": company.get("maintain_inventory", "")
                }
            }
        except ET.ParseError as e:
            logger.error(f"XML Parse Error: {e}")
            return {"error": f"XML Parse Error: {e}"}


    async def get_ledger_master(self, company: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all ledger master data from Tally with 30 fields
        
        Fields: guid, name, parent, alias, description, notes, is_revenue, is_deemed_positive,
        opening_balance, closing_balance, mailing_name, address, state, country, pincode,
        email, mobile, pan, gstin, gst_registration_type, gst_supply_type, gst_duty_head,
        tax_rate, bank_account_holder, bank_account_number, bank_ifsc, bank_swift,
        bank_name, bank_branch, credit_period
        """
        xml_request = '''<?xml version="1.0" encoding="utf-8"?>
<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>LedgerReport</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>
            <TDL>
                <TDLMESSAGE>
                    <REPORT NAME="LedgerReport">
                        <FORMS>LedgerForm</FORMS>
                    </REPORT>
                    <FORM NAME="LedgerForm">
                        <PARTS>LedgerPart</PARTS>
                    </FORM>
                    <PART NAME="LedgerPart">
                        <LINES>LedgerLine</LINES>
                        <REPEAT>LedgerLine : Ledger</REPEAT>
                        <SCROLLED>Vertical</SCROLLED>
                    </PART>
                    <LINE NAME="LedgerLine">
                        <FIELDS>FldGuid, FldName, FldParent, FldAlias, FldDescription, FldNotes, FldIsRevenue, FldIsDeemedPositive, FldOpeningBalance, FldClosingBalance, FldMailingName, FldMailingAddress, FldMailingState, FldMailingCountry, FldMailingPincode, FldEmail, FldMobile, FldITPAN, FldGSTN, FldGSTRegistrationType, FldGSTSupplyType, FldGSTDutyHead, FldTaxRate, FldBankAccountHolder, FldBankAccountNumber, FldBankIFSC, FldBankSWIFT, FldBankName, FldBankBranch, FldBillCreditPeriod</FIELDS>
                    </LINE>
                    <FIELD NAME="FldGuid"><SET>$Guid</SET></FIELD>
                    <FIELD NAME="FldName"><SET>$Name</SET></FIELD>
                    <FIELD NAME="FldParent"><SET>if $$IsEqual:$Parent:$$SysName:Primary then "" else $Parent</SET></FIELD>
                    <FIELD NAME="FldAlias"><SET>$OnlyAlias</SET></FIELD>
                    <FIELD NAME="FldDescription"><SET>$Description</SET></FIELD>
                    <FIELD NAME="FldNotes"><SET>$Notes</SET></FIELD>
                    <FIELD NAME="FldIsRevenue"><SET>$IsRevenue</SET></FIELD>
                    <FIELD NAME="FldIsDeemedPositive"><SET>$IsDeemedPositive</SET></FIELD>
                    <FIELD NAME="FldOpeningBalance"><SET>$OpeningBalance</SET></FIELD>
                    <FIELD NAME="FldClosingBalance"><SET>$ClosingBalance</SET></FIELD>
                    <FIELD NAME="FldMailingName"><SET>$MailingName</SET></FIELD>
                    <FIELD NAME="FldMailingAddress"><SET>$Address</SET></FIELD>
                    <FIELD NAME="FldMailingState"><SET>$LedgerStateName</SET></FIELD>
                    <FIELD NAME="FldMailingCountry"><SET>$LedgerCountryName</SET></FIELD>
                    <FIELD NAME="FldMailingPincode"><SET>$Pincode</SET></FIELD>
                    <FIELD NAME="FldEmail"><SET>$Email</SET></FIELD>
                    <FIELD NAME="FldMobile"><SET>$LedgerMobile</SET></FIELD>
                    <FIELD NAME="FldITPAN"><SET>$IncomeTaxNumber</SET></FIELD>
                    <FIELD NAME="FldGSTN"><SET>$PartyGSTIN</SET></FIELD>
                    <FIELD NAME="FldGSTRegistrationType"><SET>$GSTRegistrationType</SET></FIELD>
                    <FIELD NAME="FldGSTSupplyType"><SET>$TypeOfSupply</SET></FIELD>
                    <FIELD NAME="FldGSTDutyHead"><SET>$GSTDutyHead</SET></FIELD>
                    <FIELD NAME="FldTaxRate"><SET>$TaxRate</SET></FIELD>
                    <FIELD NAME="FldBankAccountHolder"><SET>$BankAccountHolderName</SET></FIELD>
                    <FIELD NAME="FldBankAccountNumber"><SET>$BankAccountNumber</SET></FIELD>
                    <FIELD NAME="FldBankIFSC"><SET>$BankIFSCCode</SET></FIELD>
                    <FIELD NAME="FldBankSWIFT"><SET>$BankSWIFTCode</SET></FIELD>
                    <FIELD NAME="FldBankName"><SET>$BankName</SET></FIELD>
                    <FIELD NAME="FldBankBranch"><SET>$BankBranch</SET></FIELD>
                    <FIELD NAME="FldBillCreditPeriod"><SET>$BillCreditPeriod</SET></FIELD>
                    <COLLECTION NAME="Ledger">
                        <TYPE>Ledger</TYPE>
                    </COLLECTION>
                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>'''
        
        try:
            response = await self.send_xml(xml_request)
            return self._parse_ledger_master_response(response)
        except Exception as e:
            logger.error(f"Failed to get ledger master: {e}")
            return {"error": str(e), "total": 0, "ledgers": []}
    
    def _parse_ledger_master_response(self, xml_response: str) -> Dict[str, Any]:
        """Parse ledger master XML response"""
        try:
            if xml_response.startswith('\ufeff'):
                xml_response = xml_response[1:]
            
            root = ET.fromstring(xml_response)
            
            ledgers = []
            current_ledger = {}
            
            field_mapping = {
                "FLDGUID": "guid",
                "FLDNAME": "name",
                "FLDPARENT": "parent",
                "FLDALIAS": "alias",
                "FLDDESCRIPTION": "description",
                "FLDNOTES": "notes",
                "FLDISREVENUE": "is_revenue",
                "FLDISDEEMEDPOSITIVE": "is_deemed_positive",
                "FLDOPENINGBALANCE": "opening_balance",
                "FLDCLOSINGBALANCE": "closing_balance",
                "FLDMAILINGNAME": "mailing_name",
                "FLDMAILINGADDRESS": "address",
                "FLDMAILINGSTATE": "state",
                "FLDMAILINGCOUNTRY": "country",
                "FLDMAILINGPINCODE": "pincode",
                "FLDEMAIL": "email",
                "FLDMOBILE": "mobile",
                "FLDITPAN": "pan",
                "FLDGSTN": "gstin",
                "FLDGSTREGISTRATIONTYPE": "gst_registration_type",
                "FLDGSTSUPPLYTYPE": "gst_supply_type",
                "FLDGSTDUTYHEAD": "gst_duty_head",
                "FLDTAXRATE": "tax_rate",
                "FLDBANKACCOUNTHOLDER": "bank_account_holder",
                "FLDBANKACCOUNTNUMBER": "bank_account_number",
                "FLDBANKIFSC": "bank_ifsc",
                "FLDBANKSWIFT": "bank_swift",
                "FLDBANKNAME": "bank_name",
                "FLDBANKBRANCH": "bank_branch",
                "FLDBILLCREDITPERIOD": "credit_period"
            }
            
            for elem in root.iter():
                tag = elem.tag.upper()
                text = elem.text.strip() if elem.text else ""
                
                if tag in field_mapping:
                    current_ledger[field_mapping[tag]] = text
                    
                    if tag == "FLDBILLCREDITPERIOD":
                        if current_ledger.get("name"):
                            ledgers.append(self._format_ledger(current_ledger))
                        current_ledger = {}
            
            logger.info(f"Parsed {len(ledgers)} ledgers from Tally")
            return {"total": len(ledgers), "ledgers": ledgers}
            
        except ET.ParseError as e:
            logger.error(f"XML Parse Error: {e}")
            return {"error": f"XML Parse Error: {e}", "total": 0, "ledgers": []}
    
    def _format_ledger(self, ledger: dict) -> dict:
        """Format single ledger into structured response"""
        return {
            "basic": {
                "guid": ledger.get("guid", ""),
                "name": ledger.get("name", ""),
                "parent": ledger.get("parent", ""),
                "alias": ledger.get("alias", ""),
                "description": ledger.get("description", ""),
                "notes": ledger.get("notes", "")
            },
            "balance": {
                "opening": ledger.get("opening_balance", ""),
                "closing": ledger.get("closing_balance", "")
            },
            "contact": {
                "mailing_name": ledger.get("mailing_name", ""),
                "address": ledger.get("address", ""),
                "state": ledger.get("state", ""),
                "country": ledger.get("country", ""),
                "pincode": ledger.get("pincode", ""),
                "email": ledger.get("email", ""),
                "mobile": ledger.get("mobile", "")
            },
            "statutory": {
                "pan": ledger.get("pan", ""),
                "gstin": ledger.get("gstin", ""),
                "gst_registration_type": ledger.get("gst_registration_type", ""),
                "gst_supply_type": ledger.get("gst_supply_type", ""),
                "gst_duty_head": ledger.get("gst_duty_head", ""),
                "tax_rate": ledger.get("tax_rate", "")
            },
            "bank": {
                "account_holder": ledger.get("bank_account_holder", ""),
                "account_number": ledger.get("bank_account_number", ""),
                "ifsc": ledger.get("bank_ifsc", ""),
                "swift": ledger.get("bank_swift", ""),
                "bank_name": ledger.get("bank_name", ""),
                "branch": ledger.get("bank_branch", "")
            },
            "settings": {
                "is_revenue": ledger.get("is_revenue", ""),
                "is_deemed_positive": ledger.get("is_deemed_positive", ""),
                "credit_period": ledger.get("credit_period", "")
            }
        }


# Global service instance
tally_service = TallyService()
