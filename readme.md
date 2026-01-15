# 🛍️ Shopping Ropa - Puestos 129 y 130
Catálogo Digital y Sistema de Gestión de Stock.

## 🚀 Inicio Rápido (Local)
1. **Carpeta:** `E:\shopping_ropa`
2. **Comando:** `python app.py`
3. **URL:** [http://localhost:5000](http://localhost:5000)

---

## 🛠️ Panel de Control (Admin)
| Acceso | Credenciales |
| :--- | :--- |
| **URL** | `/admin` |
| **Usuario** | `admin` |
| **Clave** | `admin` |

### ✨ Funciones Principales:
* **Gestión de Stock:** Carga de productos con hasta 6 imágenes.
* **Control de Galería:** Las fotos se guardan automáticamente en `static/img`.
* **Limpieza Automática:** Al eliminar un producto, se borra su imagen para no saturar el servidor.
* **Optimización Móvil:** Diseño adaptado para celulares y botón directo de **WhatsApp**.

---

## 📁 Estructura del Sistema
* `app.py`: Motor principal de la aplicación.
* `tienda.db`: Base de datos (SQLite) con todos los productos.
* `static/`: Contiene imágenes (`img/`) y estilos visuales (`css/`).
* `templates/`: Diseños HTML (Index, Admin, Editar).

---

## ✅ Mejoras Recientes (15/01/2026)

### 🔐 Seguridad y Auditoría
* **Registro de Vendedoras:** Se implementó `accesos_vendedoras.txt` que registra:
    * 📅 Fecha y Hora (Ajustada a **Argentina**).
    * 🌐 Dirección IP del dispositivo.
    * 📄 Soporte **UTF-8** para lectura correcta en la nube.
* **Cierre de Sesión:** Botón de Logout funcional con redirección segura al catálogo.

### 📊 Gestión de Stock
* **Contadores:** Se agregaron sumatorias automáticas de stock para Adultos e Niños en el panel superior.