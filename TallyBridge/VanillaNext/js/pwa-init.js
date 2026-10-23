/**
 * PWA & Mobile UI Initialization
 * Common script for all admin pages
 */

// PWA: Deferred install prompt
let deferredPrompt;

// Initialize PWA features
function initPWA() {
  // Offline/Online detection
  const offlineBanner = document.getElementById('offline-banner');
  
  function updateOnlineStatus() {
    if (offlineBanner) {
      offlineBanner.classList.toggle('show', !navigator.onLine);
    }
  }
  
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  updateOnlineStatus();
  
  // Install prompt
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    const installBanner = document.getElementById('install-banner');
    if (installBanner) {
      installBanner.classList.add('show');
    }
  });
}

// Install PWA
window.installPWA = async function() {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  console.log('Install outcome:', outcome);
  deferredPrompt = null;
  const installBanner = document.getElementById('install-banner');
  if (installBanner) {
    installBanner.classList.remove('show');
  }
};

// Dismiss install banner
window.dismissInstallBanner = function() {
  const installBanner = document.getElementById('install-banner');
  if (installBanner) {
    installBanner.classList.remove('show');
  }
};

// Mobile UI: Sidebar toggle
window.toggleSidebar = function() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.querySelector('.sidebar-overlay');
  if (sidebar) {
    sidebar.classList.toggle('open');
  }
  if (overlay) {
    overlay.classList.toggle('active');
  }
};

window.closeSidebar = function() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.querySelector('.sidebar-overlay');
  if (sidebar) {
    sidebar.classList.remove('open');
  }
  if (overlay) {
    overlay.classList.remove('active');
  }
};

// Mobile UI: Swipe support
function initMobileUI() {
  let touchStartX = 0;
  let touchEndX = 0;
  const swipeThreshold = 50;
  
  document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });
  
  document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  }, { passive: true });
  
  function handleSwipe() {
    const diff = touchEndX - touchStartX;
    const sidebar = document.getElementById('sidebar');
    
    // Swipe right to open (from left edge)
    if (diff > swipeThreshold && touchStartX < 50) {
      if (sidebar) sidebar.classList.add('open');
      const overlay = document.querySelector('.sidebar-overlay');
      if (overlay) overlay.classList.add('active');
    }
    
    // Swipe left to close
    if (diff < -swipeThreshold && sidebar?.classList.contains('open')) {
      sidebar.classList.remove('open');
      const overlay = document.querySelector('.sidebar-overlay');
      if (overlay) overlay.classList.remove('active');
    }
  }
  
  // Close sidebar on navigation click
  document.querySelectorAll('.sidebar-link').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth < 1024) {
        closeSidebar();
      }
    });
  });
}

// Service Worker Registration
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js')
      .then(reg => console.log('✅ Service Worker registered'))
      .catch(err => console.warn('❌ Service Worker failed', err));
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  initPWA();
  initMobileUI();
  registerServiceWorker();
});
