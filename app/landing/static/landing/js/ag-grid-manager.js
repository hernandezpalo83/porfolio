class AGGridManager {
    constructor(containerId, configUrl, apiBaseUrl) {
        this.containerId = containerId;
        this.configUrl = configUrl;
        this.apiBaseUrl = apiBaseUrl;
        this.gridApi = null;
        this.config = null;
        this.gridOptions = null;
    }

    async init() {
        this.showLoading();
        try {
            console.log('Fetching config from:', this.configUrl);
            const response = await fetch(this.configUrl);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            this.config = await response.json();
            console.log('Config loaded:', this.config);

            if (!this.config || !this.config.fields_to_display) {
                throw new Error('Formato de configuración inválido: falta fields_to_display');
            }
            
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
            };

            const eGridDiv = document.querySelector(`#${this.containerId}`);
            if (!eGridDiv) throw new Error(`Container #${this.containerId} not found`);

            // AG Grid v31.0+ Syntax
            if (typeof agGrid.createGrid === 'function') {
                this.gridApi = agGrid.createGrid(eGridDiv, this.gridOptions);
            } else {
                // Compatibility for older versions
                new agGrid.Grid(eGridDiv, this.gridOptions);
                this.gridApi = this.gridOptions.api;
            }
            
            this.setupUI();
            await this.loadData();
        } catch (error) {
            console.error('Error initializing AG Grid:', error);
            this.showToast(`Error: ${error.message}`, 'error');
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
        try {
            const response = await fetch(this.apiBaseUrl);
            if (!response.ok) throw new Error(`API error! status: ${response.status}`);
            const data = await response.json();
            const rowData = data.results || data;

            if (this.gridApi && this.gridApi.setGridOption) {
                this.gridApi.setGridOption('rowData', rowData);
            } else if (this.gridApi && this.gridApi.setRowData) {
                this.gridApi.setRowData(rowData);
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.showToast('Error al cargar datos del grid', 'error');
        }
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
            // Revert value
            params.node.setDataValue(colDef.field, params.oldValue);
        }
    }

    exportData() {
        if (this.config.enable_export) {
            if (this.gridApi.exportDataAsCsv) {
                this.gridApi.exportDataAsCsv();
            } else {
                this.gridOptions.api.exportDataAsCsv();
            }
        }
    }

    setupUI() {
        const container = document.querySelector(`#${this.containerId}`);
        if (this.config.enable_quick_filter) {
            const filterInput = document.createElement('input');
            filterInput.placeholder = 'Buscar...';
            filterInput.className = 'w-full p-2 mb-4 border rounded shadow-sm focus:ring-2 focus:ring-blue-500';
            filterInput.addEventListener('input', (e) => {
                if (this.gridApi.setGridOption) {
                    this.gridApi.setGridOption('quickFilterText', e.target.value);
                } else {
                    this.gridOptions.api.setQuickFilter(e.target.value);
                }
            });
            container.before(filterInput);
        }

        if (this.config.enable_export) {
            const exportBtn = document.createElement('button');
            exportBtn.innerText = 'Exportar CSV';
            exportBtn.className = 'bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4 ml-2 transition-colors';
            exportBtn.onclick = () => this.exportData();
            container.before(exportBtn);
        }
    }

    showToast(message, type) {
        console.log(`[TOAST ${type.toUpperCase()}]: ${message}`);
        // Basic visible feedback
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 p-4 rounded text-white ${type === 'error' ? 'bg-red-600' : 'bg-green-600'} z-[100]`;
        toast.innerText = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
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
