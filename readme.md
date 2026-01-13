🛍️ Shopping Ropa - Catálogo Digital
Este proyecto es una aplicación web para gestionar el stock de ropa de los Puestos 129 y 130.

🚀 Cómo iniciar la página
Abrí la terminal en la carpeta E:\shopping_ropa.

Ejecutá el comando: python app.py.

Abrí tu navegador en: http://localhost:5000.

🛠️ Panel de Administración
Acceso: http://localhost:5000/admin

Usuario: admin

Contraseña: admin

Funciones del Panel:
Cargar: Seleccioná la foto desde tu compu, elegí el puesto y poné el precio. El sistema guardará la imagen sola en la carpeta static/img.

Editar: Permite cambiar precios o detalles de un producto ya cargado.

Eliminar: Borra el producto de la web y también elimina el archivo de imagen de la carpeta para no ocupar espacio.

Buscador: Podés filtrar por nombre para encontrar productos rápido.

📱 Diseño Responsive
La web está optimizada para celulares. Los clientes verán imágenes grandes y tendrán un botón flotante de WhatsApp para enviarte pedidos directamente.

📁 Estructura del Proyecto
app.py: Servidor Flask y lógica.

tienda.db: Base de datos (SQLite).

templates/: Archivos HTML (Diseño).

static/img/: Carpeta donde se guardan las fotos de la ropa.

static/css/: Estilos de colores y formas.