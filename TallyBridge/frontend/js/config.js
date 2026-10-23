/**
 * Application Configuration
 * Application Starter Kit
 */

const CONFIG = {
  // API Base URL
  API_BASE_URL: window.location.origin,
  API_VERSION: 'v1',
  
  // App Info
  APP_NAME: 'Application Starter Kit',
  APP_VERSION: '1.2.0',
  
  // Auth Settings
  TOKEN_KEY: 'access_token',
  USER_KEY: 'user',
  COMPANY_KEY: 'active_company',
  
  // Timeouts
  API_TIMEOUT: 30000,
  TOAST_DURATION: 3000,
  
  // Pagination
  DEFAULT_PAGE_SIZE: 10,
  
  // Debug
  DEBUG: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
};

// Make config globally available
window.CONFIG = CONFIG;

console.log('✅ Config loaded:', CONFIG.APP_NAME, CONFIG.APP_VERSION);
