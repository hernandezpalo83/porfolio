document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const wrapper = document.getElementById('wrapper');
    
    // Toggle Sidebar
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            wrapper.classList.toggle('toggled');
            
            // Guardar preferencia del usuario en localStorage
            const isCollapsed = wrapper.classList.contains('toggled');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
    }

    // Mantener estado al recargar
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        wrapper.classList.add('toggled');
    }

    // Inicializar Tooltips de Bootstrap para el modo colapsado
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            // Solo mostrar si el sidebar está colapsado
            trigger: 'hover'
        });
    });
});

// Manejo de la acción de Backup con feedback
const backupForm = document.getElementById('backupForm');
if (backupForm) {
    backupForm.addEventListener('submit', function() {
        const btn = this.querySelector('button');
        const originalText = btn.innerHTML;
        
        // Efecto visual de carga
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Procesando...';
        
        // Nota: El formulario se enviará normalmente, 
        // pero esto mejora la UX para evitar clics dobles.
        setTimeout(() => {
            // Restauramos después de un tiempo por si es descarga de archivo
            btn.disabled = false;
            btn.innerHTML = originalText;
        }, 5000);
    });
}