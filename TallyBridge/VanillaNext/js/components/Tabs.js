/**
 * Tabs Component (No-Module)
 */
(function (global) {
    const Component = global.VanillaNext.Component;

    global.VanillaNext.Tabs = class Tabs extends Component {
        init() {
            this.triggers = this.element.querySelectorAll('.tab-link');
            this.contents = document.querySelectorAll(this.element.dataset.target);

            this.triggers.forEach(trigger => {
                trigger.addEventListener('click', (e) => {
                    this.activate(e.target);
                });
            });
        }

        activate(targetTab) {
            // Remove active from all triggers
            this.triggers.forEach(t => t.classList.remove('active'));
            // Add active to clicked
            targetTab.classList.add('active');

            // Hide all contents
            this.contents.forEach(c => c.classList.remove('active'));

            // Show target content
            const targetId = targetTab.dataset.content;
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        }
    };

    global.VanillaNext.registry['tabs'] = global.VanillaNext.Tabs;

})(window);
