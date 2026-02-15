
document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('.form-toggle-estado').forEach(form => {

        form.addEventListener('submit', function (e) {

            const boton = form.querySelector('button');
            const accion = boton.textContent.trim();

            let mensaje = '¿Confirmar acción?';

            if (accion === 'Desactivar') {
                mensaje = '¿Seguro que deseas DESACTIVAR este donante?';
            }

            if (accion === 'Activar') {
                mensaje = '¿Deseas ACTIVAR nuevamente este donante?';
            }

            if (!confirm(mensaje)) {
                e.preventDefault(); // ❌ cancela el submit
            }

        });

    });

});
