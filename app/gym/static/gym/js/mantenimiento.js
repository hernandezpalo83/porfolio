/**
 * mantenimiento.js
 * Lógica genérica para mantenimiento de modelos basado en metadatos.
 */

const MantenimientoGenerico = {
    metadata: null,
    apiUrl: null,
    currentId: null,

    init: async function(apiUrl) {
        this.apiUrl = apiUrl;
        await this.fetchMetadata();
        this.setupEventListeners();
    },

    fetchMetadata: async function() {
        try {
            const response = await fetch(`${this.apiUrl}metadata/`);
            this.metadata = await response.json();
        } catch (e) {
            console.error("Error fetching metadata:", e);
        }
    },

    setupEventListeners: function() {
        // Escuchar evento de edición de Tabulator (enviado por components.js)
        window.addEventListener('tabulator-edit', (e) => {
            this.openEditModal(e.detail.row);
        });

        // El botón "Añadir Nuevo" llama a abrirModalCrear()
        window.abrirModalCrear = () => {
            this.openCreateModal();
        };
    },

    openCreateModal: function() {
        this.currentId = null;
        this.renderForm({});
        showModal('modalMantenimiento');
        this.updateModalTitle('Añadir Nuevo Registro');
    },

    openEditModal: function(data) {
        this.currentId = data.id;
        this.renderForm(data);
        showModal('modalMantenimiento');
        this.updateModalTitle('Editar Registro');
    },

    updateModalTitle: function(title) {
        const modal = document.getElementById('modal-modalMantenimiento');
        const titleEl = modal.querySelector('h3');
        if (titleEl) titleEl.innerText = title;
    },

    renderForm: function(data) {
        const modalBody = document.querySelector('#modal-modalMantenimiento .overflow-y-auto');
        if (!modalBody) return;

        let html = '<form id="generic-crud-form" class="space-y-4">';
        
        this.metadata.forEach(field => {
            const val = data[field.name] || '';
            const requiredAttr = field.required ? 'required' : '';
            
            html += `<div>
                <label class="block text-sm font-medium text-gray-700 mb-1">${field.label}</label>`;

            if (field.type === 'textarea') {
                html += `<textarea name="${field.name}" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm" rows="3" ${requiredAttr}>${val}</textarea>`;
            } else if (field.type === 'number') {
                html += `<input type="number" step="any" name="${field.name}" value="${val}" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm" ${requiredAttr}>`;
            } else if (field.type === 'datetime') {
                const dateVal = val ? val.substring(0, 16) : ''; // Format for datetime-local
                html += `<input type="datetime-local" name="${field.name}" value="${dateVal}" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm" ${requiredAttr}>`;
            } else {
                html += `<input type="text" name="${field.name}" value="${val}" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm" ${requiredAttr}>`;
            }
            
            if (field.help_text) {
                html += `<p class="mt-1 text-xs text-gray-400">${field.help_text}</p>`;
            }
            html += `</div>`;
        });

        html += '</form>';
        modalBody.innerHTML = html;

        // Cambiar texto del botón de confirmar en el footer del modal
        const confirmBtn = document.querySelector('#modal-modalMantenimiento .bg-primary-600');
        if (confirmBtn) {
            confirmBtn.onclick = () => this.save();
            confirmBtn.innerText = this.currentId ? 'Actualizar' : 'Crear';
        }
    },

    save: async function() {
        const form = document.getElementById('generic-crud-form');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = new FormData(form);
        const jsonData = Object.fromEntries(formData.entries());
        
        const method = this.currentId ? 'PUT' : 'POST';
        const url = this.currentId ? `${this.apiUrl}${this.currentId}/` : this.apiUrl;

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(jsonData)
            });

            if (response.ok) {
                hideModal('modalMantenimiento');
                // Recargar tabla (usando el objeto global de components.js si está disponible)
                if (window.tabulators && window.tabulators['main']) {
                    window.tabulators['main'].setData();
                } else {
                    location.reload();
                }
            } else {
                const err = await response.json();
                alert("Error al guardar: " + JSON.stringify(err));
            }
        } catch (e) {
            console.error("Save error:", e);
        }
    },

    delete: async function(id) {
        try {
            const response = await fetch(`${this.apiUrl}${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (response.ok) {
                // Recargar tabla
                if (window.tabulators && window.tabulators['main']) {
                    window.tabulators['main'].setData();
                } else {
                    location.reload();
                }
            } else {
                alert("Error al eliminar el registro.");
            }
        } catch (e) {
            console.error("Delete error:", e);
        }
    },

    getCsrfToken: function() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    }
};
