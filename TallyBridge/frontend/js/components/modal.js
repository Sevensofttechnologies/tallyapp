/**
 * Modal Component (No-Module Version)
 */
(function (global) {
    const Component = global.VanillaNext.Component;

    global.VanillaNext.Modal = class Modal extends Component {
        get defaults() {
            return {
                keyboard: true,
                backdrop: true
            };
        }

        init() {
            this.id = this.element.id;
            this.backdrop = document.querySelector('.modal-backdrop') || this._createBackdrop();

            this.close = this.close.bind(this);
            this.handleKeydown = this.handleKeydown.bind(this);
            this.handleBackdropClick = this.handleBackdropClick.bind(this);

            this.element.querySelectorAll('[data-dismiss="modal"]').forEach(btn => {
                btn.addEventListener('click', this.close);
            });

            document.querySelectorAll(`[data-toggle="modal"][data-target="#${this.id}"]`).forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.open();
                });
            });
        }

        _createBackdrop() {
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop';
            document.body.appendChild(backdrop);
            return backdrop;
        }

        open() {
            this.backdrop.classList.add('show');
            this.element.classList.add('show');
            document.body.style.overflow = 'hidden';

            if (this.options.keyboard) {
                document.addEventListener('keydown', this.handleKeydown);
            }

            if (this.options.backdrop) {
                this.backdrop.addEventListener('click', this.handleBackdropClick);
            }

            this.emit('modal.open');
        }

        close() {
            this.backdrop.classList.remove('show');
            this.element.classList.remove('show');
            document.body.style.overflow = '';

            document.removeEventListener('keydown', this.handleKeydown);
            this.backdrop.removeEventListener('click', this.handleBackdropClick);

            this.emit('modal.close');
        }

        handleKeydown(e) {
            if (e.key === 'Escape') this.close();
        }

        handleBackdropClick(e) {
            if (e.target === this.backdrop) this.close();
        }
        static open(id) {
            const el = typeof id === 'string' ? document.getElementById(id) : id;
            if (!el) return;
            if (!el._modal) {
                el._modal = new Modal(el);
            }
            el._modal.open();
        }

        static close(id) {
            const el = typeof id === 'string' ? document.getElementById(id) : id;
            if (!el) return;
            if (el._modal) {
                el._modal.close();
            } else {
                el.classList.remove('show');
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) backdrop.classList.remove('show');
                document.body.style.overflow = '';
            }
        }

        static confirm(options) {
            const { title, message, confirmText, confirmClass, onConfirm } = options;
            let modalEl = document.getElementById('modal-confirm-global');

            if (!modalEl) {
                modalEl = document.createElement('div');
                modalEl.id = 'modal-confirm-global';
                modalEl.className = 'modal';
                modalEl.innerHTML = `
                    <div class="modal-header">
                        <h2 class="modal-title" id="modal-confirm-title"></h2>
                        <button class="modal-close" data-dismiss="modal">&times;</button>
                    </div>
                    <div class="modal-body" id="modal-confirm-body"></div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                        <button class="btn" id="modal-confirm-btn"></button>
                    </div>
                `;
                document.body.appendChild(modalEl);
            }

            modalEl.querySelector('#modal-confirm-title').textContent = title || 'Confirm';
            modalEl.querySelector('#modal-confirm-body').textContent = message || 'Are you sure?';

            const confirmBtn = modalEl.querySelector('#modal-confirm-btn');
            confirmBtn.textContent = confirmText || 'Confirm';
            confirmBtn.className = `btn ${confirmClass || 'btn-primary'}`;

            // New click handler
            const newHandler = async () => {
                confirmBtn.removeEventListener('click', newHandler);
                if (onConfirm) await onConfirm();
                this.close('modal-confirm-global');
            };

            // Remove old potential listeners (simplest way is cloning if needed, but here we just replace)
            const oldHandler = confirmBtn._handler;
            if (oldHandler) confirmBtn.removeEventListener('click', oldHandler);
            confirmBtn.addEventListener('click', newHandler);
            confirmBtn._handler = newHandler;

            this.open('modal-confirm-global');
        }
    };

    // Register
    global.VanillaNext.registry['modal'] = global.VanillaNext.Modal;

    // Expose Global Alias
    global.Modal = global.VanillaNext.Modal;

})(window);
