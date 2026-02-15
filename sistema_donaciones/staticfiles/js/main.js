function actualizarHora() {
    const now = new Date();
    const hora = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    document.getElementById('hora').textContent = hora;
}
actualizarHora(); // primera vez
setInterval(actualizarHora, 1000);


// Control del toggle del sidebar
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');

    // Función para alternar el sidebar en dispositivos móviles
    function toggleSidebar() {
        // Alternar la clase 'transform -translate-x-full' en el sidebar
        sidebar.classList.toggle('-translate-x-full');
    }

    // Escuchar el click en el botón de la hamburguesa
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // Lógica para asegurar que el sidebar se comporta correctamente al cambiar el tamaño de la ventana
    window.addEventListener('resize', function () {
        // Si la pantalla es grande (sm: o más), asegura que esté visible
        if (window.innerWidth >= 640 && sidebar.classList.contains('-translate-x-full')) {
            sidebar.classList.remove('-translate-x-full');
        }
        // Si la pantalla es pequeña y está abierto, lo oculta
        else if (window.innerWidth < 640 && !sidebar.classList.contains('-translate-x-full')) {
            sidebar.classList.add('-translate-x-full');
        }
    });

    // Inicializar en modo móvil (oculto) si el ancho es menor a 640px
    if (window.innerWidth < 640) {
        sidebar.classList.add('-translate-x-full');
    }
});
