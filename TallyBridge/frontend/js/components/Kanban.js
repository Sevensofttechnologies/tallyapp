/**
 * Kanban Drag & Drop Logic (Pure Vanilla JS)
 */
(function (global) {

    global.VanillaNext.Kanban = class Kanban {
        constructor() {
            this.draggables = document.querySelectorAll('.kanban-card');
            this.containers = document.querySelectorAll('.kanban-items');

            this.init();
        }

        init() {
            this.draggables.forEach(draggable => {
                draggable.addEventListener('dragstart', () => {
                    draggable.classList.add('dragging');
                });

                draggable.addEventListener('dragend', () => {
                    draggable.classList.remove('dragging');
                });
            });

            this.containers.forEach(container => {
                container.addEventListener('dragover', e => {
                    e.preventDefault(); // Enable dropping
                    const afterElement = this.getDragAfterElement(container, e.clientY);
                    const draggable = document.querySelector('.dragging');

                    if (afterElement == null) {
                        container.appendChild(draggable);
                    } else {
                        container.insertBefore(draggable, afterElement);
                    }
                });
            });
        }

        getDragAfterElement(container, y) {
            const draggableElements = [...container.querySelectorAll('.kanban-card:not(.dragging)')];

            return draggableElements.reduce((closest, child) => {
                const box = child.getBoundingClientRect();
                const offset = y - box.top - box.height / 2;

                if (offset < 0 && offset > closest.offset) {
                    return { offset: offset, element: child };
                } else {
                    return closest;
                }
            }, { offset: Number.NEGATIVE_INFINITY }).element;
        }
    };

    // Init
    document.addEventListener('DOMContentLoaded', () => {
        // Only init if board exists
        if (document.querySelector('.kanban-board')) {
            new global.VanillaNext.Kanban();
        }
    });

})(window);
