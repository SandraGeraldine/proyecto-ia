# === SERVICIO 3: COMPUTER VISION ===
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Union, BinaryIO

# Obtener la ruta absoluta del directorio actual
current_dir = Path(__file__).parent.absolute()
dotenv_path = current_dir / '.env'

# Cargar variables de entorno
load_dotenv(dotenv_path=dotenv_path, override=True)

# Mensajes de depuración
print("\n=== servicio_vision.py ===")
print(f"Directorio actual: {current_dir}")
print(f"Ruta del archivo .env: {dotenv_path}")
print(f"¿Existe .env? {dotenv_path.exists()}")
print(f"VISION_KEY: {'Configurada' if os.getenv('VISION_KEY') else 'No configurada'}")
print(f"VISION_ENDPOINT: {'Configurado' if os.getenv('VISION_ENDPOINT') else 'No configurado'}")

def conectar_vision():
    """
    Conecta al servicio de Azure Computer Vision.
    
    Returns:
        ComputerVisionClient: Cliente de Azure Computer Vision
    """
    key = os.getenv('VISION_KEY')
    endpoint = os.getenv('VISION_ENDPOINT')
    
    if not key or not endpoint:
        raise ValueError("VISION_KEY o VISION_ENDPOINT no están configurados")
    
    return ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

def describir_imagen(imagen: Union[str, BinaryIO]):
    """
    Describe una imagen utilizando Azure Computer Vision.
    
    Args:
        imagen: Puede ser una ruta de archivo local, un objeto de archivo o bytes
        
    Returns:
        str: Descripción de la imagen o mensaje de error
    """
    try:
        if not imagen:
            return "No se proporcionó una imagen válida"
            
        cliente = conectar_vision()
        
        # Si es un string, asumimos que es una ruta de archivo
        if isinstance(imagen, str):
            if os.path.isfile(imagen):
                # Es un archivo local
                with open(imagen, 'rb') as img:
                    imagen_bytes = img.read()
            else:
                # Es una URL
                return "El análisis por URL no está soportado actualmente. Por favor, sube un archivo de imagen."
        # Si es un objeto de archivo o similar
        elif hasattr(imagen, 'read'):
            if hasattr(imagen, 'seek'):
                imagen.seek(0)  # Asegurarse de que estamos al inicio del archivo
            imagen_bytes = imagen.read()
        else:
            return "Tipo de imagen no soportado"
        
        # Analizar la imagen desde bytes
        resultado = cliente.describe_image_in_stream(
            image=imagen_bytes,
            max_candidates=1,  # Número de descripciones a devolver
            language="es"      # Idioma de la descripción
        )
        
        # Obtener la mejor descripción
        if resultado.captions and len(resultado.captions) > 0:
            return resultado.captions[0].text
        else:
            return "No se pudo generar una descripción para la imagen"
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error al analizar la imagen: {str(e)}"
