/**
 * Dropdown Component (No-Module Version)
 */
(function (global) {
    const Component = global.VanillaNext.Component;

    global.VanillaNext.Dropdown = class Dropdown extends Component {
        init() {
            this.menu = this.element.nextElementSibling;

            this.toggle = this.toggle.bind(this);
            this.close = this.close.bind(this);
            this.handleOutsideClick = this.handleOutsideClick.bind(this);

            this.element.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggle();
            });

            if (this.menu) {
                this.menu.querySelectorAll('.dropdown-item').forEach(item => {
                    item.addEventListener('click', this.close);
                });
            }
        }

        toggle() {
            const isShowing = this.menu.classList.contains('show');

            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });

            if (!isShowing) {
                this.open();
            }
        }

        open() {
            this.menu.classList.add('show');
            this.element.setAttribute('aria-expanded', 'true');
            document.addEventListener('click', this.handleOutsideClick);
        }

        close() {
            if (this.menu) {
                this.menu.classList.remove('show');
                this.element.setAttribute('aria-expanded', 'false');
                document.removeEventListener('click', this.handleOutsideClick);
            }
        }

        handleOutsideClick(e) {
            if (!this.element.contains(e.target) && !this.menu.contains(e.target)) {
                this.close();
            }
        }
    };

    // Register
    global.VanillaNext.registry['dropdown'] = global.VanillaNext.Dropdown;

})(window);
