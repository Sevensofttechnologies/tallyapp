/**
 * Simple Lightbox (No-Module)
 */
(function (global) {

    global.VanillaNext.Lightbox = class Lightbox {
        constructor() {
            this.init();
        }

        init() {
            // Create Modal DOM
            this.modal = document.createElement('div');
            this.modal.className = 'lightbox-overlay';
            this.modal.innerHTML = `
        <div class="lightbox-content">
            <img src="" class="lightbox-img">
            <button class="lightbox-close">&times;</button>
        </div>
      `;
            document.body.appendChild(this.modal);

            this.img = this.modal.querySelector('.lightbox-img');
            this.closeBtn = this.modal.querySelector('.lightbox-close');

            // Bind events
            this.closeBtn.addEventListener('click', () => this.close());
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) this.close();
            });

            // Attach to all data-toggle="lightbox"
            document.querySelectorAll('[data-toggle="lightbox"]').forEach(el => {
                el.addEventListener('click', (e) => {
                    e.preventDefault();
                    const src = el.dataset.src || el.getAttribute('src');
                    this.open(src);
                });
            });
        }

        open(src) {
            this.img.src = src;
            this.modal.classList.add('show');
        }

        close() {
            this.modal.classList.remove('show');
        }
    };

    // Init
    document.addEventListener('DOMContentLoaded', () => {
        new global.VanillaNext.Lightbox();
    });

})(window);
