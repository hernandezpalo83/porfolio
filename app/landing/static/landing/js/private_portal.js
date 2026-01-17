/**
 * CORE: Gestión de Interfaz del Portal Privado
 * Sistema: HernandezPalo Management System
 * Descripción: Maneja la interactividad del sidebar, persistencia de estado y feedback de UX.
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // --- 1. SELECTORES PRINCIPALES ---
    const sidebarToggle = document.getElementById('sidebarToggle');
    const wrapper = document.getElementById('wrapper');
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    let tooltips = [];

    // --- 2. GESTIÓN DEL SIDEBAR (PERSISTENCIA Y TOGGLE) ---
    
    /**
     * Aplica el estado guardado en el navegador antes de mostrar la interfaz
     * para evitar el efecto de "parpadeo" (FOUC).
     */
    const syncSidebarState = () => {
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed && wrapper) {
            wrapper.classList.add('toggled');
        }
    };
    syncSidebarState();

    if (sidebarToggle && wrapper) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            
            // Toggle de clase principal
            wrapper.classList.toggle('toggled');
            
            // Persistencia de la preferencia del usuario
            const isNowCollapsed = wrapper.classList.contains('toggled');
            localStorage.setItem('sidebarCollapsed', isNowCollapsed);

            // Actualizar tooltips según el nuevo estado
            toggleTooltipsState(isNowCollapsed);
        });
    }

    // --- 3. GESTIÓN DE TOOLTIPS (INTELIGENCIA RESPONSIVA) ---

    /**
     * Inicializa los tooltips de Bootstrap 5.
     * Solo deben ser funcionales cuando el menú está colapsado para no saturar la UI.
     */
    const initTooltips = () => {
        tooltips = tooltipTriggerList.map(el => new bootstrap.Tooltip(el, {
            trigger: 'hover',
            boundary: 'viewport'
        }));
        
        // Ejecución inicial según estado de carga
        const isCurrentlyCollapsed = wrapper ? wrapper.classList.contains('toggled') : false;
        toggleTooltipsState(isCurrentlyCollapsed);
    };

    /**
     * Habilita/Deshabilita tooltips dinámicamente.
     * @param {boolean} enable - Si el sidebar está colapsado, habilitar.
     */
    const toggleTooltipsState = (enable) => {
        tooltips.forEach(t => {
            enable ? t.enable() : t.disable();
        });
    };

    if (tooltipTriggerList.length > 0) initTooltips();

    // --- 4. UX: FEEDBACK EN PROCESOS CRÍTICOS (BACKUP / SYNC) ---

    /**
     * Maneja el feedback visual en formularios de larga duración 
     * para prevenir múltiples envíos y mejorar la percepción de velocidad.
     */
    const handleFormFeedback = (formId) => {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (!submitBtn) return;

            const originalHTML = submitBtn.innerHTML;
            
            // Estado de carga
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Ejecutando...
            `;
            
            // En procesos de descarga (como el SQL Backup), el navegador no recarga la página.
            // Restauramos el botón tras un timeout de seguridad.
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalHTML;
            }, 8000);
        });
    };

    // Inicializar feedback para formularios conocidos
    handleFormFeedback('backupForm');
    handleFormFeedback('syncForm'); // Para la futura sincronización con GitHub
});

/**
 * UTILS: Manejo de clics fuera del menú en dispositivos móviles
 */
document.addEventListener('click', function(event) {
    const wrapper = document.getElementById('wrapper');
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');

    // Si estamos en móvil y el menú está abierto, cerrar al hacer clic fuera
    if (window.innerWidth < 768 && 
        wrapper && wrapper.classList.contains('toggled') && 
        !sidebar.contains(event.target) && 
        !toggle.contains(event.target)) {
        wrapper.classList.remove('toggled');
    }
});

/**
 * GESTIÓN DE LA BIBLIOTECA DE PROMPTS
 * Funcionalidad: Carga dinámica de modal, edición y portapapeles.
 */

// 1. Inicialización de Modal (Singleton de Bootstrap)
const getPromptModal = () => {
    const element = document.getElementById('promptModal');
    return bootstrap.Modal.getOrCreateInstance(element);
};

/**
 * Prepara el modal para crear un nuevo registro (limpia campos)
 */
function openCreateModal() {
    const form = document.getElementById('promptForm');
    const modalLabel = document.getElementById('modalTitleLabel').querySelector('span');
    
    form.reset();
    document.getElementById('edit_id').value = ''; // Asegura que no hay ID
    modalLabel.innerText = "Nuevo Prompt";
    
    getPromptModal().show();
}

/**
 * Prepara el modal para edición cargando datos desde la Card seleccionada
 * @param {string} cardId - ID del elemento HTML de la card
 */
function prepareEdit(cardId) {
    const card = document.getElementById(cardId);
    const form = document.getElementById('promptForm');
    const modalLabel = document.getElementById('modalTitleLabel').querySelector('span');

    if (!card) return;

    // Extracción de datos desde data-attributes
    const data = {
        id: card.dataset.id,
        title: card.dataset.title,
        category: card.dataset.category,
        description: card.dataset.description,
        content: card.dataset.content // Aquí llega el código íntegro
    };

    // Inyección en los campos del formulario
    document.getElementById('edit_id').value = data.id;
    document.getElementById('modal_title').value = data.title;
    document.getElementById('modal_category').value = data.category;
    document.getElementById('modal_description').value = data.description;
    document.getElementById('modal_content').value = data.content;

    modalLabel.innerText = "Editar Prompt";
    
    getPromptModal().show();
}

/**
 * Copia el contenido del prompt al portapapeles con feedback visual
 * @param {HTMLElement} btn - El botón que ejecuta la acción
 * @param {string} cardId - El ID de la card para obtener el contenido
 */
function copyPromptToClipboard(btn, cardId) {
    const card = document.getElementById(cardId);
    if (!card) return;

    const textToCopy = card.dataset.content;

    navigator.clipboard.writeText(textToCopy).then(() => {
        // Feedback visual tipo Gemini
        const originalIcon = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check2 text-success"></i>';
        btn.classList.add('bg-success-subtle');

        setTimeout(() => {
            btn.innerHTML = originalIcon;
            btn.classList.remove('bg-success-subtle');
        }, 2000);
    }).catch(err => {
        console.error('Error al copiar: ', err);
    });
}

/**
 * Confirmación de eliminación de prompt
 * @param {string} index - Índice del prompt en la lista
 * @param {string} title - Título para mostrar en el mensaje
 */
function confirmDelete(index, title) {
    if (confirm(`¿Estás seguro de que deseas eliminar el prompt "${title}"? Esta acción no se puede deshacer en el repositorio.`)) {
        // Redirigir a la URL de eliminación
        // Asumiendo que la URL sigue el patrón /prompts/delete/1/
        window.location.href = `/prompts/delete/${index}/`;
    }
}