# ClientesApp

Aplicación de escritorio en Python (Tkinter + tkcalendar) para gestionar clientes (apellido, nombre, descripción, teléfono, fechas). La base de datos es SQLite (`clientes.db`) y la app copia la plantilla incluida al directorio de datos del usuario en el primer arranque (p. ej. `%LOCALAPPDATA%\ClientesApp\clientes.db` en Windows, `~/.local/share/ClientesApp/clientes.db` en Linux).

## Requisitos
- Python 3.10+ (probado con 3.12)
- Dependencias Python (ver `requirements.txt`)
- Sistema:
  - Linux (Ubuntu/Debian): instalar `python3-tk`
  - macOS: instalar Python con soporte para Tk (recomendado desde python.org o instalar `tcl-tk` vía Homebrew)
  - Windows: instalar Python desde python.org (Tk viene normalmente incluido)

## Entorno virtual e instalación (Linux / macOS / Windows)
1. Crear y activar entorno virtual:
   - Linux / macOS
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Windows (PowerShell)
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar:
   ```bash
   python -m app.main
   ```
   (El `main.py` ya llama a `init_db()` para crear la BD si hace falta.)

## Empaquetado con PyInstaller
- Nota: PyInstaller debe ejecutarse en la misma plataforma de destino para obtener ejecutables nativos (ej. generar .exe en Windows desde Windows).

Ejemplos de línea de comando:

- Windows (en cmd/PowerShell) — usar .ico:
```powershell
pyinstaller --onefile --windowed --icon=assets\imagen.ico --add-data "database\clientes.db;database" app\main.py
```

- macOS — usar .icns (para .app):
```bash
pyinstaller --onefile --windowed --icon=assets/icon.icns --add-data "database/clientes.db:database" app/main.py
# Para bundle .app puedes usar --windowed y luego crear el .app con --onedir si prefieres
```

- Linux:
```bash
pyinstaller --onefile --windowed --name ClientesApp --icon=assets/imagen.png --add-data "database/clientes.db:database" app/main.py
```

Si usas `--onefile`, los archivos añadidos se extraen a un directorio temporal en ejecución; por eso el código copia la plantilla incluida al directorio de datos del usuario en el primer arranque (para que la base sea escribible).

## Icono / assets
- Crea la carpeta `assets/` en la raíz y guarda el icono allí.
- Extensiones recomendadas por plataforma:
  - Windows: `.ico` (recomendado incluir varias resoluciones: 16x16, 32x32, 48x48, 256x256)
  - macOS: `.icns`
  - Linux: `.png` (256x256 o 512x512)
- Puedes generar un `.ico` con ImageMagick:
  ```bash
  convert icon.png -resize 256x256 icon.ico
  ```
  (o usar un conversor que incluya múltiples tamaños en el `.ico`)

## Ubicación de la base de datos
- La app usa una ruta por usuario (no escribe dentro del ejecutable ni en Program Files). Ejemplos:
  - Windows: `%LOCALAPPDATA%\ClientesApp\clientes.db`
  - Linux: `~/.local/share/ClientesApp/clientes.db`
  - macOS: `~/Library/Application Support/ClientesApp/clientes.db`

## Notas finales
- Para generar .exe de Windows desde Linux usa CI (GitHub Actions) o una máquina Windows; PyInstaller no cross-compila de forma fiable.
- Llama a `init_db()` en el arranque (ya lo hace `app/main.py`) para crear tablas si no existen.
- Si necesitás, preparo un workflow de GitHub Actions para builds multiplataforma.