// categorias.js
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modalEditar');
    const formEditar = document.getElementById('formEditar');
    const btnCerrar = document.getElementById('btnCerrar');
    const botonesEditar = document.querySelectorAll('.btn-editar');

    // Asegurar que el modal esté oculto al cargar
    modal.style.display = 'none';

    // Función para abrir modal
    function abrirModal(id, nombre, descripcion) {
        document.getElementById('editId').value = id;
        document.getElementById('editNombre').value = nombre;
        document.getElementById('editDescripcion').value = descripcion;

        // Mostrar modal - FORZAR posición fixed
        modal.style.display = 'flex';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.right = '0';
        modal.style.bottom = '0';
        modal.style.zIndex = '9999';
        
        // Prevenir scroll del body cuando el modal está abierto
        document.body.style.overflow = 'hidden';
    }

    // Función para cerrar modal
    function cerrarModal() {
        modal.style.display = 'none';
        // Restaurar scroll del body
        document.body.style.overflow = '';
    }

    // Abrir modal al hacer clic en "Editar"
    botonesEditar.forEach(boton => {
        boton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const id = this.getAttribute('data-id');
            const nombre = this.getAttribute('data-nombre');
            const descripcion = this.getAttribute('data-descripcion');

            abrirModal(id, nombre, descripcion);
        });
    });

    // Cerrar modal al hacer clic en "Cancelar"
    if (btnCerrar) {
        btnCerrar.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            cerrarModal();
        });
    }

    // Cerrar modal al hacer clic fuera del contenido
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            cerrarModal();
        }
    });

    // Cerrar modal con la tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'flex') {
            cerrarModal();
        }
    });
});