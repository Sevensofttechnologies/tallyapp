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
    };

    // Register
    global.VanillaNext.registry['modal'] = global.VanillaNext.Modal;

})(window);
