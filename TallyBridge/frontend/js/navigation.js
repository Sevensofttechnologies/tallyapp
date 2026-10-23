/**
 * Navigation.js - SPA Navigation System
 * Handles page loading, navigation, and routing
 */

// Global variables
let currentPage = 'home';

// ============================================
// LOAD NAVIGATION BAR
// ============================================
async function loadNavigation() {
  try {
    const navbarContainer = document.getElementById('navbar-container');
    if (!navbarContainer) return;

    const response = await fetch('components/navbar.html');
    if (!response.ok) {
      console.error('Failed to load navbar');
      return;
    }

    const html = await response.text();
    navbarContainer.innerHTML = html;
    navbarContainer.style.display = 'block';

    // Setup navigation listeners
    setupNavListeners();

    // Load current company
    loadCurrentCompany();

    console.log('✅ Navigation loaded');
  } catch (error) {
    console.error('Error loading navigation:', error);
  }
}

// ============================================
// SETUP NAVIGATION LISTENERS
// ============================================
function setupNavListeners() {
  // Nav links
  document.querySelectorAll('.nav-link[data-section]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const section = link.dataset.section;
      if (section) {
        loadPage(section);
      }
    });
  });

  // Sidebar links
  document.querySelectorAll('.sidebar-link[data-section]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const section = link.dataset.section;
      if (section) {
        loadPage(section);
      }
    });
  });

  // Logout button
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout);
  }

  // Mobile menu toggle
  const mobileToggle = document.getElementById('mobileMenuToggle');
  const sidebar = document.querySelector('.sidebar');
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }

  // Company dropdown
  setupCompanyDropdown();
}

// ============================================
// LOAD PAGE (Main SPA Function)
// ============================================
window.loadPage = async function (pageName) {
  try {
    console.log('📄 Loading page:', pageName);

    // Save current page
    if (pageName && !['home', 'login', 'register'].includes(pageName)) {
      localStorage.setItem('currentPage', pageName);
      window.location.hash = pageName;
    }

    const pageContent = document.getElementById('page-content');
    if (!pageContent) return;

    // Hide all current sections
    document.querySelectorAll('.section').forEach(section => {
      section.classList.remove('active');
      section.style.display = 'none';
    });

    // Special pages (login, register) - show modal or load page
    if (pageName === 'login') {
      showLoginPage();
      return;
    }

    if (pageName === 'register') {
      showRegisterPage();
      return;
    }

    // Check authentication for protected pages
    const token = localStorage.getItem('access_token');
    if (!token && !['home', 'login', 'register'].includes(pageName)) {
      Toast.warning('Please login first');
      showLoginPage();
      return;
    }

    // Show navbar for authenticated pages
    const navbarContainer = document.getElementById('navbar-container');
    if (navbarContainer) {
      if (['home', 'login', 'register'].includes(pageName)) {
        navbarContainer.style.display = 'none';
      } else {
        navbarContainer.style.display = 'block';
        if (!navbarContainer.innerHTML.trim()) {
          await loadNavigation();
        }
      }
    }

    // Load page HTML from pages folder
    const response = await fetch(`pages/${pageName}.html`);
    if (!response.ok) {
      Toast.error(`Page not found: ${pageName}`);
      return;
    }

    const html = await response.text();
    pageContent.innerHTML = html;

    // Execute inline scripts
    const scripts = pageContent.querySelectorAll('script');
    scripts.forEach(oldScript => {
      const newScript = document.createElement('script');
      if (oldScript.src) {
        newScript.src = oldScript.src;
      } else {
        newScript.textContent = oldScript.textContent;
      }
      oldScript.parentNode.replaceChild(newScript, oldScript);
    });

    // Show loaded section
    const loadedSection = pageContent.querySelector('.section');
    if (loadedSection) {
      loadedSection.classList.add('active');
      loadedSection.style.display = 'block';
    }

    // Update active nav link
    updateActiveNavLink(pageName);

    // Scroll to top
    window.scrollTo(0, 0);

    currentPage = pageName;
    console.log('✅ Page loaded:', pageName);

  } catch (error) {
    console.error('Error loading page:', error);
    Toast.error('Failed to load page');
  }
};

