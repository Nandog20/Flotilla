import os
import sys
import subprocess

def check_and_install_dependencies():
    print("Verificando dependencias...")
    try:
        import customtkinter
        import PyInstaller
        print("Dependencias ya instaladas.")
    except ImportError:
        print("Instalando dependencias desde requirements.txt...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("Dependencias instaladas con éxito.")
        except Exception as e:
            print(f"Error al instalar dependencias de Python: {e}")
            print("Por favor, asegúrate de tener pip instalado y conexión a internet.")
            sys.exit(1)

def run_build():
    print("Iniciando compilación con PyInstaller...")
    try:
        import PyInstaller.__main__
    except ImportError:
        print("Error: PyInstaller no está disponible para compilar.")
        sys.exit(1)

    # Parámetros de PyInstaller:
    # - main.py: Script de entrada.
    # - --onefile: Empaqueta todo en un solo archivo ejecutable.
    # - --noconsole: Oculta la terminal detrás de la GUI al ejecutarse.
    # - --collect-all customtkinter: Copia recursos, archivos JSON de temas y binarios de customtkinter.
    # - --name FlotillaControl: Nombre del archivo de salida.
    # - --clean: Limpia la caché de PyInstaller antes de compilar.
    args = [
        'main.py',
        '--onefile',
        '--noconsole',
        '--collect-all', 'customtkinter',
        '--name', 'FlotillaControl',
        '--clean'
    ]
    
    print(f"Ejecutando PyInstaller con argumentos: {' '.join(args)}")
    try:
        PyInstaller.__main__.run(args)
        print("\n=======================================================")
        print("¡Compilación finalizada con éxito!")
        print("El archivo ejecutable se encuentra en la carpeta 'dist/'.")
        print("=======================================================")
    except Exception as e:
        print(f"Ocurrió un error durante la compilación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_and_install_dependencies()
    run_build()
