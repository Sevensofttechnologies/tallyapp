// Ledger Report JavaScript
// TallyBridge Reports Module

// State (allLedgers is in common.js)
let selectedLedger = '';
let ledgerTransactions = [];
let currentTab = 'transactions';
// API response totals - DO NOT calculate in frontend, use these values
let apiTotalDebit = 0;
let apiTotalCredit = 0;
let apiClosingBalance = 0;
let sortColumn = 'date';
let sortDirection = 'desc';
let currentMainTab = 'ledgerlist';
let ledgerMasterData = [];  // Full ledger master data with 30 fields
let filteredLedgerList = [];
let ledgerListSortColumn = 'name';
let ledgerListSortDirection = 'asc';
let currentLedgerCategory = 'all';  // all, sundry_debtors, sundry_creditors

// ============================================================
// URL STATE PERSISTENCE - Preserves state on browser refresh
// ============================================================
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        ledger: params.get('ledger') || '',
        from: params.get('from') || '',
        to: params.get('to') || '',
        tab: params.get('tab') || 'transactions',
        view: params.get('view') || 'ledgerlist'  // Main view: ledgerlist or transactions
    };
}

function updateUrlParams() {
    const params = new URLSearchParams();
    if (selectedLedger) params.set('ledger', selectedLedger);
    const fromDate = document.getElementById('fromDate')?.value;
    const toDate = document.getElementById('toDate')?.value;
    if (fromDate) params.set('from', fromDate);
    if (toDate) params.set('to', toDate);
    if (currentTab) params.set('tab', currentTab);
    if (currentMainTab) params.set('view', currentMainTab);
    
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, '', newUrl);
}

function restoreStateFromUrl() {
    const urlParams = getUrlParams();
    
    // Restore dates
    if (urlParams.from) {
        document.getElementById('fromDate').value = urlParams.from;
    }
    if (urlParams.to) {
        document.getElementById('toDate').value = urlParams.to;
    }
    
    // Restore tab (transactions/billwise)
    if (urlParams.tab) {
        currentTab = urlParams.tab;
    }
    
    // Restore main view (ledgerlist/transactions)
    if (urlParams.view) {
        currentMainTab = urlParams.view;
    }
    
    // Return ledger to load after companies are loaded
    return urlParams.ledger;
}
// ============================================================

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    if (!checkAuth()) return;
    
    initializeDates();
    
    // Restore state from URL (dates, tab, view)
    const savedLedger = restoreStateFromUrl();
    
    const loaded = await loadCompanies();
    console.log('Companies loaded:', loaded, 'selectedCompany:', selectedCompany);
    if (loaded && selectedCompany) {
        await loadLedgerMaster();  // Load full ledger master data
        await loadLedgerList();    // Load simple list for dropdown
        
        // Restore saved ledger from URL
        if (savedLedger) {
            console.log('Restoring ledger from URL:', savedLedger);
            // First switch to transactions view, then select ledger
            switchMainTab('transactions');
            await selectLedger(savedLedger);
        } else {
            // No saved ledger, show the restored main view
            switchMainTab(currentMainTab);
        }
    } else {
        console.warn('No company selected, cannot load ledgers');
    }
    
    setupLedgerListSorting();
});

// Company change handler
async function onCompanyChange() {
    selectedLedger = '';
    document.getElementById('ledgerSearchInput').value = '';
    document.getElementById('ledgerStats').style.display = 'none';
    document.getElementById('ledgerTabs').style.display = 'none';
    showTableEmpty('tableBody', 'Select a ledger to view transactions', 7);
    document.getElementById('tableTitle').textContent = 'Select a Ledger';
    
    await loadLedgerMaster();
    await loadLedgerList();
    showToast(`Loaded ${ledgerMasterData.length} ledgers for ${selectedCompany}`, 'success');
}

// Switch main tab (Ledger List / Transactions)
function switchMainTab(tab) {
    currentMainTab = tab;
    
    document.querySelectorAll('.report-tab[data-maintab]').forEach(t => {
        t.classList.toggle('active', t.dataset.maintab === tab);
    });
    
    document.getElementById('ledgerListView').style.display = tab === 'ledgerlist' ? 'block' : 'none';
    document.getElementById('transactionsView').style.display = tab === 'transactions' ? 'block' : 'none';
}

