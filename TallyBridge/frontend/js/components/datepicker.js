/**
 * Simple DatePicker (No-Module)
 */
(function (global) {

    global.VanillaNext.DatePicker = class DatePicker {
        constructor(inputElement) {
            this.input = inputElement;
            this.init();
        }

        init() {
            // 1. Create Picker DOM
            this.picker = document.createElement('div');
            this.picker.className = 'vn-datepicker';
            this.picker.style.display = 'none';
            this.renderCalendar(new Date());

            document.body.appendChild(this.picker);

            // 2. Event Listeners
            this.input.addEventListener('focus', () => this.show());

            // Close on click outside
            document.addEventListener('mousedown', (e) => {
                if (!this.picker.contains(e.target) && e.target !== this.input) {
                    this.hide();
                }
            });

            // Prevent picker click from closing
            this.picker.addEventListener('mousedown', (e) => e.preventDefault());
        }

        show() {
            const rect = this.input.getBoundingClientRect();
            this.picker.style.top = (rect.bottom + window.scrollY + 5) + 'px';
            this.picker.style.left = (rect.left + window.scrollX) + 'px';
            this.picker.style.display = 'block';
        }

        hide() {
            this.picker.style.display = 'none';
        }

        renderCalendar(date) {
            const year = date.getFullYear();
            const month = date.getMonth();
            const firstDay = new Date(year, month, 1).getDay();
            const daysInMonth = new Date(year, month + 1, 0).getDate();

            const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

            let html = `
        <div class="vn-datepicker-header">
            <button class="vn-btn-prev">&lt;</button>
            <span>${months[month]} ${year}</span>
            <button class="vn-btn-next">&gt;</button>
        </div>
        <div class="vn-datepicker-grid">
            <div class="day-name">Su</div><div class="day-name">Mo</div><div class="day-name">Tu</div><div class="day-name">We</div><div class="day-name">Th</div><div class="day-name">Fr</div><div class="day-name">Sa</div>
      `;

            // Empty slots
            for (let i = 0; i < firstDay; i++) {
                html += `<div></div>`;
            }

            // Days
            for (let i = 1; i <= daysInMonth; i++) {
                html += `<div class="vn-day" data-day="${i}">${i}</div>`;
            }

            html += `</div>`;
            this.picker.innerHTML = html;

            // Click handlers
            this.picker.querySelectorAll('.vn-day').forEach(d => {
                d.addEventListener('click', () => {
                    const day = d.dataset.day;
                    this.input.value = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                    this.hide();
                });
            });

            this.picker.querySelector('.vn-btn-prev').addEventListener('click', () => {
                this.renderCalendar(new Date(year, month - 1, 1));
            });
            this.picker.querySelector('.vn-btn-next').addEventListener('click', () => {
                this.renderCalendar(new Date(year, month + 1, 1));
            });
        }
    };

    // Init
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('[data-toggle="datepicker"]').forEach(el => new global.VanillaNext.DatePicker(el));
    });

})(window);
