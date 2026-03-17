class AGGridManager {
    constructor(containerId, configUrl, apiBaseUrl) {
        this.containerId = containerId;
        this.configUrl = configUrl;
        this.apiBaseUrl = apiBaseUrl;
        this.gridApi = null;
        this.config = null;
        this.gridOptions = null;
        this.modalElement = null;
        this.bsModal = null;
    }

    async init() {
        this.showLoading();
        try {
            const response = await fetch(this.configUrl);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            this.config = await response.json();
            console.log('Grid Config:', this.config);

            const columnDefs = this.createColumnDefs();
            
            // Customize Theme via Grid Options
            this.gridOptions = {
                columnDefs: columnDefs,
                defaultColDef: {
                    sortable: true,
                    filter: true,
                    resizable: true,
                    flex: 1,
                    minWidth: 100,
                },
                pagination: true,
                paginationPageSize: this.config.pagination_size || 20,
                paginationPageSizeSelector: [10, 20, 50, 100],
                onCellValueChanged: (params) => this.onCellValueChanged(params),
            };

            const eGridDiv = document.querySelector(`#${this.containerId}`);
            if (!eGridDiv) throw new Error(`Container #${this.containerId} not found`);

            this.gridApi = agGrid.createGrid(eGridDiv, this.gridOptions);
            
            this.setupUI();
            this.setupModal();
            await this.loadData();
        } catch (error) {
            console.error('Error initializing AG Grid:', error);
            this.showToast(`Error: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    createColumnDefs() {
        const defs = this.config.fields_to_display.map(field => {
            const info = this.config.field_info[field] || {};
            return {
                field: field,
                headerName: info.verbose_name || field.charAt(0).toUpperCase() + field.slice(1),
                editable: this.config.mode === 'edit' && this.config.inline_editing && info.editable,
                filter: info.type === 'number' ? 'agNumberColumnFilter' : 'agTextColumnFilter',
            };
        });

        // Add Actions Column
        if (this.config.mode === 'edit') {
            defs.push({
                headerName: 'Acciones',
                field: 'actions',
                pinned: 'right',
                width: 120,
                sortable: false,
                filter: false,
                cellRenderer: (params) => {
                    const div = document.createElement('div');
                    div.className = 'd-flex gap-2 py-1';
                    
                    const editBtn = document.createElement('button');
                    editBtn.className = 'btn btn-sm btn-outline-primary border-0';
                    editBtn.innerHTML = '<i class="bi bi-pencil-square"></i>';
                    editBtn.onclick = () => this.openModal('edit', params.data);
                    
                    const deleteBtn = document.createElement('button');
                    deleteBtn.className = 'btn btn-sm btn-outline-danger border-0';
                    deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
                    deleteBtn.onclick = () => this.deleteRecord(params.data.id);
                    
                    div.appendChild(editBtn);
                    div.appendChild(deleteBtn);
                    return div;
                }
            });
        }
        return defs;
    }

    async loadData() {
        try {
            const response = await fetch(this.apiBaseUrl);
            const data = await response.json();
            const rowData = data.results || data;
            this.gridApi.setGridOption('rowData', rowData);
        } catch (error) {
            this.showToast('Error al cargar datos', 'error');
        }
    }

    setupUI() {
        const container = document.querySelector(`#${this.containerId}`);
        const headerDiv = document.createElement('div');
        headerDiv.className = 'd-flex justify-content-between align-items-center mb-3 bg-white p-3 rounded shadow-sm border';

        // Search
        const searchInput = document.createElement('div');
        searchInput.className = 'input-group w-50';
        searchInput.innerHTML = `
            <span class="input-group-text bg-transparent border-end-0"><i class="bi bi-search"></i></span>
            <input type="text" class="form-control border-start-0 ps-0" placeholder="Buscar productos...">
        `;
        searchInput.querySelector('input').addEventListener('input', (e) => {
            this.gridApi.setGridOption('quickFilterText', e.target.value);
        });

        // Add Button
        const controls = document.createElement('div');
        controls.className = 'd-flex gap-2';
        
        if (this.config.mode === 'edit') {
            const createBtn = document.createElement('button');
            createBtn.className = 'btn btn-primary d-flex align-items-center gap-2';
            createBtn.innerHTML = '<i class="bi bi-plus-lg"></i> Nuevo Registro';
            createBtn.onclick = () => this.openModal('create');
            controls.appendChild(createBtn);
        }

        if (this.config.enable_export) {
            const exportBtn = document.createElement('button');
            exportBtn.className = 'btn btn-outline-secondary';
            exportBtn.innerHTML = '<i class="bi bi-download"></i> CSV';
            exportBtn.onclick = () => this.gridApi.exportDataAsCsv();
            controls.appendChild(exportBtn);
        }

        headerDiv.appendChild(searchInput);
        headerDiv.appendChild(controls);
        container.before(headerDiv);
    }

    setupModal() {
        const modalId = `${this.containerId}-modal`;
        let modalHtml = `
            <div class="modal fade" id="${modalId}" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content shadow-lg border-0">
                        <div class="modal-header border-bottom-0 pb-0">
                            <h5 class="modal-title fw-bold" id="modal-title">Editar Registro</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body p-4">
                            <form id="${modalId}-form"></form>
                        </div>
                        <div class="modal-footer border-top-0 pt-0">
                            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary px-4" id="${modalId}-save">Guardar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        this.modalElement = document.getElementById(modalId);
        this.bsModal = new bootstrap.Modal(this.modalElement);
        
        document.getElementById(`${modalId}-save`).onclick = () => this.saveRecord();
    }

    openModal(mode, data = null) {
        const form = document.querySelector(`#${this.containerId}-modal-form`);
        const title = document.getElementById('modal-title');
        title.innerText = mode === 'create' ? 'Nuevo Registro' : 'Editar Registro';
        
        form.innerHTML = '';
        form.dataset.mode = mode;
        if (data) form.dataset.id = data.id;

        this.config.fields_to_display.forEach(field => {
            const info = this.config.field_info[field];
            if (!info || (!info.editable && mode === 'edit')) return;

            const value = data ? data[field] : '';
            const fieldId = `field-${field}`;
            
            const group = document.createElement('div');
            group.className = 'mb-3';
            group.innerHTML = `
                <label for="${fieldId}" class="form-label small fw-semibold text-muted">${info.verbose_name || field}</label>
                <input type="${info.type === 'number' ? 'number' : 'text'}" 
                       class="form-control" 
                       id="${fieldId}" 
                       name="${field}" 
                       value="${value}" 
                       ${info.required ? 'required' : ''}>
            `;
            form.appendChild(group);
        });

        this.bsModal.show();
    }

    async saveRecord() {
        const form = document.querySelector(`#${this.containerId}-modal-form`);
        const mode = form.dataset.mode;
        const id = form.dataset.id;
        const formData = new FormData(form);
        const jsonData = Object.fromEntries(formData.entries());

        const url = mode === 'create' ? this.apiBaseUrl : `${this.apiBaseUrl}${id}/`;
        const method = mode === 'create' ? 'POST' : 'PATCH';

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                },
                body: JSON.stringify(jsonData),
            });

            if (!response.ok) throw new Error('Error al guardar');
            
            this.showToast(`Registro ${mode === 'create' ? 'creado' : 'actualizado'} con éxito`, 'success');
            this.bsModal.hide();
            await this.loadData();
        } catch (error) {
            this.showToast('Error al guardar los datos', 'error');
        }
    }

    async deleteRecord(id) {
        if (!confirm('¿Estás seguro de que deseas eliminar este registro?')) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                },
            });

            if (!response.ok) throw new Error('Error al eliminar');
            
            this.showToast('Registro eliminado con éxito', 'success');
            await this.loadData();
        } catch (error) {
            this.showToast('Error al eliminar el registro', 'error');
        }
    }

    async onCellValueChanged(params) {
        const { data, colDef, newValue } = params;
        try {
            const response = await fetch(`${this.apiBaseUrl}${data.id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken'),
                },
                body: JSON.stringify({ [colDef.field]: newValue }),
            });
            if (!response.ok) throw new Error();
            this.showToast('Cambio guardado', 'success');
        } catch (error) {
            this.showToast('Error al guardar', 'error');
            params.node.setDataValue(colDef.field, params.oldValue);
        }
    }

    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 p-3 rounded-lg shadow-lg text-white ${type === 'error' ? 'bg-danger' : 'bg-success'} z-[2000] animate__animated animate__fadeInUp`;
        toast.style.minWidth = '200px';
        toast.innerHTML = `
            <div class="d-flex align-items-center gap-2">
                <i class="bi ${type === 'error' ? 'bi-exclamation-circle' : 'bi-check-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.classList.replace('animate__fadeInUp', 'animate__fadeOutDown');
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }

    showLoading() {
        const spinner = document.createElement('div');
        spinner.id = 'grid-loading';
        spinner.className = 'fixed inset-0 flex items-center justify-center bg-white bg-opacity-75 z-[3000]';
        spinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div>';
        document.body.appendChild(spinner);
    }

    hideLoading() {
        const spinner = document.getElementById('grid-loading');
        if (spinner) spinner.remove();
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
