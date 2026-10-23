/**
 * VanillaNext - Main Entry Point (No-Module Version)
 * Automatically initializes components.
 */
(function (global) {

    function initAll() {
        document.querySelectorAll('[data-component]').forEach(el => {
            const name = el.dataset.component;
            const ComponentClass = global.VanillaNext.registry[name];

            if (ComponentClass) {
                if (!el.__vn_component) {
                    el.__vn_component = new ComponentClass(el);
                    console.log(`[VanillaNext] Initialized ${name}`, el);
                }
            } else {
                console.warn(`[VanillaNext] Unknown component: ${name}`);
            }
        });
    }

    // Utilities
    function initUtilities() {
        // 1. Copy Code
        document.querySelectorAll('.doc-code').forEach(block => {
            block.style.cursor = 'pointer';
            block.setAttribute('title', 'Click to copy');
            block.addEventListener('click', () => {
                const code = block.innerText;
                navigator.clipboard.writeText(code).then(() => {
                    global.Toast.show('✓ Copied to clipboard!', 'success', 2000);
                });
            });
        });

        // 2. Scroll to Top
        const scrollBtn = document.createElement('button');
        scrollBtn.className = 'btn btn-primary btn-rounded';
        scrollBtn.innerHTML = '↑';
        scrollBtn.style.cssText = 'position: fixed; bottom: 30px; right: 30px; display: none; z-index: 2000; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
        document.body.appendChild(scrollBtn);

        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) scrollBtn.style.display = 'block';
            else scrollBtn.style.display = 'none';
        });

        scrollBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Auto-init
    document.addEventListener('DOMContentLoaded', () => {
        // 1. Init Theme
        if (global.VanillaNext.ThemeManager) {
            global.VanillaNext.ThemeManager.init();
        }

        // 2. Init Components
        initAll();

        // 3. Init Utils
        initUtilities();

        // 4. Console Stats
        console.log(`🎨 Advanced UI Kit v1.0\n📊 Components Loaded: ${Object.keys(global.VanillaNext.registry).length}`);
    });

    // Expose API
    global.VanillaNext.initAll = initAll;

})(window);
