// Outstanding Report JavaScript
// TallyBridge Reports Module

// State
let currentType = 'receivable';
let currentReport = 'ledgerwise';
let outstandingData = [];
let currentPage = 1;
let pageSize = 50;
let sortColumn = 'closing';
let sortDirection = 'desc';

let lastBillwiseTotals = null;
let lastBillwiseTotalCount = null;
let lastLedgerwiseTotals = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    if (!checkAuth()) return;
    
    initializeDates();
    initFromUrl();
    
    const loaded = await loadCompanies();
    if (loaded) {
        loadOutstandingData();
    }
});

// Initialize from URL params
function initFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const type = params.get('type');
    if (type === 'receivable' || type === 'payable') {
        currentType = type;
        updateActiveSubmenu();
        updateLabels();
    }
    updateTableTitle();
}

// Update active submenu
function updateActiveSubmenu() {
    document.querySelectorAll('.submenu-link[data-type]').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.type === currentType) {
            link.classList.add('active');
        }
    });
}

// Update labels based on type
function updateLabels() {
    const label = currentType === 'receivable' ? 'Receivable' : 'Payable';
    document.getElementById('outstandingLabel').textContent = `Total ${label}`;
    
    // Update header title and badge
    const titleEl = document.getElementById('reportTypeTitle');
    const badgeEl = document.getElementById('reportTypeBadge');
    if (titleEl) titleEl.textContent = label;
    if (badgeEl) {
        badgeEl.textContent = label.toUpperCase();
        if (currentType === 'receivable') {
            badgeEl.style.background = '#dcfce7';
            badgeEl.style.color = '#16a34a';
        } else {
            badgeEl.style.background = '#fee2e2';
            badgeEl.style.color = '#dc2626';
        }
    }
}

// Switch type (receivable/payable)
function switchType(type) {
    currentType = type;
    updateActiveSubmenu();
    updateLabels();
    updateTableTitle();
    history.pushState({}, '', `?type=${type}`);
    loadOutstandingData();
}

// Switch report tab
function switchReport(report) {
    currentReport = report;
    currentPage = 1;
    
    document.querySelectorAll('.report-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.report === report);
    });
    
    updateTableTitle();
    loadOutstandingData();
}

// Update table title based on current tab and type
function updateTableTitle() {
    const tabNames = {
        'ledgerwise': 'Ledger-wise Outstanding',
        'billwise': 'Bill-wise Outstanding',
        'ageing': 'Ageing Analysis'
    };
    const typeLabel = currentType === 'receivable' ? 'RECEIVABLE' : 'PAYABLE';
    const titleEl = document.getElementById('tableTitle');
    if (titleEl) {
        titleEl.textContent = `${tabNames[currentReport] || 'Outstanding'} ${typeLabel}`;
    }
}

// Company change handler
function onCompanyChange() {
    loadOutstandingData();
}

// Period change handler
function onPeriodChange() {
    // Optional: auto-reload on period change
}

// Apply period filter
function applyPeriodFilter() {
    loadOutstandingData();
}

// Reset period filter
function resetPeriodFilter() {
    document.getElementById('fromDate').value = CONFIG.DEFAULT_FROM_DATE;
    document.getElementById('toDate').value = CONFIG.DEFAULT_TO_DATE;
    loadOutstandingData();
}

