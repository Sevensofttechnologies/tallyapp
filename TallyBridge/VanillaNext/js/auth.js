/**
 * Authentication & RBAC - Application Starter Kit
 * JWT handling, role-based access control
 * Version: 2.0
 */

const Auth = {
  getToken() {
    return localStorage.getItem('access_token');
  },

  setToken(token) {
    localStorage.setItem('access_token', token);
  },

  clearToken() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('active_company');
  },

  getUser() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch (e) {
        return null;
      }
    }

    const token = this.getToken();
    if (!token) return null;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload;
    } catch (e) {
      return null;
    }
  },

  setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
  },

  isAuthenticated() {
    const token = this.getToken();
    return !!token;
  },

  hasRole(role) {
    const user = this.getUser();
    if (!user) return false;

    const userRole = (user.role || '').toLowerCase().replace('_', '');
    const targetRole = (role || '').toLowerCase().replace('_', '');

    if (targetRole === 'superadmin') {
      return userRole === 'superadmin';
    }
    if (targetRole === 'admin') {
      return ['superadmin', 'admin'].includes(userRole);
    }
    if (targetRole === 'manager') {
      return ['superadmin', 'admin', 'manager'].includes(userRole);
    }
    return true;
  },

  hasPermission(permission) {
    const user = this.getUser();
    if (!user) return false;

    if (user.role === 'super_admin') return true;

    const permissions = user.permissions || [];
    return permissions.includes(permission);
  },

  getActiveCompany() {
    const companyStr = localStorage.getItem('active_company');
    if (companyStr) {
      try {
        return JSON.parse(companyStr);
      } catch (e) {
        return null;
      }
    }
    return null;
  },

  setActiveCompany(company) {
    localStorage.setItem('active_company', JSON.stringify(company));
  },

  async login(email, password) {
    const response = await API.auth.login({ email, password });
    if (response.success && response.data) {
      this.setToken(response.data.access_token);
      this.setUser(response.data.user);
      return response.data;
    }
    throw response;
  },

  async logout() {
    try {
      await API.auth.logout();
    } catch (e) {
      // Ignore logout errors
    }
    this.clearToken();
    // Redirect to website landing page
    window.location.href = '/frontend/website/index.html';
  },

  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = '/frontend/login.html';
      return false;
    }
    return true;
  },

  requireCompany() {
    if (!this.requireAuth()) return false;
    const company = this.getActiveCompany();
    if (!company) {
      window.location.href = '/frontend/dashboard.html?selectCompany=true';
      return false;
    }
    return true;
  },

  requireRole(role) {
    if (!this.requireAuth()) return false;
    if (!this.hasRole(role)) {
      Toast.show('Access denied. Insufficient permissions.', 'error');
      return false;
    }
    return true;
  },

  // Company-specific role check
  getCompanyRole() {
    const company = this.getActiveCompany();
    if (!company) return null;
    return company.role || 'user';
  },

  hasCompanyPermission(permission) {
    const company = this.getActiveCompany();
    if (!company) return false;

    const user = this.getUser();
    if (user?.role === 'super_admin') return true;

    const companyPermissions = company.permissions || [];
    return companyPermissions.includes(permission);
  },

  applyRoleVisibility() {
    const user = this.getUser();
    const role = user?.role || 'user';

    document.body.setAttribute('data-role', role);

    // 1. Core Role Visibility
    document.querySelectorAll('.admin-only').forEach(el => {
      el.style.display = this.hasRole('admin') ? '' : 'none';
    });

    document.querySelectorAll('.manager-only').forEach(el => {
      el.style.display = this.hasRole('manager') ? '' : 'none';
    });

    document.querySelectorAll('.super-admin-only').forEach(el => {
      el.style.display = this.hasRole('super_admin') ? '' : 'none';
    });

    // 2. Granular Permission Visibility
    document.querySelectorAll('[data-permission]').forEach(el => {
      const permission = el.getAttribute('data-permission');
      if (permission && !this.hasPermission(permission)) {
        el.style.display = 'none';
      }
    });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  const publicPages = ['login.html', 'register.html', 'forgot-password.html', 'reset-password.html', 'components.html'];
  const companyRequiredPages = ['users.html', 'companies.html', 'audit.html'];
  const currentPage = window.location.pathname.split('/').pop();

  // Public pages - no auth required
  if (publicPages.includes(currentPage)) {
    return;
  }

  // Check authentication first
  if (!Auth.isAuthenticated()) {
    window.location.href = '/frontend/login.html';
    return;
  }

  // Apply role visibility
  Auth.applyRoleVisibility();

  // Check if company selection is required
  if (companyRequiredPages.includes(currentPage)) {
    const company = Auth.getActiveCompany();
    if (!company) {
      // Show warning and redirect to dashboard
      sessionStorage.setItem('redirect_after_company', window.location.href);
      window.location.href = '/frontend/dashboard.html?selectCompany=true';
      return;
    }
  }

  // Dashboard - check if redirected for company selection
  if (currentPage === 'dashboard.html') {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('selectCompany') === 'true') {
      setTimeout(() => {
        if (typeof Toast !== 'undefined') {
          Toast.warning('Please select a company first to continue');
        }
        // Highlight company dropdown
        const dropdown = document.getElementById('company-dropdown');
        if (dropdown) {
          dropdown.classList.add('highlight-pulse');
          setTimeout(() => dropdown.classList.remove('highlight-pulse'), 3000);
        }
      }, 500);
    }
  }
});

window.Auth = Auth;
