# Flotilla Control 🚢

Sistema de control de flotilla de vehículos de escritorio desarrollado en Python utilizando **CustomTkinter** para la interfaz de usuario moderna, **SQLite** para el almacenamiento de datos persistente, y **PyInstaller** para la compilación y empaquetado como aplicación independiente.

## Estructura del Proyecto

*   `main.py`: Punto de entrada del programa. Inicializa la base de datos y lanza la interfaz gráfica.
*   `gui.py`: Definición y diseño de la interfaz gráfica adaptativa (Dashboard, sección de Vehículos, y sección de Mantenimientos).
*   `database.py`: Manejador de la base de datos SQLite. Contiene el esquema de tablas y operaciones CRUD completas.
*   `build.py`: Script para automatizar la compilación a ejecutable usando PyInstaller.
*   `requirements.txt`: Lista de dependencias de Python necesarias.

## Requisitos Previos

Asegúrate de tener instalado Python 3.8 o superior en tu sistema.

### En Linux (Debian/Ubuntu y derivados):
Tkinter es parte de la biblioteca estándar de Python, pero en algunas distribuciones de Linux es necesario instalarlo explícitamente:
```bash
sudo apt-get install python3-tk
```

## Configuración y Ejecución Directa

1.  Crea y activa un entorno virtual (opcional pero recomendado):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

3.  Ejecuta la aplicación:
    ```bash
    python3 main.py
    ```

La base de datos SQLite (`fleet_management.db`) se creará automáticamente en la primera ejecución con algunos datos de ejemplo iniciales (vehículos y mantenimientos) para que puedas ver el dashboard poblado de inmediato.

## Generación del Ejecutable con PyInstaller

Para empaquetar toda la aplicación en un único archivo ejecutable de escritorio que no requiera Python para ejecutarse:

1.  Ejecuta el script de compilación provisto:
    ```bash
    python3 build.py
    ```

Este script:
-   Verificará e instalará cualquier dependencia faltante de `requirements.txt`.
-   Ejecutará PyInstaller con los parámetros necesarios (`--onefile`, `--noconsole`, `--collect-all customtkinter`).
-   Generará el ejecutable final en la carpeta `dist/FlotillaControl` (o `dist/FlotillaControl.exe` en Windows).

---
*Desarrollado con CustomTkinter, SQLite3 y PyInstaller.*
