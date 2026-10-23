/**
 * Notification Center (Bell Dropdown)
 */
(function (global) {

    global.VanillaNext.NotificationCenter = class NotificationCenter {
        constructor() {
            this.init();
        }

        init() {
            // 1. Find bell button
            const btn = document.querySelector('[data-toggle="notifications"]');
            if (!btn) return;

            // 2. Create Dropdown
            const dropdown = document.createElement('div');
            dropdown.className = 'vn-notification-dropdown card';
            dropdown.innerHTML = `
        <div class="p-3 border-b border-gray-200 flex justify-between items-center">
            <span class="font-bold text-sm">Notifications</span>
            <button class="text-xs text-primary-600 hover:underline">Mark all read</button>
        </div>
        <div class="vn-notification-list">
             <div class="vn-notification-item unread">
                <div class="vn-notif-icon bg-success-100 text-success-600">✓</div>
                <div class="vn-notif-content">
                    <div class="vn-notif-title">Project deployed</div>
                    <div class="vn-notif-time">Just now</div>
                </div>
             </div>
             <div class="vn-notification-item unread">
                <div class="vn-notif-icon bg-primary-100 text-primary-600">💬</div>
                <div class="vn-notif-content">
                    <div class="vn-notif-title">New message from Sarah</div>
                    <div class="vn-notif-time">2 m ago</div>
                </div>
             </div>
             <div class="vn-notification-item">
                <div class="vn-notif-icon bg-warning-100 text-warning-600">⚠️</div>
                <div class="vn-notif-content">
                    <div class="vn-notif-title">Storage reporting 90%</div>
                    <div class="vn-notif-time">5 h ago</div>
                </div>
             </div>
        </div>
        <div class="p-2 border-t border-gray-200 text-center">
            <a href="#" class="text-xs font-bold text-gray-500 hover:text-gray-900">View All</a>
        </div>
      `;
            document.body.appendChild(dropdown);

            // Styles
            const style = document.createElement('style');
            style.innerHTML = `
        .vn-notification-dropdown {
            position: absolute;
            width: 300px;
            top: 70px;
            right: 20px;
            z-index: 1000;
            display: none;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        }
        .vn-notification-dropdown.show { display: block; animation: slideDown 0.2s; }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        
        .vn-notification-list { max-height: 300px; overflow-y: auto; }
        
        .vn-notification-item {
            padding: 12px;
            display: flex;
            gap: 12px;
            border-bottom: 1px solid var(--gray-100);
            cursor: pointer;
            transition: background 0.2s;
        }
        .vn-notification-item:hover { background: var(--gray-50); }
        .vn-notification-item.unread { background: var(--primary-50); }
        
        .vn-notif-icon {
            width: 32px; height: 32px;
            min-width: 32px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.875rem;
        }
        .vn-notif-title { font-size: 0.875rem; font-weight: 500; color: var(--gray-800); margin-bottom: 2px; }
        .vn-notif-time { font-size: 0.75rem; color: var(--gray-500); }
      `;
            document.head.appendChild(style);

            // Logic
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const rect = btn.getBoundingClientRect();
                dropdown.style.right = (window.innerWidth - rect.right) + 'px';
                dropdown.classList.toggle('show');
            });

            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target) && !btn.contains(e.target)) {
                    dropdown.classList.remove('show');
                }
            });
        }
    };

    // Init
    document.addEventListener('DOMContentLoaded', () => {
        new global.VanillaNext.NotificationCenter();
    });

})(window);