// Load outstanding data based on current report type
async function loadOutstandingData() {
    showTableLoading('tableBody', getColspan());
    
    try {
        let endpoint = '';
        const fromDate = document.getElementById('fromDate').value;
        const toDate = document.getElementById('toDate').value;
        
        const params = new URLSearchParams();
        params.append('type', currentType);
        if (selectedCompany) params.append('company', selectedCompany);
        if (fromDate) params.append('from_date', fromDate);
        if (toDate) params.append('to_date', toDate);
        
        switch (currentReport) {
            case 'ledger':
                endpoint = `${CONFIG.API_BASE}/outstanding?${params}`;
                break;
            case 'billwise':
                params.append('page', currentPage);
                params.append('page_size', pageSize);
                params.append('include_totals', String(currentPage === 1));
                endpoint = `${CONFIG.API_BASE}/outstanding/billwise?${params}`;
                break;
            case 'ledgerwise':
                params.append('include_totals', String(true));
                endpoint = `${CONFIG.API_BASE}/outstanding/ledgerwise?${params}`;
                break;
            case 'ageing':
                endpoint = `${CONFIG.API_BASE}/outstanding/ageing?${params}`;
                break;
            case 'group':
                endpoint = `${CONFIG.API_BASE}/outstanding/group?${params}`;
                break;
        }
        
        const response = await apiFetch(endpoint);
        // Handle nested response: {success, data: {type, data: [...]}}
        const actualData = response?.data?.data || response?.data || response || [];
        outstandingData = Array.isArray(actualData) ? actualData : [];
        
        // Pass the inner data structure to render
        const renderResponse = response?.data || response;

        if (currentReport === 'billwise') {
            if (renderResponse?.totals) lastBillwiseTotals = renderResponse.totals;
            const tc = renderResponse?.pagination?.total_count;
            if (typeof tc === 'number') lastBillwiseTotalCount = tc;

            if (!renderResponse?.totals && lastBillwiseTotals) renderResponse.totals = lastBillwiseTotals;
            if (renderResponse?.pagination && renderResponse.pagination.total_count == null && typeof lastBillwiseTotalCount === 'number') {
                renderResponse.pagination.total_count = lastBillwiseTotalCount;
            }
        }

        if (currentReport === 'ledgerwise') {
            if (renderResponse?.totals && Object.keys(renderResponse.totals || {}).length) {
                lastLedgerwiseTotals = renderResponse.totals;
            } else if (lastLedgerwiseTotals) {
                renderResponse.totals = lastLedgerwiseTotals;
            }
        }

        renderTable(renderResponse);
        updateStats(renderResponse);
        showToast(`Loaded ${Array.isArray(outstandingData) ? outstandingData.length : 1} records`, 'success');
    } catch (error) {
        console.error('Failed to load outstanding:', error);
        showToast('Failed to load data: ' + error.message, 'error');
        showTableEmpty('tableBody', 'Failed to load data', getColspan());
    }
}

// Get colspan based on report type
function getColspan() {
    switch (currentReport) {
        case 'ledger': return 5;
        case 'billwise': return 8;
        case 'ledgerwise': return 6;
        case 'ageing': return 6;
        case 'group': return 5;
        default: return 5;
    }
}

// Render table based on report type
function renderTable(response) {
    updateTableHeader();
    
    switch (currentReport) {
        case 'ledger':
            renderLedgerTable(response);
            break;
        case 'billwise':
            renderBillwiseTable(response);
            break;
        case 'ledgerwise':
            renderLedgerwiseTable(response);
            break;
        case 'ageing':
            renderAgeingTable(response);
            break;
        case 'group':
            renderGroupTable(response);
            break;
    }
}

