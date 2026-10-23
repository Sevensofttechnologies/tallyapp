/**
 * Theme Customizer (Live Settings)
 */
(function (global) {

    global.VanillaNext.ThemeCustomizer = class ThemeCustomizer {
        constructor() {
            this.init();
        }

        init() {
            // 1. Inject DOM
            const html = `
        <div class="vn-customizer-toggle"><span class="vn-spin">⚙️</span></div>
        <div class="vn-customizer-panel">
            <div class="vn-customizer-header">
                <h3 class="font-bold text-lg">Theme Settings</h3>
                <button class="btn btn-sm btn-ghost close-customizer">✕</button>
            </div>
            
            <div class="mb-6">
                <label class="text-xs font-bold text-muted uppercase mb-3 block">Primary Color</label>
                <div class="flex gap-2 flex-wrap" id="color-options">
                    <div class="color-swatch" style="background: #2563eb" data-color="#2563eb"></div>
                    <div class="color-swatch" style="background: #7c3aed" data-color="#7c3aed"></div>
                    <div class="color-swatch" style="background: #db2777" data-color="#db2777"></div>
                    <div class="color-swatch" style="background: #059669" data-color="#059669"></div>
                    <div class="color-swatch" style="background: #dc2626" data-color="#dc2626"></div>
                    <div class="color-swatch" style="background: #000000" data-color="#000000"></div>
                </div>
            </div>

            <div class="mb-6">
                 <label class="text-xs font-bold text-muted uppercase mb-3 block">Border Radius</label>
                 <div class="flex gap-2">
                    <button class="btn btn-sm btn-outline flex-1" data-radius="0px">Square</button>
                    <button class="btn btn-sm btn-outline flex-1" data-radius="6px">Default</button>
                    <button class="btn btn-sm btn-outline flex-1" data-radius="12px">Round</button>
                 </div>
            </div>

            <div class="mb-6">
                <label class="text-xs font-bold text-muted uppercase mb-3 block">Mode</label>
                <button class="btn btn-outline w-full" id="panel-theme-toggle">Toggle Dark/Light</button>
            </div>
            
            <div class="p-4 bg-gray-50 rounded text-xs text-center text-muted">
                Changes are saved to LocalStorage.
            </div>
        </div>
      `;

            const div = document.createElement('div');
            div.innerHTML = html;
            document.body.appendChild(div);

            // 2. Event Listeners
            const panel = document.querySelector('.vn-customizer-panel');
            const toggle = document.querySelector('.vn-customizer-toggle');

            toggle.addEventListener('click', () => panel.classList.toggle('open'));
            document.querySelector('.close-customizer').addEventListener('click', () => panel.classList.remove('open'));

            // Color Switcher
            document.querySelectorAll('.color-swatch').forEach(swatch => {
                swatch.addEventListener('click', () => {
                    const color = swatch.dataset.color;
                    document.documentElement.style.setProperty('--primary-600', color);
                    document.documentElement.style.setProperty('--primary-500', color); // Simplified for demo
                    // Ideally generates full palette
                });
            });

            // Radius Switcher
            document.querySelectorAll('[data-radius]').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.documentElement.style.setProperty('--radius', btn.dataset.radius);
                });
            });

            // Dark Mode
            document.getElementById('panel-theme-toggle').addEventListener('click', () => {
                global.VanillaNext.ThemeManager.toggle();
            });
        }
    };

    // Init
    document.addEventListener('DOMContentLoaded', () => {
        new global.VanillaNext.ThemeCustomizer();
    });

})(window);
