/**
 * Accordion Component (No-Module)
 */
(function (global) {
    const Component = global.VanillaNext.Component;

    global.VanillaNext.Accordion = class Accordion extends Component {
        init() {
            this.items = this.element.querySelectorAll('.accordion-item');

            this.items.forEach(item => {
                const header = item.querySelector('.accordion-header');
                header.addEventListener('click', () => this.toggle(item));
            });
        }

        toggle(item) {
            const header = item.querySelector('.accordion-header');
            const body = item.querySelector('.accordion-body');
            const isOpen = header.classList.contains('active');

            // Auto-close others if needed (optional, keeping it simple for now)
            this.items.forEach(i => {
                const h = i.querySelector('.accordion-header');
                const b = i.querySelector('.accordion-body');
                if (h !== header && h.classList.contains('active')) {
                    h.classList.remove('active');
                    b.style.maxHeight = null;
                }
            });

            if (isOpen) {
                header.classList.remove('active');
                body.style.maxHeight = null;
            } else {
                header.classList.add('active');
                body.style.maxHeight = body.scrollHeight + "px";
            }
        }
    };

    global.VanillaNext.registry['accordion'] = global.VanillaNext.Accordion;

})(window);