// Load ledger master data (30 fields)
async function loadLedgerMaster() {
    const tbody = document.getElementById('ledgerListBody');
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-cell"><div class="spinner"></div> Loading ledgers...</td></tr>';
    }
    
    try {
        console.log('Loading ledger master for company:', selectedCompany);
        const response = await apiFetch(`/api/v1/tally/ledger/master?company=${encodeURIComponent(selectedCompany)}`);
        console.log('Ledger master response:', response);
        
        ledgerMasterData = response?.ledgers || [];
        filteredLedgerList = [...ledgerMasterData];
        
        console.log(`Loaded ${ledgerMasterData.length} ledgers with full data`);
        
        renderLedgerListTable();
        
    } catch (error) {
        console.error('Failed to load ledger master:', error);
        ledgerMasterData = [];
        filteredLedgerList = [];
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">Failed to load ledgers: ' + error.message + '</td></tr>';
        }
    }
}

// Render ledger list table
function renderLedgerListTable() {
    const tbody = document.getElementById('ledgerListBody');
    const countEl = document.getElementById('ledgerListCount');
    
    if (!tbody) return;
    
    if (filteredLedgerList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">No ledgers found</td></tr>';
        if (countEl) countEl.textContent = '0 ledgers';
        return;
    }
    
    let html = '';
    filteredLedgerList.forEach(ledger => {
        const name = ledger.basic?.name || '';
        const parent = ledger.basic?.parent || '';
        const gstin = ledger.statutory?.gstin || '';
        const mobile = ledger.contact?.mobile || '';
        const email = ledger.contact?.email || '';
        const opening = ledger.balance?.opening || '';
        const closing = ledger.balance?.closing || '';
        
        const escapedName = name.replace(/'/g, "\\'").replace(/"/g, '&quot;');
        
        html += `
            <tr onclick="openLedgerTransactions('${escapedName}')" style="cursor: pointer;">
                <td><strong>${name}</strong></td>
                <td>${parent}</td>
                <td>${gstin}</td>
                <td>${mobile}</td>
                <td>${email}</td>
                <td class="text-right">${opening}</td>
                <td class="text-right">${closing}</td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
    if (countEl) countEl.textContent = `${filteredLedgerList.length} ledgers`;
}

// Switch ledger category (All / Sundry Debtors / Sundry Creditors)
function switchLedgerCategory(category) {
    currentLedgerCategory = category;
    
    // Update tab active state
    document.querySelectorAll('.report-tab[data-category]').forEach(t => {
        t.classList.toggle('active', t.dataset.category === category);
    });
    
    // Clear search
    const searchInput = document.getElementById('ledgerListSearch');
    if (searchInput) searchInput.value = '';
    
    // Apply filter
    filterLedgerList();
}

// Filter ledger list by search and category
function filterLedgerList() {
    const searchInput = document.getElementById('ledgerListSearch');
    const search = searchInput ? searchInput.value.toLowerCase() : '';
    
    // First filter by category
    let categoryFiltered = [];
    if (currentLedgerCategory === 'all') {
        categoryFiltered = [...ledgerMasterData];
    } else if (currentLedgerCategory === 'sundry_debtors') {
        categoryFiltered = ledgerMasterData.filter(ledger => {
            const parent = (ledger.basic?.parent || '').toLowerCase();
            return parent === 'sundry debtors';
        });
    } else if (currentLedgerCategory === 'sundry_creditors') {
        categoryFiltered = ledgerMasterData.filter(ledger => {
            const parent = (ledger.basic?.parent || '').toLowerCase();
            return parent === 'sundry creditors';
        });
    }
    
    // Then filter by search
    if (!search) {
        filteredLedgerList = categoryFiltered;
    } else {
        filteredLedgerList = categoryFiltered.filter(ledger => {
            const name = (ledger.basic?.name || '').toLowerCase();
            const parent = (ledger.basic?.parent || '').toLowerCase();
            const gstin = (ledger.statutory?.gstin || '').toLowerCase();
            const mobile = (ledger.contact?.mobile || '').toLowerCase();
            const email = (ledger.contact?.email || '').toLowerCase();
            
            return name.includes(search) || 
                   parent.includes(search) || 
                   gstin.includes(search) || 
                   mobile.includes(search) || 
                   email.includes(search);
        });
    }
    
    renderLedgerListTable();
}

// Open ledger transactions (click on row)
function openLedgerTransactions(ledgerName) {
    selectedLedger = ledgerName;
    document.getElementById('ledgerSearchInput').value = ledgerName;
    
    // Switch to transactions tab
    switchMainTab('transactions');
    
    // Show stats and tabs
    document.getElementById('ledgerStats').style.display = 'grid';
    document.getElementById('ledgerTabs').style.display = 'flex';
    document.getElementById('tableTitle').textContent = ledgerName;
    
    // Load transactions
    loadLedgerTransactions();
}

// Setup ledger list sorting
function setupLedgerListSorting() {
    document.querySelectorAll('#ledgerListTable th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.dataset.sort;
            if (ledgerListSortColumn === column) {
                ledgerListSortDirection = ledgerListSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                ledgerListSortColumn = column;
                ledgerListSortDirection = 'asc';
            }
            updateLedgerListSortIcons();
            sortLedgerList();
            renderLedgerListTable();
        });
    });
}

// Update ledger list sort icons
function updateLedgerListSortIcons() {
    document.querySelectorAll('#ledgerListTable th[data-sort]').forEach(th => {
        const icon = th.querySelector('.sort-icon');
        if (!icon) return;
        
        if (th.dataset.sort === ledgerListSortColumn) {
            icon.textContent = ledgerListSortDirection === 'asc' ? '↑' : '↓';
        } else {
            icon.textContent = '↕';
        }
    });
}

// Sort ledger list
function sortLedgerList() {
    filteredLedgerList.sort((a, b) => {
        let aVal, bVal;
        
        switch (ledgerListSortColumn) {
            case 'name':
                aVal = a.basic?.name || '';
                bVal = b.basic?.name || '';
                break;
            case 'parent':
                aVal = a.basic?.parent || '';
                bVal = b.basic?.parent || '';
                break;
            case 'gstin':
                aVal = a.statutory?.gstin || '';
                bVal = b.statutory?.gstin || '';
                break;
            case 'mobile':
                aVal = a.contact?.mobile || '';
                bVal = b.contact?.mobile || '';
                break;
            case 'email':
                aVal = a.contact?.email || '';
                bVal = b.contact?.email || '';
                break;
            case 'opening':
                aVal = parseFloat((a.balance?.opening || '0').replace(/[₹,]/g, '')) || 0;
                bVal = parseFloat((b.balance?.opening || '0').replace(/[₹,]/g, '')) || 0;
                break;
            case 'closing':
                aVal = parseFloat((a.balance?.closing || '0').replace(/[₹,]/g, '')) || 0;
                bVal = parseFloat((b.balance?.closing || '0').replace(/[₹,]/g, '')) || 0;
                break;
            default:
                aVal = '';
                bVal = '';
        }
        
        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }
        
        if (aVal < bVal) return ledgerListSortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return ledgerListSortDirection === 'asc' ? 1 : -1;
        return 0;
    });
}

// Load ledger list
async function loadLedgerList() {
    try {
        console.log('Loading ledgers for company:', selectedCompany);
        const response = await apiFetch(`${CONFIG.API_BASE}/ledger/list?company=${encodeURIComponent(selectedCompany)}`);
        console.log('Ledger API response:', response);
        
        // Handle response: TallyInsight returns {total, data, ledgers} directly
        // ledgers array contains just names (strings)
        const ledgerNames = response?.ledgers || response?.data?.ledgers || [];
        allLedgers = Array.isArray(ledgerNames) ? ledgerNames : [];
        
        console.log(`Loaded ${allLedgers.length} ledgers`, allLedgers.slice(0, 5));
        
        // Show dropdown immediately after loading
        if (allLedgers.length > 0) {
            showLedgerDropdown();
        } else {
            console.warn('No ledgers found in response');
        }
    } catch (error) {
        console.error('Failed to load ledgers:', error);
        allLedgers = [];
    }
}

// Show ledger dropdown
function showLedgerDropdown() {
    const dropdown = document.getElementById('ledgerDropdown');
    if (!dropdown) {
        console.error('Dropdown element not found');
        return;
    }
    
    const searchInput = document.getElementById('ledgerSearchInput');
    const search = searchInput ? searchInput.value.toLowerCase() : '';
    
    console.log('showLedgerDropdown called, allLedgers count:', allLedgers.length, 'search:', search);
    
    const filtered = allLedgers.filter(l => {
        // ledgers array contains strings (ledger names)
        const name = typeof l === 'string' ? l : (l.name || l.ledger_name || '');
        return name.toLowerCase().includes(search);
    }).slice(0, 50); // Limit to 50 results
    
    console.log('Filtered ledgers:', filtered.length);
    
    if (filtered.length === 0) {
        dropdown.innerHTML = '<div class="dropdown-item disabled">No ledgers found</div>';
    } else {
        dropdown.innerHTML = filtered.map(l => {
            const name = typeof l === 'string' ? l : (l.name || l.ledger_name);
            const escapedName = name.replace(/'/g, "\\'").replace(/"/g, '&quot;');
            return `<div class="dropdown-item" onclick="selectLedger('${escapedName}')">${name}</div>`;
        }).join('');
    }
    
    dropdown.classList.add('show');
    dropdown.style.display = 'block';
}

// Filter ledger dropdown
function filterLedgerDropdown() {
    showLedgerDropdown();
}

// Select ledger
async function selectLedger(ledgerName) {
    selectedLedger = ledgerName;
    document.getElementById('ledgerSearchInput').value = ledgerName;
    const dropdown = document.getElementById('ledgerDropdown');
    if (dropdown) dropdown.style.display = 'none';
    
    document.getElementById('ledgerStats').style.display = 'grid';
    document.getElementById('ledgerTabs').style.display = 'flex';
    document.getElementById('tableTitle').textContent = ledgerName;
    // PDF button is now always visible
    
    // Switch to transactions view if on ledger list
    if (currentMainTab === 'ledgerlist') {
        switchMainTab('transactions');
    }
    
    // Update tab UI based on restored state
    document.querySelectorAll('.report-tab[data-tab]').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === currentTab);
    });
    updateTableForTab();
    
    await loadLedgerTransactions();
    
    // Save state to URL for refresh persistence
    updateUrlParams();
}

// Export PDF - Ledger Report or Bill-wise based on current tab
async function exportLedgerPDF() {
    if (!selectedLedger) {
        alert('Please select a ledger first');
        return;
    }
    
    const fromDate = document.getElementById('fromDate').value;
    const toDate = document.getElementById('toDate').value;
    
    const params = new URLSearchParams();
    params.append('ledger', selectedLedger);
    params.append('company', selectedCompany);
    if (fromDate) params.append('from_date', fromDate);
    if (toDate) params.append('to_date', toDate);
    
    // ============================================================
    // PDF EXPORT LOGIC:
    // - Transactions tab: Export Ledger Report PDF
    // - Bill-wise tab: Export Bill-wise PDF (Pending Bills)
    // ============================================================
    const pdfEndpoint = currentTab === 'billwise' 
        ? '/api/v1/tally/ledger-billwise/pdf' 
        : '/api/v1/tally/ledger-report/pdf';
    
    const fileName = currentTab === 'billwise'
        ? `Billwise_${selectedLedger.replace(/\s+/g, '_')}.pdf`
        : `Ledger_${selectedLedger.replace(/\s+/g, '_')}.pdf`;
    
    try {
        // Fetch PDF with authentication
        const token = localStorage.getItem('token');
        const response = await fetch(`${pdfEndpoint}?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        // Create blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (error) {
        console.error('PDF export failed:', error);
        alert('Failed to export PDF: ' + error.message);
    }
}

// Reload ledger if selected
function reloadLedgerIfSelected() {
    if (selectedLedger) {
        loadLedgerTransactions();
        // Save state to URL for refresh persistence
        updateUrlParams();
    }
}

// Load ledger transactions
async function loadLedgerTransactions() {
    if (!selectedLedger) return;
    
    showTableLoading('tableBody', 7);
    
    try {
        const fromDate = document.getElementById('fromDate').value;
        const toDate = document.getElementById('toDate').value;
        
        const params = new URLSearchParams();
        params.append('company', selectedCompany);
        if (fromDate) params.append('from_date', fromDate);
        if (toDate) params.append('to_date', toDate);
        
        const response = await apiFetch(`${CONFIG.API_BASE}/ledger/${encodeURIComponent(selectedLedger)}?${params}`);
        
        ledgerTransactions = response.transactions || response.data || [];
        
        updateLedgerStats(response);
        renderLedgerTable();
        showToast(`Loaded ${ledgerTransactions.length} transactions`, 'success');
    } catch (error) {
        console.error('Failed to load ledger transactions:', error);
        showToast('Failed to load transactions: ' + error.message, 'error');
        showTableEmpty('tableBody', 'Failed to load transactions', 7);
    }
}

// Update ledger stats
function updateLedgerStats(response) {
    const summary = response.summary || response;
    
    // Store API totals for table footer - DO NOT recalculate in frontend
    apiTotalDebit = parseFloat(summary.total_debit) || 0;
    apiTotalCredit = parseFloat(summary.total_credit) || 0;
    apiClosingBalance = parseFloat(summary.closing_balance) || 0;
    
    document.getElementById('ledgerOpening').textContent = formatCurrency(summary.opening_balance || 0);
    document.getElementById('ledgerDebit').textContent = formatCurrency(summary.total_debit || 0);
    document.getElementById('ledgerCredit').textContent = formatCurrency(summary.total_credit || 0);
    document.getElementById('ledgerClosing').textContent = formatCurrency(summary.closing_balance || 0);
}

// Switch ledger tab
function switchLedgerTab(tab) {
    currentTab = tab;
    
    document.querySelectorAll('.report-tab[data-tab]').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tab);
    });
    
    updateTableForTab();
    renderLedgerTable();
    
    // Save state to URL for refresh persistence
    updateUrlParams();
}