// Update table header based on report type
function updateTableHeader() {
    const thead = document.getElementById('tableHead');
    const tfoot = document.getElementById('tableFoot');
    const paginationContainer = document.getElementById('paginationContainer');
    
    let headerHtml = '';
    let showFoot = true;
    let showPagination = false;
    
    switch (currentReport) {
        case 'ledger':
            headerHtml = `<tr>
                <th data-sort="party_name" style="cursor:pointer">PARTY NAME <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="opening" style="cursor:pointer">OPENING <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="debit" style="cursor:pointer">DEBIT <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="credit" style="cursor:pointer">CREDIT <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="closing" style="cursor:pointer">CLOSING <span class="sort-icon">↕</span></th>
            </tr>`;
            document.getElementById('tableTitle').textContent = 'Outstanding Summary';
            break;
        case 'billwise':
            headerHtml = `<tr>
                <th data-sort="party_name" style="cursor:pointer">PARTY NAME <span class="sort-icon">↕</span></th>
                <th data-sort="bill_no" style="cursor:pointer">BILL NO <span class="sort-icon">↕</span></th>
                <th data-sort="bill_date" style="cursor:pointer">BILL DATE <span class="sort-icon">↕</span></th>
                <th data-sort="due_date" style="cursor:pointer">DUE DATE <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="bill_amount" style="cursor:pointer">BILL AMT <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="paid" style="cursor:pointer">PAID <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="pending" style="cursor:pointer">PENDING <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="overdue" style="cursor:pointer">OVERDUE <span class="sort-icon">↕</span></th>
            </tr>`;
            document.getElementById('tableTitle').textContent = 'Bill-wise Outstanding';
            showFoot = false;
            showPagination = true;
            break;
        case 'ledgerwise':
            headerHtml = `<tr>
                <th data-sort="party_name" style="cursor:pointer">PARTY / BILL <span class="sort-icon">↕</span></th>
                <th data-sort="bill_date" style="cursor:pointer">BILL DATE <span class="sort-icon">↕</span></th>
                <th data-sort="due_date" style="cursor:pointer">DUE DATE <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="pending" style="cursor:pointer">PENDING <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="overdue" style="cursor:pointer">OVERDUE <span class="sort-icon">↕</span></th>
                <th>SOURCE</th>
            </tr>`;
            document.getElementById('tableTitle').textContent = 'Ledger-wise Outstanding';
            showFoot = false;
            break;
        case 'ageing':
            headerHtml = `<tr>
                <th data-sort="party_name" style="cursor:pointer">PARTY NAME <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="days_0_30" style="cursor:pointer">0-30 DAYS <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="days_30_60" style="cursor:pointer">30-60 DAYS <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="days_60_90" style="cursor:pointer">60-90 DAYS <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="days_90_plus" style="cursor:pointer">90+ DAYS <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="total" style="cursor:pointer">TOTAL <span class="sort-icon">↕</span></th>
            </tr>`;
            document.getElementById('tableTitle').textContent = 'Ageing Analysis';
            break;
        case 'group':
            headerHtml = `<tr>
                <th data-sort="group_name" style="cursor:pointer">GROUP <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="parties" style="cursor:pointer">PARTIES <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="opening" style="cursor:pointer">OPENING <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="transactions" style="cursor:pointer">TRANSACTIONS <span class="sort-icon">↕</span></th>
                <th class="text-right" data-sort="closing" style="cursor:pointer">CLOSING <span class="sort-icon">↕</span></th>
            </tr>`;
            document.getElementById('tableTitle').textContent = 'Group Outstanding';
            showFoot = false;
            break;
    }
    
    thead.innerHTML = headerHtml;
    tfoot.style.display = showFoot ? '' : 'none';
    paginationContainer.style.display = showPagination ? '' : 'none';
    
    // Re-attach sorting event listeners after header update
    setupSorting();
}

