// Voucher Report JavaScript
// TallyBridge Reports Module

// State
let allVouchers = [];
let filteredVouchers = [];
let currentPage = 1;
let pageSize = CONFIG.DEFAULT_PAGE_SIZE;
let sortColumn = 'date';
let sortDirection = 'desc';
let selectedVoucherType = 'Sales';

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    if (!checkAuth()) return;
    
    initializeDates();
    initFromUrl();
    setupEventListeners();
    
    const loaded = await loadCompanies();
    if (loaded) {
        document.getElementById('voucherType').value = selectedVoucherType;
        loadVouchers();
    }
});

// Initialize from URL params
function initFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const type = params.get('type');
    if (type) {
        selectedVoucherType = type;
        updateActiveSubmenu();
    }
}

// Update active submenu
function updateActiveSubmenu() {
    document.querySelectorAll('.submenu-link[data-type]').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.type === selectedVoucherType) {
            link.classList.add('active');
        }
    });
}

// Setup event listeners
function setupEventListeners() {
    // Submenu links
    document.querySelectorAll('.submenu-link[data-type]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            selectedVoucherType = link.dataset.type;
            updateActiveSubmenu();
            document.getElementById('voucherType').value = selectedVoucherType;
            loadVouchers();
            history.pushState({}, '', `?type=${selectedVoucherType}`);
        });
    });
    
    // Table header sorting
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
            sortVouchers();
            renderVouchers();
        });
    });
}

// Update sort icons to show current sort state
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

// Company change handler
function onCompanyChange() {
    loadVouchers();
}

// Load vouchers
async function loadVouchers() {
    showTableLoading('vouchersTableBody', 6);
    
    try {
        const fromDate = document.getElementById('fromDate').value;
        const toDate = document.getElementById('toDate').value;
        const voucherType = document.getElementById('voucherType').value || selectedVoucherType;
        
        allVouchers = await fetchAllVouchers({
            from_date: fromDate,
            to_date: toDate,
            voucher_type: voucherType,
            company: selectedCompany
        });
        
        filterVouchers();
        updateStats();
        showToast(`Loaded ${allVouchers.length} vouchers`, 'success');
    } catch (error) {
        console.error('Failed to load vouchers:', error);
        showToast('Failed to load vouchers: ' + error.message, 'error');
        showTableEmpty('vouchersTableBody', 'Failed to load vouchers', 6);
    }
}

// Fetch all vouchers with pagination
async function fetchAllVouchers(params) {
    const BATCH_SIZE = 1000;
    let offset = 0;
    let allItems = [];
    let hasMore = true;
    
    while (hasMore) {
        const queryParams = new URLSearchParams();
        if (params.voucher_type) queryParams.append('voucher_type', params.voucher_type);
        if (params.from_date) queryParams.append('from_date', params.from_date);
        if (params.to_date) queryParams.append('to_date', params.to_date);
        if (params.company) queryParams.append('company', params.company);
        queryParams.append('limit', BATCH_SIZE);
        queryParams.append('offset', offset);
        
        const response = await apiFetch(`${CONFIG.API_BASE}/vouchers?${queryParams}`);
        // Handle nested response: {success, data: {total, data: [...]}}
        const innerData = response?.data?.data || response?.data || response?.vouchers || response || [];
        const vouchers = Array.isArray(innerData) ? innerData : [];
        allItems.push(...vouchers);
        
        if (vouchers.length < BATCH_SIZE) {
            hasMore = false;
        } else {
            offset += BATCH_SIZE;
        }
    }
    
    return allItems;
}