// Update table header for tab
function updateTableForTab() {
    const thead = document.getElementById('tableHead');
    
    if (currentTab === 'transactions') {
        thead.innerHTML = `
            <tr>
                <th data-sort="date" style="cursor:pointer">DATE <span class="sort-icon">↕</span></th>
                <th data-sort="particulars" style="cursor:pointer">PARTICULARS <span class="sort-icon">↕</span></th>
                <th data-sort="voucher_type" style="cursor:pointer">VOUCHER TYPE <span class="sort-icon">↕</span></th>
                <th>VOUCHER NO.</th>
                <th class="text-right" data-sort="debit" style="cursor:pointer">DEBIT <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="credit" style="cursor:pointer">CREDIT <span class="sort-icon">↕</span></th>
                <th class="text-right">BALANCE</th>
            </tr>
        `;
    } else {
        // ============================================================
        // BILL-WISE TABLE HEADER (Tally Arrangement)
        // Columns: Date, Ref. No., Opening Amt, Pending Amt, Due On, Overdue By Days
        // Due Date = Bill Date + Credit Period (from API)
        // Overdue Days = Selected Period's To Date - Due Date (from API)
        // ============================================================
        thead.innerHTML = `
            <tr>
                <th data-sort="bill_date" style="cursor:pointer">DATE <span class="sort-icon">↕</span></th>
                <th data-sort="bill_name" style="cursor:pointer">REF. NO. <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="opening_amount" style="cursor:pointer">OPENING AMT <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="pending" style="cursor:pointer">PENDING AMT <span class="sort-icon">↕</span></th>
                <th data-sort="due_date" style="cursor:pointer">DUE ON <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="overdue_days" style="cursor:pointer">OVERDUE BY DAYS <span class="sort-icon">↕</span></th>
            </tr>
        `;
    }
    
    // Re-attach sorting event listeners after header update
    setupSorting();
}

