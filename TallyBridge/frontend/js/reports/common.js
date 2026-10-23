// Common functions for TallyBridge Reports
// Shared across vouchers.js, outstanding.js, ledger.js

const CONFIG = {
    API_BASE: '/api/v1/reports',
    DEFAULT_FROM_DATE: '2025-04-01',
    DEFAULT_TO_DATE: '2026-03-31',
    DEFAULT_PAGE_SIZE: 50,
    CURRENCY_SYMBOL: '₹',
    CURRENCY_LOCALE: 'en-IN'
};

// Global state
let selectedCompany = '';
let allLedgers = [];

// Initialize dates
function initializeDates() {
    const fromDate = document.getElementById('fromDate');
    const toDate = document.getElementById('toDate');
    if (fromDate) fromDate.value = CONFIG.DEFAULT_FROM_DATE;
    if (toDate) toDate.value = CONFIG.DEFAULT_TO_DATE;
}

// Load companies for dropdown
async function loadCompanies() {
    try {
        const response = await fetch('/api/v1/tally/synced-companies', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
        });
        const data = await response.json();
        
        const select = document.getElementById('companySelect');
        const footer = document.getElementById('currentCompany');
        
        const companies = data.companies || data.data?.companies || [];
        
        if (companies.length > 0) {
            companies.forEach(c => {
                const option = document.createElement('option');
                option.value = c.company_name || c.name;
                option.textContent = c.company_name || c.name;
                select.appendChild(option);
            });
            
            // Use saved company from localStorage, or fallback to first company
            const savedCompany = localStorage.getItem('selectedReportCompany');
            const companyNames = companies.map(c => c.company_name || c.name);
            
            if (savedCompany && companyNames.includes(savedCompany)) {
                selectedCompany = savedCompany;
            } else {
                selectedCompany = companies[0].company_name || companies[0].name;
            }
            
            select.value = selectedCompany;
            if (footer) footer.textContent = selectedCompany;
            
            return true;
        } else {
            if (footer) footer.textContent = 'No companies synced';
            showToast('No companies found. Please sync data first.', 'warning');
            return false;
        }
    } catch (error) {
        console.error('Failed to load companies:', error);
        showToast('Failed to load companies', 'error');
        return false;
    }
}

// Change company
function changeCompany() {
    const select = document.getElementById('companySelect');
    selectedCompany = select.value;
    
    // Save to localStorage for persistence across page refresh
    if (selectedCompany) {
        localStorage.setItem('selectedReportCompany', selectedCompany);
    }
    
    const footer = document.getElementById('currentCompany');
    if (footer) footer.textContent = selectedCompany || 'All Companies';
    
    // Call page-specific reload function if exists
    if (typeof onCompanyChange === 'function') {
        onCompanyChange();
    }
}

// Toggle submenu
function toggleSubmenu(event) {
    event.preventDefault();
    const navItem = event.currentTarget.parentElement;
    const submenu = navItem.querySelector('.submenu');
    navItem.classList.toggle('open');
    if (submenu) submenu.classList.toggle('show');
}

// Format date
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    
    const day = date.getDate().toString().padStart(2, '0');
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    
    return `${day}-${month}-${year}`;
}

// Format currency
function formatCurrency(amount) {
    const num = parseFloat(amount) || 0;
    return CONFIG.CURRENCY_SYMBOL + num.toLocaleString(CONFIG.CURRENCY_LOCALE, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Format amount (without currency symbol)
function formatAmount(value) {
    const num = parseFloat(value) || 0;
    return num.toLocaleString(CONFIG.CURRENCY_LOCALE, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'check-circle',
        error: 'times-circle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas fa-${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Show loading in table
function showTableLoading(tbodyId, colspan = 5) {
    const tbody = document.getElementById(tbodyId);
    if (tbody) {
        tbody.innerHTML = `<tr><td colspan="${colspan}" class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>`;
    }
}

// Show empty state in table
function showTableEmpty(tbodyId, message, colspan = 5) {
    const tbody = document.getElementById(tbodyId);
    if (tbody) {
        tbody.innerHTML = `<tr><td colspan="${colspan}" class="loading-cell">${message}</td></tr>`;
    }
}

// Toggle filters visibility
function toggleFilters() {
    const body = document.getElementById('filtersBody');
    const icon = document.getElementById('filterToggleIcon');
    if (body && icon) {
        body.style.display = body.style.display === 'none' ? 'block' : 'none';
        icon.classList.toggle('fa-chevron-down');
        icon.classList.toggle('fa-chevron-up');
    }
}

// Export placeholder
function exportToExcel() {
    showToast('Export feature coming soon', 'info');
}

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/frontend/login.html';
        return false;
    }
    return true;
}

// API fetch wrapper with auth
async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    };
    
    try {
        const response = await fetch(endpoint, { ...defaultOptions, ...options });
        
        if (response.status === 401) {
            window.location.href = '/frontend/login.html';
            return null;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error: ${endpoint}`, error);
        throw error;
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-dropdown')) {
        const dropdowns = document.querySelectorAll('.custom-dropdown');
        dropdowns.forEach(d => d.style.display = 'none');
    }
});

// Close modal on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        if (typeof closeModal === 'function') closeModal();
    }
});

console.log('TallyBridge Reports - Common JS loaded');
