/**
 * Advanced DataTable Component
 * Supports: Search, Pagination, Sorting, Custom Renders
 * Pure Vanilla JS
 */
(function (global) {
    global.VanillaNext = global.VanillaNext || {};

    global.VanillaNext.DataTable = class DataTable {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            if (!this.container) throw new Error(`DataTable: Container ${container} not found`);

            this.options = {
                columns: options.columns || [],
                pageSize: options.perPage || 10,
                searchable: options.searchable !== false,
                emptyMessage: options.emptyMessage || 'No data found',
                classList: options.classList || {
                    table: 'table w-full',
                    thead: 'bg-surface border-b',
                    tbody: 'text-sm'
                }
            };

            this.data = options.data || [];
            this.filteredData = [...this.data];
            this.currentPage = 1;
            this.currentSort = { key: null, dir: 'asc' };
            this.searchTerm = '';
            this.isLoading = false;

            this.init();
        }

        init() {
            this.container.innerHTML = `
                <div class="datatable-wrapper">
                    ${this.options.searchable ? `
                        <div class="datatable-header flex justify-between items-center mb-4">
                            <div class="datatable-title font-bold text-lg"></div>
                            <div class="datatable-search w-64">
                                <input type="text" class="form-input" placeholder="Search...">
                            </div>
                        </div>
                    ` : ''}
                    <div class="datatable-container relative min-h-[200px]">
                        <table class="${this.options.classList.table}">
                            <thead class="${this.options.classList.thead}">
                                <tr id="datatable-head"></tr>
                            </thead>
                            <tbody class="${this.options.classList.tbody}" id="datatable-body">
                            </tbody>
                        </table>
                        <div id="datatable-loader" class="absolute inset-0 bg-white/50 backdrop-blur-[1px] flex items-center justify-center hidden">
                            <div class="spinner"></div>
                        </div>
                    </div>
                    <div class="datatable-footer flex justify-between items-center mt-4 text-sm text-muted" id="datatable-footer">
                    </div>
                </div>
            `;

            this.thead = this.container.querySelector('#datatable-head');
            this.tbody = this.container.querySelector('#datatable-body');
            this.loader = this.container.querySelector('#datatable-loader');
            this.footer = this.container.querySelector('#datatable-footer');

            if (this.options.searchable) {
                this.container.querySelector('.datatable-search input').addEventListener('input', (e) => {
                    this.search(e.target.value);
                });
            }

            this.renderHead();
            this.render();
        }

        renderHead() {
            this.thead.innerHTML = this.options.columns.map((col, index) => `
                <th class="px-4 py-3 text-left font-semibold cursor-pointer select-none hover:bg-gray-50 transition" data-key="${col.key}">
                    <div class="flex items-center gap-2">
                        ${col.label}
                        <span class="sort-icon text-gray-300 text-[10px]">↕</span>
                    </div>
                </th>
            `).join('');

            this.thead.querySelectorAll('th').forEach(th => {
                th.addEventListener('click', () => {
                    this.sort(th.dataset.key);
                });
            });
        }

        setData(data) {
            this.data = data || [];
            this.applyFilters();
            this.setLoading(false);
        }

        setLoading(loading) {
            this.isLoading = loading;
            if (this.loader) {
                this.loader.classList.toggle('hidden', !loading);
            }
        }

        search(term) {
            this.searchTerm = term.toLowerCase();
            this.currentPage = 1;
            this.applyFilters();
        }

        sort(key) {
            const dir = this.currentSort.key === key && this.currentSort.dir === 'asc' ? 'desc' : 'asc';
            this.currentSort = { key, dir };

            // Update UI
            this.thead.querySelectorAll('th').forEach(th => {
                const icon = th.querySelector('.sort-icon');
                if (th.dataset.key === key) {
                    icon.textContent = dir === 'asc' ? '↑' : '↓';
                    icon.classList.add('text-primary-600');
                } else {
                    icon.textContent = '↕';
                    icon.classList.remove('text-primary-600');
                }
            });

            this.applyFilters();
        }

        applyFilters() {
            // Search
            this.filteredData = this.data.filter(item => {
                return Object.values(item).some(val =>
                    String(val).toLowerCase().includes(this.searchTerm)
                );
            });

            // Sort
            if (this.currentSort.key) {
                const { key, dir } = this.currentSort;
                this.filteredData.sort((a, b) => {
                    const valA = a[key] || '';
                    const valB = b[key] || '';
                    const res = String(valA).localeCompare(String(valB), undefined, { numeric: true });
                    return dir === 'asc' ? res : -res;
                });
            }

            this.render();
        }

        render() {
            const totalItems = this.filteredData.length;
            const totalPages = Math.ceil(totalItems / this.options.pageSize);
            const start = (this.currentPage - 1) * this.options.pageSize;
            const end = Math.min(start + this.options.pageSize, totalItems);
            const paginatedData = this.filteredData.slice(start, end);

            if (totalItems === 0) {
                this.tbody.innerHTML = `<tr><td colspan="${this.options.columns.length}" class="px-4 py-8 text-center text-muted">${this.options.emptyMessage}</td></tr>`;
                this.footer.innerHTML = '';
                return;
            }

            this.tbody.innerHTML = paginatedData.map(item => `
                <tr class="hover:bg-gray-50 border-b last:border-0 transition">
                    ${this.options.columns.map(col => `
                        <td class="px-4 py-3">
                            ${col.render ? col.render(item[col.key], item) : (item[col.key] ?? '')}
                        </td>
                    `).join('')}
                </tr>
            `).join('');

            this.renderFooter(totalItems, totalPages, start, end);
        }

        renderFooter(totalItems, totalPages, start, end) {
            this.footer.innerHTML = `
                <div>Showing <span class="font-semibold text-gray-900">${start + 1}</span> to <span class="font-semibold text-gray-900">${end}</span> of <span class="font-semibold text-gray-900">${totalItems}</span> entries</div>
                <div class="datatable-pagination flex gap-1">
                    <button class="btn btn-ghost btn-sm px-2 ${this.currentPage === 1 ? 'opacity-50 pointer-events-none' : ''}" data-page="${this.currentPage - 1}">Previous</button>
                    ${this.generatePageNumbers(totalPages)}
                    <button class="btn btn-ghost btn-sm px-2 ${this.currentPage === totalPages ? 'opacity-50 pointer-events-none' : ''}" data-page="${this.currentPage + 1}">Next</button>
                </div>
            `;

            this.footer.querySelectorAll('[data-page]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const page = parseInt(btn.dataset.page);
                    if (page >= 1 && page <= totalPages) {
                        this.currentPage = page;
                        this.render();
                    }
                });
            });
        }

        generatePageNumbers(totalPages) {
            let html = '';
            for (let i = 1; i <= totalPages; i++) {
                if (i === 1 || i === totalPages || (i >= this.currentPage - 1 && i <= this.currentPage + 1)) {
                    html += `<button class="btn btn-sm px-3 ${i === this.currentPage ? 'btn-primary' : 'btn-ghost'}" data-page="${i}">${i}</button>`;
                } else if (i === this.currentPage - 2 || i === this.currentPage + 2) {
                    html += `<span class="px-1">...</span>`;
                }
            }
            return html;
        }
    };

    // Global Alias
    global.DataTable = global.VanillaNext.DataTable;

})(window);