// Render ledger table
function renderLedgerTable() {
    const tbody = document.getElementById('tableBody');
    
    if (currentTab === 'transactions') {
        renderTransactionsTable(tbody);
    } else {
        renderBillwiseTable(tbody);
    }
}

// ============================================================
// DEVELOPER NOTE: LEDGER TABLE DISPLAY LOGIC
// - Opening Balance row: ALWAYS show (even with 0 transactions)
// - Transactions: Show if available, else show "No transactions in this period"
// - Closing Balance row: ALWAYS show (even with 0 transactions)
// This matches Tally's behavior where Opening/Closing are always visible
// ============================================================
function renderTransactionsTable(tbody) {
    // Calculate running balance
    let balance = 0;
    const openingBalance = parseFloat(document.getElementById('ledgerOpening').textContent.replace(/[₹,]/g, '')) || 0;
    balance = openingBalance;
    
    // Opening Balance row - ALWAYS show
    let html = `
        <tr class="opening-row">
            <td></td>
            <td><strong>Opening Balance</strong></td>
            <td></td>
            <td></td>
            <td class="text-right"></td>
            <td class="text-right"></td>
            <td class="text-right"><strong>${formatAmount(openingBalance)}</strong></td>
        </tr>
    `;
    
    // If no transactions, show message row
    if (ledgerTransactions.length === 0) {
        html += `
            <tr>
                <td colspan="7" class="loading-cell" style="color: #6b7280; font-style: italic;">No transactions in this period</td>
            </tr>
        `;
    }
    
    let totalDebit = 0;
    let totalCredit = 0;
    
    ledgerTransactions.forEach(txn => {
        const debit = parseFloat(txn.debit) || 0;
        const credit = parseFloat(txn.credit) || 0;
        // Running Balance: Previous - Debit + Credit (for Sundry Debtors)
        balance = balance - debit + credit;
        totalDebit += debit;
        totalCredit += credit;
        
        html += `
            <tr>
                <td>${formatDate(txn.date)}</td>
                <td>${txn.particulars || txn.counter_ledger || '-'}</td>
                <td>${txn.voucher_type || '-'}</td>
                <td>${txn.voucher_no || '-'}</td>
                <td class="text-right">${debit > 0 ? formatAmount(debit) : '-'}</td>
                <td class="text-right">${credit > 0 ? formatAmount(credit) : '-'}</td>
                <td class="text-right">${formatAmount(balance)}</td>
            </tr>
        `;
    });
    
    // ============================================================
    // DEVELOPER NOTE: USE API RESPONSE VALUES - DO NOT CALCULATE IN FRONTEND
    // API provides correct totals: apiTotalDebit, apiTotalCredit, apiClosingBalance
    // These are set in updateLedgerStats() from API response
    // Closing = Opening - Debit + Credit (calculated by API)
    // ============================================================
    const closingInDebit = apiClosingBalance < 0;
    
    html += `
        <tr style="background: #f1f5f9; border-top: 2px solid #cbd5e1;">
            <td colspan="4" style="text-align: right; padding: 10px 16px;"><strong>Current Total :</strong></td>
            <td class="text-right" style="padding: 10px 16px;"><strong>${formatAmount(apiTotalDebit)}</strong></td>
            <td class="text-right" style="padding: 10px 16px;"><strong>${formatAmount(apiTotalCredit)}</strong></td>
            <td class="text-right"></td>
        </tr>
        <tr style="background: #e2e8f0;">
            <td colspan="4" style="text-align: right; padding: 10px 16px;"><strong>Closing Balance :</strong></td>
            <td class="text-right" style="padding: 10px 16px;">${closingInDebit ? '<strong>' + formatAmount(Math.abs(apiClosingBalance)) + '</strong>' : ''}</td>
            <td class="text-right" style="padding: 10px 16px;">${!closingInDebit ? '<strong>' + formatAmount(Math.abs(apiClosingBalance)) + '</strong>' : ''}</td>
            <td class="text-right"></td>
        </tr>
    `;
    
    tbody.innerHTML = html;
    document.getElementById('recordCount').textContent = `${ledgerTransactions.length} entries`;
}