// ============================================
// LOGIN PAGE
// ============================================
function showLoginPage() {
  const pageContent = document.getElementById('page-content');
  const navbarContainer = document.getElementById('navbar-container');

  if (navbarContainer) navbarContainer.style.display = 'none';

  pageContent.innerHTML = `
    <section id="login" class="section active" style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
      <div class="card" style="width: 100%; max-width: 400px; padding: 40px;">
        <div style="text-align: center; margin-bottom: 32px;">
          <h1 style="font-size: 2rem; margin-bottom: 8px;">🚀 AppStarter</h1>
          <p style="color: var(--text-muted);">Sign in to your account</p>
        </div>
        <form id="loginForm" onsubmit="handleLogin(event)">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input type="email" id="loginEmail" class="form-input" placeholder="you@example.com" required>
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input type="password" id="loginPassword" class="form-input" placeholder="••••••••" required>
          </div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 8px;">Sign In</button>
        </form>
        <div style="text-align: center; margin-top: 24px;">
          <p style="color: var(--text-muted);">
            Don't have an account? <a href="#" onclick="loadPage('register'); return false;" style="color: var(--primary);">Register</a>
          </p>
          <p style="margin-top: 8px;">
            <a href="#" onclick="loadPage('home'); return false;" style="color: var(--text-muted); font-size: 0.9rem;">← Back to Home</a>
          </p>
        </div>
      </div>
    </section>
  `;

  window.location.hash = 'login';
}

// ============================================
// REGISTER PAGE
// ============================================
function showRegisterPage() {
  const pageContent = document.getElementById('page-content');
  const navbarContainer = document.getElementById('navbar-container');

  if (navbarContainer) navbarContainer.style.display = 'none';

  pageContent.innerHTML = `
    <section id="register" class="section active" style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
      <div class="card" style="width: 100%; max-width: 450px; padding: 40px;">
        <div style="text-align: center; margin-bottom: 32px;">
          <h1 style="font-size: 2rem; margin-bottom: 8px;">🚀 Create Account</h1>
          <p style="color: var(--text-muted);">Get started with AppStarter</p>
        </div>
        <form id="registerForm" onsubmit="handleRegister(event)">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
            <div class="form-group">
              <label class="form-label">Last Name</label>
              <input type="text" id="regLastName" class="form-input" placeholder="Doe" required>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input type="email" id="regEmail" class="form-input" placeholder="you@example.com" required>
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input type="password" id="regPassword" class="form-input" placeholder="Min. 8 characters" required minlength="8">
          </div>
          <div class="form-group">
            <label class="form-label">Confirm Password</label>
            <input type="password" id="regConfirmPassword" class="form-input" placeholder="Confirm password" required>
          </div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 8px;">Create Account</button>
        </form>
        <div style="text-align: center; margin-top: 24px;">
          <p style="color: var(--text-muted);">
            Already have an account? <a href="#" onclick="loadPage('login'); return false;" style="color: var(--primary);">Sign In</a>
          </p>
          <p style="margin-top: 8px;">
            <a href="#" onclick="loadPage('home'); return false;" style="color: var(--text-muted); font-size: 0.9rem;">← Back to Home</a>
          </p>
        </div>
      </div>
    </section>
  `;

  window.location.hash = 'register';
}

// ============================================
// AUTH HANDLERS
// ============================================
window.handleLogin = async function (e) {
  e.preventDefault();

  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  try {
    const response = await API.auth.login({ email, password });

    if (response.success) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));

      Toast.success('Login successful!');

      // Load navigation and go to dashboard
      await loadNavigation();
      loadPage('dashboard');
    } else {
      Toast.error(response.message || 'Login failed');
    }
  } catch (error) {
    Toast.error('Login failed. Please try again.');
  }
};

window.handleRegister = async function (e) {
  e.preventDefault();

  const password = document.getElementById('regPassword').value;
  const confirmPassword = document.getElementById('regConfirmPassword').value;

  if (password !== confirmPassword) {
    Toast.error('Passwords do not match');
    return;
  }

  const data = {
    first_name: document.getElementById('regFirstName').value,
    last_name: document.getElementById('regLastName').value,
    email: document.getElementById('regEmail').value,
    password: password
  };

  try {
    const response = await API.auth.register(data);

    if (response.success) {
      Toast.success('Registration successful! Please login.');
      loadPage('login');
    } else {
      Toast.error(response.message || 'Registration failed');
    }
  } catch (error) {
    Toast.error('Registration failed. Please try again.');
  }
};

window.handleLogout = function () {
  console.log('Logout clicked');

  // Clear all auth data
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  localStorage.removeItem('active_company');
  localStorage.removeItem('currentPage');

  // Redirect directly to website landing page (not SPA)
  window.location.href = '/frontend/website/index.html';
};

