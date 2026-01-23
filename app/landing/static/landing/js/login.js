// Login Form Interactions

// Mejora la UX: cambia el texto del botón al enviar para feedback instantáneo
const form = document.getElementById('loginForm');
const btn = document.getElementById('btnSubmit');

form.addEventListener('submit', function() {
    btn.classList.add('loading');
    btn.innerHTML = 'Iniciando sesión...';
});

// Limpieza automática de errores al empezar a escribir
const inputs = document.querySelectorAll('input');
inputs.forEach(input => {
    input.addEventListener('input', () => {
        const error = document.querySelector('.error-message');
        if (error) error.style.display = 'none';
    });
});
