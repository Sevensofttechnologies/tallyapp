/**
 * Utility Functions - Application Starter Kit
 * Helpers, formatters, common functions
 * Version: 2.0
 */

const Utils = {
  formatDate(dateStr, format = 'short') {
    const date = new Date(dateStr);
    if (isNaN(date)) return '-';
    
    const options = {
      short: { day: '2-digit', month: 'short', year: 'numeric' },
      long: { day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' },
      time: { hour: '2-digit', minute: '2-digit' },
      relative: null
    };
    
    if (format === 'relative') {
      return this.timeAgo(date);
    }
    
    return date.toLocaleDateString('en-IN', options[format] || options.short);
  },
  
  timeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    const intervals = [
      { label: 'year', seconds: 31536000 },
      { label: 'month', seconds: 2592000 },
      { label: 'week', seconds: 604800 },
      { label: 'day', seconds: 86400 },
      { label: 'hour', seconds: 3600 },
      { label: 'minute', seconds: 60 }
    ];
    
    for (const interval of intervals) {
      const count = Math.floor(seconds / interval.seconds);
      if (count >= 1) {
        return `${count} ${interval.label}${count > 1 ? 's' : ''} ago`;
      }
    }
    return 'Just now';
  },
  
  truncate(str, length = 50) {
    if (!str) return '';
    return str.length > length ? str.substring(0, length) + '...' : str;
  },
  
  capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  },
  
  slugify(str) {
    return str.toLowerCase().trim().replace(/[^\w\s-]/g, '').replace(/[\s_-]+/g, '-');
  },
  
  debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
  
  throttle(func, limit = 300) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },
  
  getInitials(name) {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
  },
  
  formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toLocaleString();
  },
  
  validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },
  
  validatePassword(password) {
    const errors = [];
    if (password.length < 8) errors.push('At least 8 characters');
    if (!/[A-Z]/.test(password)) errors.push('One uppercase letter');
    if (!/[a-z]/.test(password)) errors.push('One lowercase letter');
    if (!/[0-9]/.test(password)) errors.push('One number');
    if (!/[!@#$%^&*]/.test(password)) errors.push('One special character (!@#$%^&*)');
    return { valid: errors.length === 0, errors };
  },
  
  escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  },
  
  copyToClipboard(text) {
    if (navigator.clipboard) {
      return navigator.clipboard.writeText(text);
    }
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    return Promise.resolve();
  },
  
  generateId() {
    return Math.random().toString(36).substring(2, 11);
  },
  
  parseQueryParams() {
    const params = new URLSearchParams(window.location.search);
    const result = {};
    for (const [key, value] of params) {
      result[key] = value;
    }
    return result;
  },
  
  setQueryParams(params) {
    const url = new URL(window.location);
    Object.entries(params).forEach(([key, value]) => {
      if (value === null || value === undefined) {
        url.searchParams.delete(key);
      } else {
        url.searchParams.set(key, value);
      }
    });
    window.history.replaceState({}, '', url);
  }
};

window.Utils = Utils;