// ============================================
// COMPANY MANAGEMENT
// ============================================
async function loadCurrentCompany() {
  const companyName = document.getElementById('active-company');
  if (!companyName) return;

  const activeCompany = Auth.getActiveCompany();
  if (activeCompany) {
    companyName.textContent = activeCompany.name;
  } else {
    // Fetch companies and select first one
    try {
      const response = await API.companies.list();
      if (response.success && response.data && response.data.length > 0) {
        const company = response.data[0];
        Auth.setActiveCompany({ id: company.id, name: company.name });
        companyName.textContent = company.name;
      }
    } catch (e) {
      console.error('Error loading company:', e);
    }
  }
}

function setupCompanyDropdown() {
  const dropdown = document.getElementById('company-dropdown');
  const companyList = document.getElementById('company-list');

  if (!dropdown || !companyList) return;

  dropdown.addEventListener('click', async () => {
    // Load companies
    try {
      const response = await API.companies.list();
      if (response.success && response.data) {
        companyList.innerHTML = response.data.map(c =>
          `<a href="#" class="dropdown-item" onclick="selectCompany(${c.id}, '${c.name}'); return false;">${c.name}</a>`
        ).join('');
      }
    } catch (e) {
      console.error('Error loading companies:', e);
    }
  });
}

window.selectCompany = function (id, name) {
  Auth.setActiveCompany({ id, name });
  document.getElementById('active-company').textContent = name;
  Toast.success(`Switched to ${name}`);

  // Reload current page
  loadPage(currentPage);
};

// ============================================
// HELPER FUNCTIONS
// ============================================
function updateActiveNavLink(pageName) {
  // Remove active from all
  document.querySelectorAll('.nav-link, .sidebar-link').forEach(link => {
    link.classList.remove('active');
  });

  // Add active to current
  document.querySelectorAll(`[data-section="${pageName}"]`).forEach(link => {
    link.classList.add('active');
  });
}

// ============================================
// PWA & MOBILE OPTIMIZATION
// ============================================
let deferredPrompt;

function initPWA() {
  const offlineBanner = document.getElementById('offline-banner');
  const installBanner = document.getElementById('install-banner');

  // 1. Connectivity Detection
  window.addEventListener('online', () => {
    if (offlineBanner) offlineBanner.classList.remove('show');
    Toast.info('Back online! 🟢');
  });

  window.addEventListener('offline', () => {
    if (offlineBanner) offlineBanner.classList.add('show');
    Toast.warning('Working offline... 🔴');
  });

  // Initial check
  if (!navigator.onLine && offlineBanner) offlineBanner.classList.add('show');

  // 2. Install Prompt logic
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBanner) installBanner.classList.add('show');
  });

  window.addEventListener('appinstalled', () => {
    if (installBanner) installBanner.classList.remove('show');
    deferredPrompt = null;
    Toast.success('App installed successfully! 🎉');
  });
}

window.installPWA = async function () {
  if (!deferredPrompt) return;

  const installBanner = document.getElementById('install-banner');
  if (installBanner) installBanner.classList.remove('show');

  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  console.log(`User response to install: ${outcome}`);
  deferredPrompt = null;
};

window.dismissInstallBanner = function () {
  const installBanner = document.getElementById('install-banner');
  if (installBanner) installBanner.classList.remove('show');
};

// Toggle sidebar (mobile)
window.toggleSidebar = function () {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');

  if (sidebar) sidebar.classList.toggle('open');
  if (overlay) overlay.classList.toggle('active');
};

// Close sidebar
window.closeSidebar = function () {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');

  if (sidebar) sidebar.classList.remove('open');
  if (overlay) overlay.classList.remove('active');
};

function initMobileUI() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');

  if (!sidebar) return;

  // Professional Swipe Support
  let touchStartX = 0;
  let touchEndX = 0;

  document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, false);

  document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  }, false);

  function handleSwipe() {
    const swipeDistance = touchEndX - touchStartX;
    const isMobile = window.innerWidth <= 768;

    if (!isMobile) return;

    // Swipe right from edge (open)
    if (swipeDistance > 80 && touchStartX < 40) {
      window.toggleSidebar();
    }
    // Swipe left anywhere on screen (close) if sidebar is open
    if (swipeDistance < -80 && sidebar.classList.contains('open')) {
      window.closeSidebar();
    }
  }

  // Ensure sidebar closes on navigation and overlay click
  if (overlay) {
    overlay.addEventListener('click', window.closeSidebar);
  }

  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768 && e.target.closest('.sidebar-link')) {
      window.closeSidebar();
    }
  });
}

// Auto-init on load
document.addEventListener('DOMContentLoaded', () => {
  initPWA();
  initMobileUI();
});

console.log('✅ Navigation.js loaded');
