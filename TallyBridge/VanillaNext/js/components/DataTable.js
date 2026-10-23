/**
 * DataTable Component (Sort, Search, Page)
 * Pure Vanilla JS
 */
(function (global) {

    global.VanillaNext.DataTable = class DataTable {
        constructor(tableElement, options = {}) {
            this.table = tableElement;
            this.tbody = this.table.querySelector('tbody');
            this.rows = Array.from(this.tbody.querySelectorAll('tr'));
            this.pageSize = options.pageSize || 5;
            this.currentPage = 1;
            this.currentSort = { col: null, dir: 'asc' };

            this.init();
        }

        init() {
            // 1. Wrap structure
            this.wrapper = document.createElement('div');
            this.wrapper.className = 'datatable-wrapper';
            this.table.parentNode.insertBefore(this.wrapper, this.table);

            // 2. Create Header (Search)
            const header = document.createElement('div');
            header.className = 'datatable-header';
            header.innerHTML = `
        <div class="font-bold">Data Grid</div>
        <div class="datatable-search">
            <input type="text" class="form-input" placeholder="Search rows...">
        </div>
      `;
            this.wrapper.appendChild(header);

            // Move table inside
            const tableDiv = document.createElement('div');
            tableDiv.style.overflowX = 'auto'; // Responsive
            tableDiv.appendChild(this.table);
            this.wrapper.appendChild(tableDiv);
            this.table.classList.add('datatable');

            // 3. Create Footer (Pagination)
            this.footer = document.createElement('div');
            this.footer.className = 'datatable-footer';
            this.wrapper.appendChild(this.footer);

            // Events
            this.setupSorting();
            this.setupSearch(header.querySelector('input'));

            this.render();
        }

        setupSorting() {
            this.table.querySelectorAll('thead th').forEach((th, index) => {
                th.addEventListener('click', () => {
                    const dir = this.currentSort.col === index && this.currentSort.dir === 'asc' ? 'desc' : 'asc';

                    // Clear icons
                    this.table.querySelectorAll('th').forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
                    th.classList.add(`sort-${dir}`);

                    this.currentSort = { col: index, dir };
                    this.sortErrors(index, dir);
                });
            });
        }

        sortErrors(index, dir) {
            this.rows.sort((a, b) => {
                const valA = a.children[index].textContent.trim().toLowerCase();
                const valB = b.children[index].textContent.trim().toLowerCase();

                if (dir === 'asc') return valA.localeCompare(valB, undefined, { numeric: true });
                return valB.localeCompare(valA, undefined, { numeric: true });
            });
            this.render();
        }

        setupSearch(input) {
            input.addEventListener('input', (e) => {
                const term = e.target.value.toLowerCase();
                this.rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.dataset.visible = text.includes(term) ? 'true' : 'false';
                });
                this.currentPage = 1;
                this.render();
            });
        }

        render() {
            // Filter visible
            const visibleRows = this.rows.filter(r => r.dataset.visible !== 'false');
            const totalPages = Math.ceil(visibleRows.length / this.pageSize);

            // Paginate
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;

            // Clear tbody
            this.tbody.innerHTML = '';
            visibleRows.slice(start, end).forEach(row => this.tbody.appendChild(row));

            // Update Footer
            this.renderPagination(visibleRows.length, totalPages);
        }

        renderPagination(totalItems, totalPages) {
            this.footer.innerHTML = `
        <div>Showing ${(this.currentPage - 1) * this.pageSize + 1} to ${Math.min(this.currentPage * this.pageSize, totalItems)} of ${totalItems} entries</div>
        <div class="datatable-pagination">
             ${this.createPageButtons(totalPages)}
        </div>
      `;

            this.footer.querySelectorAll('.page-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const page = parseInt(btn.dataset.page);
                    if (page > 0 && page <= totalPages) {
                        this.currentPage = page;
                        this.render();
                    }
                });
            });
        }

        createPageButtons(totalPages) {
            let btns = '';
            if (totalPages <= 1) return '';

            btns += `<button class="page-btn" data-page="${this.currentPage - 1}" ${this.currentPage === 1 ? 'disabled' : ''}>&lt;</button>`;

            for (let i = 1; i <= totalPages; i++) {
                btns += `<button class="page-btn ${i === this.currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
            }

            btns += `<button class="page-btn" data-page="${this.currentPage + 1}" ${this.currentPage === totalPages ? 'disabled' : ''}>&gt;</button>`;
            return btns;
        }
    };

    // Auto Init
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('[data-component="datatable"]').forEach(el => new global.VanillaNext.DataTable(el));
    });

})(window);
