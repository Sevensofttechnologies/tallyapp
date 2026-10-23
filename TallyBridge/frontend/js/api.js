/**
 * API Layer - Application Starter Kit
 * Fetch wrapper with JWT authentication
 * Version: 2.0
 */

const API = {
  baseURL: '/api/v1',

  async request(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');

    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    };

    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    if (options.body && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, config);
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401) {
          this.handleUnauthorized();
        }
        throw { status: response.status, ...data };
      }

      return data;
    } catch (error) {
      if (error.status) throw error;
      throw { status: 0, message: 'Network error', error };
    }
  },

  handleUnauthorized() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    if (!window.location.pathname.includes('login')) {
      window.location.href = '/frontend/login.html';
    }
  },

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },

  post(endpoint, body) {
    return this.request(endpoint, { method: 'POST', body });
  },

  put(endpoint, body) {
    return this.request(endpoint, { method: 'PUT', body });
  },

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  },

  // Auth endpoints
  auth: {
    login: (data) => API.post('/auth/login', data),
    register: (data) => API.post('/auth/register', data),
    logout: () => API.post('/auth/logout'),
    me: () => API.get('/auth/me'),
    changePassword: (data) => API.put('/auth/change-password', data),
    forgotPassword: (email) => API.post('/auth/forgot-password', { email }),
    resetPassword: (data) => API.post('/auth/reset-password', data)
  },

  // Users endpoints
  users: {
    list: (companyId, params = {}) => {
      const query = new URLSearchParams(params).toString();
      return API.get(`/companies/${companyId}/users${query ? '?' + query : ''}`);
    },
    get: (companyId, userId) => API.get(`/companies/${companyId}/users/${userId}`),
    create: (companyId, data) => API.post(`/companies/${companyId}/users`, data),
    update: (companyId, userId, data) => API.put(`/companies/${companyId}/users/${userId}`, data),
    delete: (companyId, userId) => API.delete(`/companies/${companyId}/users/${userId}`),
    updateRole: (companyId, userId, role) => API.put(`/companies/${companyId}/users/${userId}/role`, { role })
  },

  // Companies endpoints
  companies: {
    list: (params = {}) => {
      const query = new URLSearchParams(params).toString();
      return API.get(`/companies${query ? '?' + query : ''}`);
    },
    get: (id) => API.get(`/companies/${id}`),
    create: (data) => API.post('/companies', data),
    update: (id, data) => API.put(`/companies/${id}`, data),
    delete: (id) => API.delete(`/companies/${id}`),
    select: (id) => API.post(`/companies/select/${id}`)
  },

  // Permissions endpoints
  permissions: {
    list: () => API.get('/permissions'),
    getByRole: (role, companyId) => {
      const query = companyId ? `?company_id=${companyId}` : '';
      return API.get(`/permissions/role/${role}${query}`);
    },
    check: (data) => API.post('/permissions/check', data),
    assign: (permissionId, role, companyId) => {
      const data = { permission_id: permissionId, role, company_id: companyId };
      return API.post(`/permissions/assign?permission_id=${permissionId}&role=${role}${companyId ? '&company_id=' + companyId : ''}`, {});
    },
    revoke: (permissionId, role, companyId) => {
      return API.post(`/permissions/revoke?permission_id=${permissionId}&role=${role}${companyId ? '&company_id=' + companyId : ''}`, {});
    }
  },

  // Health endpoints
  health: {
    check: () => API.get('/health'),
    ready: () => fetch('/ready').then(r => r.json())
  },

  // Tally Integration endpoints
  tally: {
    // Health & Status
    health: () => API.get('/tally/health'),
    status: () => API.get('/tally/status'),
    
    // Companies
    getCompanies: () => API.get('/tally/companies'),
    getSyncedCompanies: () => API.get('/tally/synced-companies'),
    sync: (companyName, mode = 'full') => 
      API.post(`/tally/sync?company_name=${encodeURIComponent(companyName)}&sync_mode=${mode}`),
    
    // Ledgers
    getLedgers: (params = {}) => {
      const query = new URLSearchParams(params).toString();
      return API.get(`/tally/ledgers${query ? '?' + query : ''}`);
    },
    getLedgerDetails: (name, company = null) => {
      const query = company ? `?company=${encodeURIComponent(company)}` : '';
      return API.get(`/tally/ledgers/${encodeURIComponent(name)}${query}`);
    },
    
    // Vouchers
    getVouchers: (params = {}) => {
      const query = new URLSearchParams(params).toString();
      return API.get(`/tally/vouchers${query ? '?' + query : ''}`);
    },
    
    // Stock Items
    getStockItems: (params = {}) => {
      const query = new URLSearchParams(params).toString();
      return API.get(`/tally/stock-items${query ? '?' + query : ''}`);
    },
    
    // Groups
    getGroups: (company = null) => {
      const query = company ? `?company=${encodeURIComponent(company)}` : '';
      return API.get(`/tally/groups${query}`);
    },
    
    // Reports
    getTrialBalance: (params = {}) => {
      const query = new URLSearchParams(params).toString();
      return API.get(`/tally/reports/trial-balance${query ? '?' + query : ''}`);
    },
    getOutstanding: (params = {}) => {
      const query = new URLSearchParams(params).toString();
      return API.get(`/tally/reports/outstanding${query ? '?' + query : ''}`);
    },
    getDashboard: (company = null) => {
      const query = company ? `?company=${encodeURIComponent(company)}` : '';
      return API.get(`/tally/reports/dashboard${query}`);
    }
  },

  adminEmailSettings: {
    get: (companyId) => API.get(`/admin/email-settings?company_id=${companyId}`),
    save: (data) => API.put('/admin/email-settings', data),
    test: (data) => API.post('/admin/email-settings/test', data)
  }
};

window.API = API;
