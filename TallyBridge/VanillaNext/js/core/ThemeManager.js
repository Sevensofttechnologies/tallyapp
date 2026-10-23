/**
 * Theme Manager (No-Module Version)
 */
(function (global) {

    global.VanillaNext.ThemeManager = class ThemeManager {
        static init() {
            this.storageKey = 'vn-theme';
            this.toggles = document.querySelectorAll('[data-toggle="theme"]');

            const storedTheme = localStorage.getItem(this.storageKey);
            const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

            if (storedTheme === 'dark' || (!storedTheme && systemDark)) {
                this.setTheme('dark');
            } else {
                this.setTheme('light');
            }

            this.toggles.forEach(btn => {
                btn.addEventListener('click', () => this.toggle());
            });
        }

        static toggle() {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            this.setTheme(next);
        }

        static setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem(this.storageKey, theme);

            this.toggles.forEach(btn => {
                const modeText = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
                if (btn.tagName === 'BUTTON' || btn.tagName === 'A') {
                    const span = btn.querySelector('.theme-text');
                    if (span) span.textContent = modeText;
                }
            });
        }
    };

})(window);
