/**
 * CORE: Gestión de Interfaz del Portal Privado
 * Sistema: HernandezPalo Management System
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // --- 1. SELECTORES PRINCIPALES ---
    const sidebarToggle = document.getElementById('sidebarToggle');
    const wrapper = document.getElementById('wrapper');
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    let tooltips = [];

    // --- 2. GESTIÓN DEL SIDEBAR (PERSISTENCIA Y TOGGLE) ---
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
            wrapper.classList.toggle('toggled');
            const isNowCollapsed = wrapper.classList.contains('toggled');
            localStorage.setItem('sidebarCollapsed', isNowCollapsed);
            toggleTooltipsState(isNowCollapsed);
        });
    }

    // --- 3. GESTIÓN DE TOOLTIPS (INTELIGENCIA RESPONSIVA) ---
    const initTooltips = () => {
        tooltips = tooltipTriggerList.map(el => new bootstrap.Tooltip(el, {
            trigger: 'hover',
            boundary: 'viewport'
        }));
        const isCurrentlyCollapsed = wrapper ? wrapper.classList.contains('toggled') : false;
        toggleTooltipsState(isCurrentlyCollapsed);
    };

    const toggleTooltipsState = (enable) => {
        tooltips.forEach(t => {
            enable ? t.enable() : t.disable();
        });
    };

    if (tooltipTriggerList.length > 0) initTooltips();

    // --- 4. UX: FEEDBACK EN PROCESOS CRÍTICOS (BACKUP / SYNC) ---
    const handleFormFeedback = (formId) => {
        const form = document.getElementById(formId);
        if (!form) return;
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (!submitBtn) return;
            const originalHTML = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Ejecutando...`;
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalHTML;
            }, 8000);
        });
    };
    handleFormFeedback('backupForm');
    handleFormFeedback('syncForm');
});

// UTILS: Clic fuera en móviles
document.addEventListener('click', function(event) {
    const wrapper = document.getElementById('wrapper');
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');
    if (window.innerWidth < 768 && wrapper && wrapper.classList.contains('toggled') && 
        sidebar && !sidebar.contains(event.target) && !toggle.contains(event.target)) {
        wrapper.classList.remove('toggled');
    }
});

// GESTIÓN DE LA BIBLIOTECA DE PROMPTS
const getPromptModal = () => {
    const element = document.getElementById('promptModal');
    return element ? bootstrap.Modal.getOrCreateInstance(element) : null;
};

function openCreateModal() {
    const form = document.getElementById('promptForm');
    const modalLabel = document.getElementById('modalTitleLabel').querySelector('span');
    if (form) form.reset();
    document.getElementById('edit_id').value = '';
    modalLabel.innerText = "Nuevo Prompt";
    const modal = getPromptModal();
    if(modal) modal.show();
}

function prepareEdit(cardId) {
    const card = document.getElementById(cardId);
    const modalLabel = document.getElementById('modalTitleLabel').querySelector('span');
    if (!card) return;
    document.getElementById('edit_id').value = card.dataset.id;
    document.getElementById('modal_title').value = card.dataset.title;
    document.getElementById('modal_category').value = card.dataset.category;
    document.getElementById('modal_description').value = card.dataset.description;
    document.getElementById('modal_content').value = card.dataset.content;
    modalLabel.innerText = "Editar Prompt";
    const modal = getPromptModal();
    if(modal) modal.show();
}

function copyPromptToClipboard(btn, cardId) {
    const card = document.getElementById(cardId);
    if (!card) return;
    navigator.clipboard.writeText(card.dataset.content).then(() => {
        const originalIcon = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check2 text-success"></i>';
        btn.classList.add('bg-success-subtle');
        setTimeout(() => {
            btn.innerHTML = originalIcon;
            btn.classList.remove('bg-success-subtle');
        }, 2000);
    });
}

function confirmDelete(index, title) {
    if (confirm(`¿Estás seguro de que deseas eliminar el prompt "${title}"?`)) {
        window.location.href = `/prompts/delete/${index}/`;
    }
}