// Filter vouchers
function filterVouchers() {
    const searchTerm = document.getElementById('globalSearch').value.toLowerCase();
    const partyFilter = document.getElementById('partyFilter').value.toLowerCase();
    
    filteredVouchers = allVouchers.filter(v => {
        if (partyFilter && !v.party_name?.toLowerCase().includes(partyFilter)) return false;
        
        if (searchTerm) {
            const searchFields = [
                v.voucher_number,
                v.party_name,
                v.narration,
                v.voucher_type,
                v.reference_number
            ].filter(Boolean).join(' ').toLowerCase();
            
            if (!searchFields.includes(searchTerm)) return false;
        }
        
        return true;
    });
    
    sortVouchers();
    currentPage = 1;
    renderVouchers();
    updateVoucherCount();
}

// Sort vouchers
function sortVouchers() {
    filteredVouchers.sort((a, b) => {
        let aVal = a[sortColumn];
        let bVal = b[sortColumn];
        
        if (sortColumn === 'date') {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        }
        
        if (sortColumn === 'amount') {
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

// Render vouchers
function renderVouchers() {
    const tbody = document.getElementById('vouchersTableBody');
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageVouchers = filteredVouchers.slice(start, end);
    
    if (pageVouchers.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="6" class="loading-cell">
                <div class="empty-state"><i class="fas fa-inbox"></i><p>No vouchers found</p></div>
            </td></tr>
        `;
        return;
    }
    
    tbody.innerHTML = pageVouchers.map(v => {
        const typeClass = v.voucher_type?.toLowerCase().replace(/\s+/g, '-') || 'other';
        const amount = parseFloat(v.amount) || 0;
        
        return `
            <tr>
                <td>${formatDate(v.date)}</td>
                <td><span class="voucher-type-tag ${typeClass}">${v.voucher_type}</span></td>
                <td>${v.voucher_number || '-'}</td>
                <td>${v.party_name || '-'}</td>
                <td class="text-right">${formatCurrency(amount)}</td>
                <td class="text-center">
                    <button class="action-btn" onclick="viewVoucher('${v.guid}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            </tr>
        `;
    }).join('');
    
    renderPagination();
    updateShowingInfo();
}

// Render pagination
function renderPagination() {
    const totalPages = Math.ceil(filteredVouchers.length / pageSize);
    const pagination = document.getElementById('pagination');
    
    let html = '';
    
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})"><i class="fas fa-chevron-left"></i></button>`;
    
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        html += `<button onclick="goToPage(1)">1</button>`;
        if (startPage > 2) html += `<button disabled>...</button>`;
    }
    
    for (let i = startPage; i <= endPage; i++) {
        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) html += `<button disabled>...</button>`;
        html += `<button onclick="goToPage(${totalPages})">${totalPages}</button>`;
    }
    
    html += `<button ${currentPage === totalPages || totalPages === 0 ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})"><i class="fas fa-chevron-right"></i></button>`;
    
    pagination.innerHTML = html;
}

// Go to page
function goToPage(page) {
    currentPage = page;
    renderVouchers();
    document.querySelector('.table-container').scrollTop = 0;
}

// Update showing info
function updateShowingInfo() {
    const start = filteredVouchers.length > 0 ? (currentPage - 1) * pageSize + 1 : 0;
    const end = Math.min(currentPage * pageSize, filteredVouchers.length);
    
    document.getElementById('showingFrom').textContent = start;
    document.getElementById('showingTo').textContent = end;
    document.getElementById('totalRecords').textContent = filteredVouchers.length;
}

// Update voucher count
function updateVoucherCount() {
    document.getElementById('voucherCount').textContent = `${filteredVouchers.length} vouchers`;
}

// Update stats
function updateStats() {
    let sales = 0, purchase = 0, payment = 0, receipt = 0;
    
    allVouchers.forEach(v => {
        const type = v.voucher_type?.toLowerCase() || '';
        const amount = Math.abs(parseFloat(v.amount) || 0);
        
        if (type.includes('sales')) sales += amount;
        else if (type.includes('purchase')) purchase += amount;
        else if (type.includes('payment')) payment += amount;
        else if (type.includes('receipt')) receipt += amount;
    });
    
    document.getElementById('totalSales').textContent = formatCurrency(sales);
    document.getElementById('totalPurchase').textContent = formatCurrency(purchase);
    document.getElementById('totalPayment').textContent = formatCurrency(payment);
    document.getElementById('totalReceipt').textContent = formatCurrency(receipt);
}

// View voucher details
async function viewVoucher(guid) {
    console.log('viewVoucher called with guid:', guid);
    try {
        const response = await apiFetch(`${CONFIG.API_BASE}/vouchers/${guid}`);
        console.log('Voucher details response:', response);
        // Handle nested response from TallyBridge
        const data = response?.data || response;
        showVoucherModal(data);
    } catch (error) {
        console.error('Failed to load voucher details:', error);
        showToast('Failed to load voucher details: ' + error.message, 'error');
    }
}

// Show voucher modal
function showVoucherModal(data) {
    console.log('showVoucherModal called with data:', data);
    const voucher = data.voucher || data;
    const entries = data.entries || data.accounting || [];
    const inventory = data.inventory || [];
    const bills = data.bills || [];
    const bank = data.bank || [];
    
    console.log('Voucher:', voucher);
    console.log('Entries:', entries.length, 'Inventory:', inventory.length);
    
    document.getElementById('modalVoucherType').textContent = voucher.voucher_type;
    document.getElementById('modalVoucherNumber').textContent = voucher.voucher_number;
    document.getElementById('modalDate').textContent = formatDate(voucher.date);
    document.getElementById('modalParty').textContent = voucher.party_name || '-';
    document.getElementById('modalRefNo').textContent = voucher.reference_number || '-';
    document.getElementById('modalRefDate').textContent = voucher.reference_date ? formatDate(voucher.reference_date) : '-';
    document.getElementById('modalNarration').textContent = voucher.narration || '-';
    
    // Render ledger entries
    let totalDebit = 0, totalCredit = 0;
    const ledgerHtml = entries.map(e => {
        const amount = parseFloat(e.amount) || 0;
        const debit = amount < 0 ? Math.abs(amount) : 0;
        const credit = amount >= 0 ? amount : 0;
        totalDebit += debit;
        totalCredit += credit;
        
        return `
            <tr>
                <td>${e.ledger}</td>
                <td class="text-right">${debit > 0 ? formatCurrency(debit) : '-'}</td>
                <td class="text-right">${credit > 0 ? formatCurrency(credit) : '-'}</td>
            </tr>
        `;
    }).join('');
    
    document.getElementById('ledgerEntries').innerHTML = ledgerHtml || '<tr><td colspan="3" class="loading-cell">No entries</td></tr>';
    document.getElementById('totalDebit').textContent = formatCurrency(totalDebit);
    document.getElementById('totalCredit').textContent = formatCurrency(totalCredit);
    
    // Render inventory
    const inventoryHtml = inventory.map(i => `
        <tr>
            <td>${i.item || i.stock_item}</td>
            <td class="text-right">${i.quantity}</td>
            <td class="text-right">${formatCurrency(i.rate)}</td>
            <td class="text-right">${formatCurrency(i.amount)}</td>
            <td>${i.godown || '-'}</td>
        </tr>
    `).join('');
    document.getElementById('inventoryItems').innerHTML = inventoryHtml || '<tr><td colspan="5" class="loading-cell">No items</td></tr>';
    document.getElementById('itemCount').textContent = inventory.length;
    
    // Render bills
    const billsHtml = bills.map(b => `
        <tr>
            <td>${b.name || b.bill_name}</td>
            <td>${b.billtype || b.bill_type || '-'}</td>
            <td class="text-right">${formatCurrency(b.amount)}</td>
        </tr>
    `).join('');
    document.getElementById('billAllocations').innerHTML = billsHtml || '<tr><td colspan="3" class="loading-cell">No bills</td></tr>';
    document.getElementById('billCount').textContent = bills.length;
    
    // Render bank
    const bankHtml = bank.map(b => `
        <tr>
            <td>${b.transaction_type || '-'}</td>
            <td>${b.instrument_number || '-'}</td>
            <td>${b.instrument_date ? formatDate(b.instrument_date) : '-'}</td>
            <td>${b.bank_name || '-'}</td>
            <td class="text-right">${b.amount ? formatCurrency(b.amount) : '-'}</td>
        </tr>
    `).join('');
    document.getElementById('bankDetails').innerHTML = bankHtml || '<tr><td colspan="5" class="loading-cell">No bank details</td></tr>';
    document.getElementById('bankCount').textContent = bank.length;
    
    showModalTab('ledger');
    
    const modal = document.getElementById('vmModal');
    const backdrop = document.getElementById('vmBackdrop');
    if (modal && backdrop) {
        // Set voucher type badge class
        const typeEl = document.getElementById('modalVoucherType');
        if (typeEl) {
            const typeClass = voucher.voucher_type?.toLowerCase().replace(/\s+/g, '-') || 'sales';
            typeEl.className = 'vm-type-badge ' + typeClass;
        }
        
        modal.classList.add('show');
        backdrop.classList.add('show');
        console.log('Modal visible now');
    }
}

// Show modal tab
function showModalTab(tabName) {
    document.querySelectorAll('.vm-tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.vm-tab').forEach(b => b.classList.remove('active'));
    
    document.getElementById(tabName + 'Tab').classList.add('active');
    document.querySelector(`.vm-tab[data-tab="${tabName}"]`)?.classList.add('active');
}

// Close modal
function closeModal() {
    const modal = document.getElementById('vmModal');
    const backdrop = document.getElementById('vmBackdrop');
    if (modal) modal.classList.remove('show');
    if (backdrop) backdrop.classList.remove('show');
}

// Apply filters
function applyFilters() {
    loadVouchers();
}

// Reset filters
function resetFilters() {
    document.getElementById('fromDate').value = CONFIG.DEFAULT_FROM_DATE;
    document.getElementById('toDate').value = CONFIG.DEFAULT_TO_DATE;
    document.getElementById('voucherType').value = selectedVoucherType;
    document.getElementById('partyFilter').value = '';
    document.getElementById('globalSearch').value = '';
    
    document.querySelectorAll('.quick-filters .btn-chip').forEach(b => b.classList.remove('active'));
    document.querySelector('.quick-filters .btn-chip:last-child')?.classList.add('active');
    
    loadVouchers();
}

// Set quick filter
function setQuickFilter(period) {
    const today = new Date();
    let fromDate, toDate;
    
    switch (period) {
        case 'today':
            fromDate = toDate = today.toISOString().split('T')[0];
            break;
        case 'week':
            const weekStart = new Date(today);
            weekStart.setDate(today.getDate() - today.getDay());
            fromDate = weekStart.toISOString().split('T')[0];
            toDate = today.toISOString().split('T')[0];
            break;
        case 'month':
            fromDate = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0];
            toDate = today.toISOString().split('T')[0];
            break;
        case 'year':
        default:
            fromDate = CONFIG.DEFAULT_FROM_DATE;
            toDate = CONFIG.DEFAULT_TO_DATE;
    }
    
    document.getElementById('fromDate').value = fromDate;
    document.getElementById('toDate').value = toDate;
    
    document.querySelectorAll('.quick-filters .btn-chip').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    
    loadVouchers();
}

// Change page size
function changePageSize() {
    pageSize = parseInt(document.getElementById('pageSize').value);
    currentPage = 1;
    renderVouchers();
}

// Refresh data
function refreshData() {
    loadVouchers();
}

// Print voucher
function printVoucher() {
    showToast('Print voucher feature coming soon', 'info');
}

console.log('TallyBridge Reports - Vouchers JS loaded');
