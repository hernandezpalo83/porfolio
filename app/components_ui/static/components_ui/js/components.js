/**
 * components.js
 * Vanilla JavaScript helpers para Django Components UI.
 * Incluye lógica para tooltips, modales, alertas, etc.
 */

document.addEventListener('DOMContentLoaded', () => {
    initModals();
    initDismissibles();
    initDropdowns();
    initTabulators();
});

const tabulators = {};

function initTabulators() {
    document.querySelectorAll('[data-comp-type="tabulator"]').forEach(container => {
        if (container.classList.contains('tabulator-initialized')) return;
        container.classList.add('tabulator-initialized');

        const id = container.id.replace('tabulator-', '');
        const url = container.getAttribute('data-url');
        const pageSize = parseInt(container.getAttribute('data-page-size') || 10);
        const groupBy = container.getAttribute('data-group-by');
        const filterable = container.getAttribute('data-filterable') === 'true';
        const selectable = container.getAttribute('data-selectable') === 'true';
        const editable = container.getAttribute('data-editable') === 'true';
        let columnsData = [];
        
        try {
            columnsData = JSON.parse(container.getAttribute('data-columns') || '[]');
        } catch (e) { console.error("Error parsing columns for Tabulator", e); }

        // Definir columnas si no se proporcionan
        let columns = [];
        if (selectable) {
            columns.push({formatter:"rowSelection", titleFormatter:"rowSelection", hozAlign: "center", headerSort:false, width: 40});
        }

        if (columnsData.length > 0) {
            columns = columns.concat(columnsData.map(col => ({
                title: col.title || col.name || col.field,
                field: col.field || col.name,
                headerFilter: filterable ? "input" : false,
                editor: editable ? "input" : false,
                sortable: true,
                ...col
            })));
        }

        if (editable) {
            columns.push({
                formatter: function() { return "<button class='text-primary-600 hover:text-primary-900 font-medium'>Editar</button>"; },
                width: 80, hozAlign: "center", headerSort: false,
                cellClick: function(e, cell) {
                    window.dispatchEvent(new CustomEvent('tabulator-edit', {detail: {row: cell.getRow().getData()}}));
                }
            });
        }

        const tableOptions = {
            ajaxURL: url !== '/' ? url : null,
            layout: "fitColumns",
            pagination: "local",
            paginationSize: pageSize,
            groupBy: groupBy || null,
            groupHeader: function(value, count, data, group){
                return value + "<span class='ml-2 text-gray-500 text-xs'>(" + count + " items)</span>";
            },
            placeholder: "No hay datos disponibles",
            locale: "es",
            langs: {
                "es": {
                    "pagination": {
                        "first": "Primero",
                        "prev": "Anterior",
                        "next": "Siguiente",
                        "last": "Último",
                    }
                }
            }
        };

        if (columns.length > 0) {
            tableOptions.columns = columns;
        } else {
            tableOptions.autoColumns = true;
        }

        const table = new Tabulator(container, tableOptions);

        table.on("tableBuilt", () => {
             // Escondemos cargador que esté dentro o cerca
             const loader = container.querySelector('.animate-pulse') || container.parentElement.querySelector('.animate-pulse');
             if (loader) loader.classList.add('hidden');
        });

        tabulators[id] = table;
    });
}
    // Listener para búsqueda global
    window.addEventListener('tabulator-search', (e) => {
        const { id, value } = e.detail;
        if (tabulators[id]) {
            tabulators[id].setFilter(function(data) {
                return Object.values(data).some(val => 
                    String(val).toLowerCase().includes(value.toLowerCase())
                );
            });
        }
    });

function initModals() {
    document.querySelectorAll('[data-modal-toggle]').forEach(button => {
        if (button.classList.contains('comp-modal-initialized')) return;
        button.classList.add('comp-modal-initialized');
        
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-modal-toggle');
            const targetModal = document.getElementById(targetId);
            if (targetModal) {
                targetModal.classList.remove('hidden');
                targetModal.setAttribute('aria-hidden', 'false');
                document.body.style.overflow = 'hidden'; // Prevents background scrolling
            }
        });
    });

    // Cerrar modales (botones close)
    document.querySelectorAll('[data-modal-hide]').forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-modal-hide');
            closeModal(targetId);
        });
    });

    // Cerrar al hacer click fuera (backdrop)
    document.querySelectorAll('.comp-modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) {
                const targetId = backdrop.closest('[role="dialog"]').id;
                closeModal(targetId);
            }
        });
    });
}

function closeModal(targetId) {
    const targetModal = document.getElementById(targetId);
    if (targetModal) {
        targetModal.classList.add('hidden');
        targetModal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
}

function initDismissibles() {
    document.querySelectorAll('[data-dismiss-target]').forEach(button => {
        if (button.classList.contains('comp-dismiss-initialized')) return;
        button.classList.add('comp-dismiss-initialized');

        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-dismiss-target');
            const targetElement = document.getElementById(targetId) || document.querySelector(targetId);
            if (targetElement) {
                targetElement.remove();
            }
        });
    });
}

function initDropdowns() {
    document.querySelectorAll('[data-dropdown-toggle]').forEach(button => {
        if (button.classList.contains('comp-dropdown-initialized')) return;
        button.classList.add('comp-dropdown-initialized');
        
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            const targetId = button.getAttribute('data-dropdown-toggle');
            const targetDropdown = document.getElementById(targetId);
            if (targetDropdown) {
                targetDropdown.classList.toggle('hidden');
            }
        });
    });

    // Cerrar dropdown al clicar fuera
    document.addEventListener('click', () => {
        document.querySelectorAll('.comp-dropdown-menu').forEach(menu => {
            if (!menu.classList.contains('hidden')) {
                menu.classList.add('hidden');
            }
        });
    });
}
