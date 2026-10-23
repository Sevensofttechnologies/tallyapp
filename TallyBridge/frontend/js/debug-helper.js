/**
 * VanillaNext Debug Helper
 * Intercepts console errors and displays them in a visual overlay for easy debugging.
 */

(function () {
    console.log('🧪 Debug Helper Initialized. Monitoring console for errors...');

    const errorLogs = [];
    const overlayId = 'debug-error-overlay';

    // Create UI overlay
    const createOverlay = () => {
        if (document.getElementById(overlayId)) return;

        const overlay = document.createElement('div');
        overlay.id = overlayId;
        overlay.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            right: 20px;
            max-height: 200px;
            background: rgba(220, 38, 38, 0.95);
            color: white;
            padding: 15px;
            border-radius: 8px;
            z-index: 999999;
            font-family: monospace;
            font-size: 12px;
            overflow-y: auto;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            display: none;
            border: 2px solid #fecaca;
        `;

        const header = document.createElement('div');
        header.style.cssText = 'display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 5px; margin-bottom: 10px; font-weight: bold;';
        header.innerHTML = '<span>🚨 CONSOLE ERRORS DETECTED</span> <button onclick="this.parentElement.parentElement.style.display=\'none\'" style="background:none; border:none; color:white; cursor:pointer;">✕</button>';

        const list = document.createElement('div');
        list.id = 'debug-error-list';

        overlay.appendChild(header);
        overlay.appendChild(list);
        document.body.appendChild(overlay);
    };

    const logError = (msg) => {
        createOverlay();
        const overlay = document.getElementById(overlayId);
        const list = document.getElementById('debug-error-list');

        overlay.style.display = 'block';

        const item = document.createElement('div');
        item.style.marginBottom = '5px';
        item.innerHTML = `<strong>[Error]</strong> ${msg}`;
        list.appendChild(item);

        // Keep only last 10 errors
        while (list.children.length > 10) {
            list.removeChild(list.firstChild);
        }
    };

    // Intercept Window Errors (Syntax, Runtime)
    window.onerror = function (message, source, lineno, colno, error) {
        logError(`${message} at ${source}:${lineno}`);
    };

    // Intercept Unhandled Rejections (Promises/Async)
    window.addEventListener('unhandledrejection', function (event) {
        logError(`Async Error: ${event.reason}`);
    });

    // Intercept Console.error
    const originalConsoleError = console.error;
    console.error = function () {
        originalConsoleError.apply(console, arguments);
        const args = Array.from(arguments).map(arg =>
            typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
        );
        logError(args.join(' '));
    };

    // Test Resource Load Failures
    window.addEventListener('error', function (e) {
        if (e.target.tagName === 'SCRIPT' || e.target.tagName === 'LINK') {
            logError(`Failed to load resource: ${e.target.src || e.target.href}`);
        }
    }, true);

})();
