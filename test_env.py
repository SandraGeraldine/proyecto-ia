from dotenv import load_dotenv
import os
from pathlib import Path

print("=== Información del sistema ===")
print(f"Directorio de trabajo actual: {os.getcwd()}")
print(f"Directorio del script: {Path(__file__).parent.absolute()}")

# Intentar cargar el archivo .env de varias formas
dotenv_paths = [
    Path(__file__).parent.absolute() / '.env',  # Mismo directorio que el script
    Path.cwd() / '.env',  # Directorio de trabajo actual
    Path.home() / '.env',  # Directorio home del usuario
]

loaded = False
for path in dotenv_paths:
    print(f"\nIntentando cargar: {path}")
    if path.exists():
        print(f"Archivo .env encontrado en: {path}")
        load_dotenv(path, override=True)
        loaded = True
        break
    else:
        print(f"No se encontró el archivo en: {path}")

if not loaded:
    print("\n⚠️ No se pudo encontrar el archivo .env en ninguna ubicación estándar")
    print("Intentando cargar sin especificar ruta...")
    load_dotenv()  # Último intento sin ruta específica

# Verificar variables de entorno
print("\n=== Variables de entorno ===")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'No configurado')}")
print(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'No configurado')}")

# Variables específicas de la aplicación
variables = [
    'TEXT_ANALYTICS_KEY',
    'TEXT_ANALYTICS_ENDPOINT',
    'VISION_KEY',
    'VISION_ENDPOINT',
    'TRANSLATOR_KEY',
    'TRANSLATOR_ENDPOINT',
    'TRANSLATOR_REGION'
]

print("\n=== Estado de las variables de entorno ===")
for var in variables:
    value = os.getenv(var)
    if value:
        # Mostrar solo los primeros 5 caracteres de las claves por seguridad
        display_value = f"{value[:5]}..." if var.endswith('_KEY') else value
        print(f"✅ {var}: {display_value}")
    else:
        print(f"❌ {var}: No configurada")

# Mostrar todas las variables de entorno (filtradas para no mostrar información sensible)
print("\n=== Variables de entorno del sistema ===")
for key, value in os.environ.items():
    if any(key.startswith(prefix) for prefix in ['TEXT_', 'VISION_', 'TRANSLATOR_', 'PYTHON', 'VIRTUAL']):
        # Ocultar valores de claves sensibles
        display_value = f"{value[:5]}..." if key.endswith(('_KEY', '_SECRET', '_PASSWORD')) else value
        print(f"{key}: {display_value}")

# Verificar si el archivo .env existe y su contenido
env_file = Path(__file__).parent.absolute() / '.env'
if env_file.exists():
    print(f"\n=== Contenido de {env_file} ===")
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Ocultar valores de claves sensibles
                if '=' in line and any(key in line for key in ['_KEY=', '_SECRET=', '_PASSWORD=']):
                    key, value = line.split('=', 1)
                    print(f"{key}=[PROTECTED]")
                else:
                    print(line.strip())
    except Exception as e:
        print(f"Error al leer el archivo .env: {e}")