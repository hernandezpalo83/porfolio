document.addEventListener('DOMContentLoaded', function() {
    // Obtener el modal
    var modal = document.getElementById("loginModal");

    // Obtener el botón que abre el modal
    var btn = document.getElementById("loginBtn");

    // Verificar si el botón existe en el DOM
    if (!btn) {
        console.error("El botón con id 'loginBtn' no se encontró en el DOM.");
        return;
    }

    // Obtener el elemento <span> que cierra el modal
    var span = document.getElementsByClassName("close")[0];

    // Verificar si el elemento <span> existe en el DOM
    if (!span) {
        console.error("El elemento con clase 'close' no se encontró en el DOM.");
        return;
    }

    // Cuando el usuario hace clic en el botón, abre el modal
    btn.onclick = function() {
        modal.style.display = "block";
    }

    // Cuando el usuario hace clic en <span> (x), cierra el modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // Cuando el usuario hace clic en cualquier lugar fuera del modal, lo cierra
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
});