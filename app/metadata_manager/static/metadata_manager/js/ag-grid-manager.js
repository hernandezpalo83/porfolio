class AGGridManager {
    constructor(containerId, configUrl, apiBaseUrl) {
        this.containerId = containerId;
        this.configUrl = configUrl;
        this.apiBaseUrl = apiBaseUrl;
        this.gridOptions = null;
        this.config = null;
    }

    async init() {
        this.showLoading();
        try {
            const response = await fetch(this.configUrl);
            this.config = await response.json();
            
            const columnDefs = this.createColumnDefs();
            
            this.gridOptions = {
                columnDefs: columnDefs,
                defaultColDef: {
                    sortable: true,
                    filter: true,
                    resizable: this.config.enable_reorder,
                    suppressMovable: !this.config.enable_reorder,
                    flex: 1,
                },
                pagination: true,
                paginationPageSize: this.config.pagination_size,
                onCellValueChanged: (params) => this.onCellValueChanged(params),
                // Other AG Grid options
            };

            const eGridDiv = document.querySelector(`#${this.containerId}`);
            new agGrid.Grid(eGridDiv, this.gridOptions);
            
            this.setupUI();
            this.loadData();
        } catch (error) {
            console.error('Error initializing AG Grid:', error);
            this.showToast('Error cargando configuración', 'error');
        } finally {
            this.hideLoading();
        }
    }

    createColumnDefs() {
        return this.config.fields_to_display.map(field => ({
            field: field,
            headerName: this.capitalize(field),
            editable: this.config.mode === 'edit' && this.config.inline_editing && this.config.editable_fields.includes(field),
        }));
    }

    async loadData() {
        const response = await fetch(this.apiBaseUrl);
        const data = await response.json();
        this.gridOptions.api.setRowData(data.results || data);
    }

    async onCellValueChanged(params) {
        const { data, colDef, newValue } = params;
        const id = data.id;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}${id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                },
                body: JSON.stringify({ [colDef.field]: newValue }),
            });

            if (response.ok) {
                this.showToast('Cambio guardado con éxito', 'success');
            } else {
                throw new Error('Error al guardar');
            }
        } catch (error) {
            this.showToast('Error al guardar cambios', 'error');
            params.node.setDataValue(colDef.field, params.oldValue);
        }
    }

    exportData() {
        if (this.config.enable_export) {
            this.gridOptions.api.exportDataAsCsv();
        }
    }

    setupUI() {
        if (this.config.enable_quick_filter) {
            const filterInput = document.createElement('input');
            filterInput.placeholder = 'Buscar...';
            filterInput.className = 'w-full p-2 mb-4 border rounded shadow-sm focus:ring-2 focus:ring-blue-500';
            filterInput.addEventListener('input', (e) => {
                this.gridOptions.api.setQuickFilter(e.target.value);
            });
            document.querySelector(`#${this.containerId}`).before(filterInput);
        }

        if (this.config.enable_export) {
            const exportBtn = document.createElement('button');
            exportBtn.innerText = 'Exportar CSV';
            exportBtn.className = 'bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4 ml-2 transition-colors';
            exportBtn.onclick = () => this.exportData();
            document.querySelector(`#${this.containerId}`).before(exportBtn);
        }
    }

    showToast(message, type) {
        // Implementación básica de Toast
        console.log(`[TOAST ${type.toUpperCase()}]: ${message}`);
        // Aquí podrías usar una librería como Toastify o implementar uno con Tailwind
    }

    showLoading() {
        const spinner = document.createElement('div');
        spinner.id = 'grid-loading';
        spinner.className = 'fixed inset-0 flex items-center justify-center bg-white bg-opacity-50 z-50';
        spinner.innerHTML = '<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>';
        document.body.appendChild(spinner);
    }

    hideLoading() {
        const spinner = document.getElementById('grid-loading');
        if (spinner) spinner.remove();
    }

    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}
