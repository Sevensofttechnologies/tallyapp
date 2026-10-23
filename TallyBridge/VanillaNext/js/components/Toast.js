/**
 * Toast Component (No-Module Version)
 */
(function (global) {

    global.VanillaNext.Toast = class Toast {
        static container = null;

        static init() {
            if (!this.container) {
                this.container = document.createElement('div');
                this.container.className = 'toast-container';
                document.body.appendChild(this.container);
            }
        }

        static show(message, type = 'info', duration = 3000) {
            this.init();

            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.innerHTML = `
        <div class="toast-message">${message}</div>
        <button class="toast-close">&times;</button>
      `;

            toast.querySelector('.toast-close').addEventListener('click', () => {
                this.dismiss(toast);
            });

            this.container.appendChild(toast);

            if (duration > 0) {
                setTimeout(() => {
                    this.dismiss(toast);
                }, duration);
            }
        }

        static dismiss(toast) {
            toast.classList.add('hiding');
            toast.addEventListener('transitionend', () => {
                toast.remove();
            });
        }
    };

    // Expose handy alias
    global.Toast = global.VanillaNext.Toast;

})(window);