// Render billwise table
function renderBillwiseTable(tbody) {
    // Load billwise data from API
    loadLedgerBillwise();
}

// State for billwise data
let ledgerBills = [];

// Load ledger billwise data
async function loadLedgerBillwise() {
    if (!selectedLedger) return;
    
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading-cell"><div class="spinner"></div> Loading bills...</td></tr>';
    
    try {
        const fromDate = document.getElementById('fromDate').value;
        const toDate = document.getElementById('toDate').value;
        
        const params = new URLSearchParams();
        params.append('company', selectedCompany);
        if (fromDate) params.append('from_date', fromDate);
        if (toDate) params.append('to_date', toDate);
        
        const response = await apiFetch(`${CONFIG.API_BASE}/ledger/${encodeURIComponent(selectedLedger)}/billwise?${params}`);
        console.log('Billwise response:', response);
        
        ledgerBills = response?.bills || [];
        // New API response fields
        const billsSubTotalOpening = response?.bills_sub_total_opening || 0;
        const billsSubTotalPending = response?.bills_sub_total_pending || 0;
        const onAccountVouchers = response?.on_account_vouchers || [];
        const onAccountTotal = response?.on_account_total || 0;
        const grandTotalOpening = response?.grand_total_opening || 0;
        const grandTotalPending = response?.grand_total_pending || 0;
        
        // ============================================================
        // BILL-WISE TABLE LOGIC (Tally Arrangement)
        // - Columns: Date, Ref. No., Opening Amt, Pending Amt, Due On, Overdue By Days
        // - Sub Total row after bills
        // - On Account section with voucher details
        // - Total row at the end
        // ============================================================
        
        if (ledgerBills.length === 0 && onAccountTotal === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading-cell">No pending bills found for this period</td></tr>';
            document.getElementById('recordCount').textContent = '0 bills';
            return;
        }
        
        let html = '';
        
        // Bills rows (Tally arrangement: Date, Ref. No., Opening Amt, Pending Amt, Due On, Overdue By Days)
        ledgerBills.forEach(bill => {
            const openingAmount = bill.opening_amount || 0;
            const pendingAmount = bill.pending_amount || 0;
            const overdueDays = bill.overdue_days || 0;
            const dueDate = bill.due_date || bill.bill_date;
            
            html += `
                <tr>
                    <td>${formatDate(bill.bill_date)}</td>
                    <td>${bill.bill_no || '-'}</td>
                    <td class="text-right">${formatAmount(openingAmount)} Dr</td>
                    <td class="text-right">${formatAmount(pendingAmount)} Dr</td>
                    <td>${formatDate(dueDate)}</td>
                    <td class="text-right ${overdueDays > 0 ? 'text-danger' : ''}">${overdueDays > 0 ? overdueDays : '-'}</td>
                </tr>
            `;
        });
        
        // Sub Total row
        html += `
            <tr style="background: #f1f5f9; border-top: 2px solid #cbd5e1;">
                <td></td>
                <td><strong>Sub Total</strong></td>
                <td class="text-right"><strong>${formatAmount(billsSubTotalOpening)} Dr</strong></td>
                <td class="text-right"><strong>${formatAmount(billsSubTotalPending)} Dr</strong></td>
                <td></td>
                <td></td>
            </tr>
        `;
        
        // On Account section header
        if (onAccountVouchers.length > 0 || onAccountTotal > 0) {
            html += `
                <tr style="background: #e2e8f0;">
                    <td colspan="6"><strong>On Account</strong></td>
                </tr>
            `;
            
            // On Account voucher details
            onAccountVouchers.forEach(voucher => {
                html += `
                    <tr>
                        <td>${formatDate(voucher.voucher_date)}</td>
                        <td>${voucher.voucher_type || ''} ${voucher.voucher_no || ''}</td>
                        <td class="text-right">${formatAmount(voucher.amount)} Dr</td>
                        <td class="text-right">${formatAmount(voucher.amount)} Dr</td>
                        <td></td>
                        <td></td>
                    </tr>
                `;
            });
        }
        
        // Note: Tally does NOT show Total row in Pending Bills view
        // Only Sub Total and On Account are shown
        
        tbody.innerHTML = html;
        document.getElementById('recordCount').textContent = `${ledgerBills.length} bills`;
        
    } catch (error) {
        console.error('Failed to load billwise:', error);
        tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">Failed to load bills: ' + error.message + '</td></tr>';
    }
}

