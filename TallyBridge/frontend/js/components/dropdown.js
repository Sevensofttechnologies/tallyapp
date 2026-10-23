/**
 * Dropdown Component (No-Module Version)
 * Uses Event Delegation to support dynamic elements (like DataTable)
 */
(function (global) {
    const Dropdown = {
        toggle(toggleBtn) {
            const dropdown = toggleBtn.closest('.dropdown');
            const menu = toggleBtn.nextElementSibling || dropdown.querySelector('.dropdown-menu');

            if (!menu) return;

            const isShowing = menu.classList.contains('show');

            // Close all other dropdowns
            this.closeAll();

            if (!isShowing) {
                this.open(dropdown, menu, toggleBtn);
            }
        },

        open(wrapper, menu, toggleBtn) {
            menu.classList.add('show');
            wrapper.classList.add('active');
            toggleBtn.setAttribute('aria-expanded', 'true');
        },

        closeAll() {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
            document.querySelectorAll('.dropdown.active').forEach(wrapper => {
                wrapper.classList.remove('active');
            });
            document.querySelectorAll('[data-toggle="dropdown"][aria-expanded="true"]').forEach(btn => {
                btn.setAttribute('aria-expanded', 'false');
            });
        },

        init() {
            // Global Event Delegation
            document.addEventListener('click', (e) => {
                const toggleBtn = e.target.closest('[data-toggle="dropdown"]');

                if (toggleBtn) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.toggle(toggleBtn);
                } else if (!e.target.closest('.dropdown-menu')) {
                    // Click outside
                    this.closeAll();
                }
            });
        }
    };

    // Initialize globally
    Dropdown.init();

    // Register
    global.VanillaNext = global.VanillaNext || {};
    global.VanillaNext.Dropdown = Dropdown;
    global.VanillaNext.registry = global.VanillaNext.registry || {};
    global.VanillaNext.registry['dropdown'] = Dropdown;

})(window);
