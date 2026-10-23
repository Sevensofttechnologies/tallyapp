/**
 * Command Palette Component (No-Module)
 */
(function (global) {

    global.VanillaNext.CommandPalette = class CommandPalette {
        constructor(element) {
            this.element = element;
            this.input = element.querySelector('.cmd-input');
            this.items = element.querySelectorAll('.cmd-item');
            this.closeBtn = element.querySelector('.cmd-close'); // optional

            this.isOpen = false;
            this.selectedIndex = 0;

            this.init();
        }

        init() {
            // Global Shortcut (Ctrl+K)
            document.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    this.toggle();
                }
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });

            // Close on backdrop click
            this.element.addEventListener('click', (e) => {
                if (e.target === this.element) this.close();
            });

            // Input handling (Filtering)
            this.input.addEventListener('input', (e) => this.filter(e.target.value));

            // Navigation
            this.input.addEventListener('keydown', (e) => this.navigate(e));

            // Items click
            this.items.forEach(item => {
                item.addEventListener('click', () => {
                    this.selectAction(item);
                });
            });
        }

        toggle() {
            if (this.isOpen) this.close();
            else this.open();
        }

        open() {
            this.element.classList.add('show');
            this.isOpen = true;
            setTimeout(() => this.input.focus(), 50);
        }

        close() {
            this.element.classList.remove('show');
            this.isOpen = false;
        }

        filter(query) {
            const lowerQuery = query.toLowerCase();
            this.items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(lowerQuery)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        navigate(e) {
            // Simple Up/Down navigation logic can be added here
            // For now, Enter triggers first visible
            if (e.key === 'Enter') {
                const visible = Array.from(this.items).find(i => i.style.display !== 'none');
                if (visible) this.selectAction(visible);
            }
        }

        selectAction(item) {
            const action = item.dataset.action;
            console.log('Command Triggered:', action);

            // Example actions
            if (action === 'theme-toggle') global.VanillaNext.ThemeManager.toggle();
            if (action === 'go-home') window.location.href = '#';
            if (action === 'copy-url') {
                navigator.clipboard.writeText(window.location.href);
                global.Toast.show('URL Copied', 'success');
            }

            this.close();
        }
    };

    // Init globally if found
    document.addEventListener('DOMContentLoaded', () => {
        const cmdEl = document.querySelector('.cmd-backdrop');
        if (cmdEl) {
            global.VanillaNext.cmd = new global.VanillaNext.CommandPalette(cmdEl);
        }
    });

})(window);
