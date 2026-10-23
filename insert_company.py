"""Insert company details into mst_company table"""
import sqlite3

conn = sqlite3.connect('TallyInsight/tally.db')
cursor = conn.cursor()

# Insert company data (from API response)
cursor.execute("""
INSERT OR REPLACE INTO mst_company (
    _company, guid, alter_id, name, formal_name,
    address, state, country, pincode,
    email, mobile, telephone, website,
    gstin, pan, tan, cin,
    books_from, starting_from,
    currency, decimal_places, maintain_inventory
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "Vrushali Infotech Pvt Ltd -21 -25",
    "8fdcfdd1-71cc-4873-99c6-95735225388e",
    102214,
    "Vrushali Infotech Pvt Ltd. 25-26",
    "Indian Rupees",
    "Ananda Niwas Shivshankar Colony No.2",
    "Maharashtra",
    "India",
    "411039",
    "ganesh@vrushaliinfotech.com",
    "7040469030/31,9921640630",
    "",
    "www.vrushaliinfotech.com",
    "",
    "AAECV1138M",
    "",
    "",
    "1-Apr-25",
    "1-Apr-25",
    "INR",
    2,
    1
))

conn.commit()
print("Company data inserted successfully!")

# Verify
cursor.execute("SELECT _company, name, email, address, state FROM mst_company")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