// Refresh data
function refreshData() {
    if (selectedLedger) {
        loadLedgerTransactions();
    } else {
        loadLedgerList();
    }
}

// Setup sorting event listeners
function setupSorting() {
    document.querySelectorAll('.data-table th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.dataset.sort;
            if (sortColumn === column) {
                sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortDirection = 'asc';
            }
            updateSortIcons();
            sortTransactions();
            renderTransactionsTable(document.getElementById('tableBody'));
        });
    });
}

// Update sort icons
function updateSortIcons() {
    document.querySelectorAll('.data-table th[data-sort]').forEach(th => {
        const icon = th.querySelector('.sort-icon');
        if (!icon) return;
        
        if (th.dataset.sort === sortColumn) {
            icon.textContent = sortDirection === 'asc' ? '↑' : '↓';
        } else {
            icon.textContent = '↕';
        }
    });
}

// Sort transactions
function sortTransactions() {
    ledgerTransactions.sort((a, b) => {
        let aVal = a[sortColumn];
        let bVal = b[sortColumn];
        
        if (sortColumn === 'date') {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        }
        
        if (sortColumn === 'debit' || sortColumn === 'credit') {
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
        }
        
        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal?.toLowerCase() || '';
        }
        
        if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
        return 0;
    });
}

// Initialize sorting on page load
document.addEventListener('DOMContentLoaded', () => {
    setupSorting();
});

console.log('TallyBridge Reports - Ledger JS loaded');