// Render ledger summary table
function renderLedgerTable(response) {
    const tbody = document.getElementById('tableBody');
    // Handle various response formats
    const data = Array.isArray(response?.data) ? response.data : 
                 Array.isArray(response?.ledgers) ? response.ledgers : 
                 Array.isArray(response) ? response : [];
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading-cell">No data found</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(row => `
        <tr>
            <td>${row.ledger_name || '-'}</td>
            <td class="text-right">${formatAmount(row.opening || 0)}</td>
            <td class="text-right">${formatAmount(row.debit || 0)}</td>
            <td class="text-right">${formatAmount(row.credit || 0)}</td>
            <td class="text-right ${(row.closing || 0) >= 0 ? 'amount-positive' : 'amount-negative'}">${formatAmount(row.closing || 0)}</td>
        </tr>
    `).join('');
    
    // Update footer
    const totals = response.totals || {};
    document.getElementById('footOpening').textContent = formatAmount(totals.opening || 0);
    document.getElementById('footDebit').textContent = formatAmount(totals.debit || 0);
    document.getElementById('footCredit').textContent = formatAmount(totals.credit || 0);
    document.getElementById('footClosing').textContent = formatAmount(totals.closing || 0);
    
    document.getElementById('recordCount').textContent = `${data.length} records`;
}

// Render billwise table
function renderBillwiseTable(response) {
    const tbody = document.getElementById('tableBody');
    const data = Array.isArray(response?.data) ? response.data : 
                 Array.isArray(response?.bills) ? response.bills : 
                 Array.isArray(response) ? response : [];
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="loading-cell">No bills found</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(row => `
        <tr>
            <td>${row.party_name || '-'}</td>
            <td>${row.bill_no || '-'}</td>
            <td>${formatDate(row.bill_date)}</td>
            <td>${formatDate(row.due_date)}</td>
            <td class="text-right">${formatAmount(row.bill_amount || 0)}</td>
            <td class="text-right">${formatAmount(row.paid_amount || 0)}</td>
            <td class="text-right ${(row.pending_amount || 0) > 0 ? 'amount-positive' : 'amount-negative'}">${formatAmount(Math.abs(row.pending_amount || 0))}</td>
            <td class="text-right ${(row.overdue_days || 0) > 0 ? 'overdue' : ''}">${row.overdue_days || 0} days</td>
        </tr>
    `).join('');
    
    // Update pagination
    const pagination = response.pagination || {};
    document.getElementById('showingFrom').textContent = ((pagination.page - 1) * pagination.page_size) + 1;
    document.getElementById('showingTo').textContent = Math.min(pagination.page * pagination.page_size, pagination.total_count);
    document.getElementById('totalRecords').textContent = pagination.total_count || 0;
    
    renderBillwisePagination(pagination);
    document.getElementById('recordCount').textContent = `${pagination.total_count || data.length} bills`;
}

// Render billwise pagination
function renderBillwisePagination(pagination) {
    const container = document.getElementById('pagination');
    const totalPages = pagination.total_pages || 1;
    
    let html = '';
    html += `<button ${!pagination.has_prev ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})"><i class="fas fa-chevron-left"></i></button>`;
    
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
    }
    
    html += `<button ${!pagination.has_next ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})"><i class="fas fa-chevron-right"></i></button>`;
    
    container.innerHTML = html;
}

// Go to page (for billwise)
function goToPage(page) {
    currentPage = page;
    loadOutstandingData();
}

// Render ledgerwise table
function renderLedgerwiseTable(response) {
    const tbody = document.getElementById('tableBody');
    const data = Array.isArray(response?.data) ? response.data : 
                 Array.isArray(response?.ledgers) ? response.ledgers : 
                 Array.isArray(response) ? response : [];
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading-cell">No data found</td></tr>';
        return;
    }
    
    let html = '';
    data.forEach(party => {
        // Party header row
        html += `<tr class="party-header"><td colspan="6"><strong>${party.party_name}</strong> - Total: ${formatCurrency(party.party_total)}</td></tr>`;
        
        // Bill rows
        party.bills.forEach(bill => {
            html += `
                <tr class="bill-row">
                    <td style="padding-left: 2rem;">${bill.bill_no}</td>
                    <td>${formatDate(bill.bill_date)}</td>
                    <td>${formatDate(bill.due_date)}</td>
                    <td class="text-right">${formatAmount(bill.pending_amount)}</td>
                    <td class="text-right ${bill.overdue_days > 0 ? 'overdue' : ''}">${bill.overdue_days} days</td>
                    <td>${bill.source || '-'}</td>
                </tr>
            `;
        });
    });
    
    tbody.innerHTML = html;
    document.getElementById('recordCount').textContent = `${data.length} parties`;
}

// Render ageing table
function renderAgeingTable(response) {
    const tbody = document.getElementById('tableBody');
    const data = Array.isArray(response?.data) ? response.data : 
                 Array.isArray(response?.ageing) ? response.ageing : 
                 Array.isArray(response) ? response : [];
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading-cell">No data found</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(row => `
        <tr>
            <td>${row.party_name || '-'}</td>
            <td class="text-right">${formatAmount(row.days_0_30 || 0)}</td>
            <td class="text-right">${formatAmount(row.days_30_60 || 0)}</td>
            <td class="text-right">${formatAmount(row.days_60_90 || 0)}</td>
            <td class="text-right ${(row.days_90_plus || 0) > 0 ? 'overdue' : ''}">${formatAmount(row.days_90_plus || 0)}</td>
            <td class="text-right"><strong>${formatAmount(row.total || 0)}</strong></td>
        </tr>
    `).join('');
    
    document.getElementById('recordCount').textContent = `${data.length} parties`;
}

// Render group table
function renderGroupTable(response) {
    const tbody = document.getElementById('tableBody');
    const data = response.data;
    
    if (!data || !data.group_name) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading-cell">No data found</td></tr>';
        return;
    }
    
    const transactions = (data.debit || 0) - (data.credit || 0);
    
    tbody.innerHTML = `
        <tr>
            <td><strong>${data.group_name || response.group_name}</strong></td>
            <td class="text-right">${data.party_count || 0}</td>
            <td class="text-right">${formatAmount(data.opening || 0)}</td>
            <td class="text-right">${formatAmount(transactions)}</td>
            <td class="text-right"><strong>${formatAmount(data.closing || 0)}</strong></td>
        </tr>
    `;
    
    document.getElementById('recordCount').textContent = '1 group';
}

// Update stats
function updateStats(response) {
    let total = 0;
    let parties = 0;
    
    if (currentReport === 'ledger') {
        const totals = response.totals || {};
        total = Math.abs(totals.closing || 0);
        parties = response.count || (response.data?.length || 0);
    } else if (currentReport === 'billwise') {
        const totals = response.totals || {};
        total = Math.abs(totals.pending_amount || 0);
        parties = response.pagination?.total_count || 0;
    } else if (currentReport === 'ageing') {
        const totals = response.totals || {};
        total = totals.total || 0;
        parties = response.count || (response.data?.length || 0);
    } else if (currentReport === 'ledgerwise') {
        const totals = response.totals || {};
        total = Math.abs(totals.grand_total || 0);
        parties = totals.party_count || 0;
    } else if (currentReport === 'group') {
        total = Math.abs(response.data?.closing || 0);
        parties = response.data?.party_count || 0;
    }
    
    document.getElementById('totalOutstanding').textContent = formatCurrency(total);
    document.getElementById('totalParties').textContent = parties;
}

// Filter table (client-side search)
function filterTable() {
    const search = document.getElementById('globalSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#tableBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(search) ? '' : 'none';
    });
}

// Refresh data
function refreshData() {
    loadOutstandingData();
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
            sortData();
            renderCurrentReport();
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

// Sort data
function sortData() {
    outstandingData.sort((a, b) => {
        let aVal = a[sortColumn];
        let bVal = b[sortColumn];
        
        if (['opening', 'debit', 'credit', 'closing', 'amount'].includes(sortColumn)) {
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

// Render current report after sort
function renderCurrentReport() {
    const tbody = document.getElementById('tableBody');
    if (currentReport === 'ledgerwise') {
        renderLedgerwiseTable(tbody, outstandingData);
    } else if (currentReport === 'billwise') {
        renderBillwiseTable(tbody, outstandingData);
    } else if (currentReport === 'ageing') {
        renderAgeingTable(tbody, outstandingData);
    }
}

// Initialize sorting on page load
document.addEventListener('DOMContentLoaded', () => {
    setupSorting();
});

console.log('TallyBridge Reports - Outstanding JS loaded');
