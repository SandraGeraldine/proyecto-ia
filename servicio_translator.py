from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
import os
from pathlib import Path
from dotenv import load_dotenv

# Obtener la ruta absoluta del directorio actual
current_dir = Path(__file__).parent.absolute()
dotenv_path = current_dir / '.env'

# Cargar variables de entorno
load_dotenv(dotenv_path=dotenv_path, override=True)

# Mensajes de depuración
print("\n=== servicio_translator.py ===")
print(f"Directorio actual: {current_dir}")
print(f"Ruta del archivo .env: {dotenv_path}")
print(f"¿Existe .env? {dotenv_path.exists()}")
print(f"TRANSLATOR_KEY: {'Configurada' if os.getenv('TRANSLATOR_KEY') else 'No configurada'}")
print(f"TRANSLATOR_ENDPOINT: {'Configurado' if os.getenv('TRANSLATOR_ENDPOINT') else 'No configurado'}")
print(f"TRANSLATOR_REGION: {'Configurada' if os.getenv('TRANSLATOR_REGION') else 'No configurada'}")

def get_translation_client():
    """Crea y retorna un cliente de Azure Translator"""
    key = os.getenv('TRANSLATOR_KEY')
    endpoint = os.getenv('TRANSLATOR_ENDPOINT')
    
    if not key or not endpoint:
        raise ValueError("Las credenciales de Azure Translator no están configuradas correctamente.")
    
    credential = AzureKeyCredential(key)
    return TextTranslationClient(endpoint=endpoint, credential=credential)

def traducir_texto(texto, idioma_destino="en"):
    """
    Traduce un texto al idioma especificado usando Azure Translator.
    
    Args:
        texto (str): Texto a traducir
        idioma_destino (str): Código de idioma de destino (por defecto: "en")
        
    Returns:
        str: Texto traducido o mensaje de error
    """
    try:
        # Validar entrada
        if not texto or not isinstance(texto, str) or not texto.strip():
            return ""

        # Obtener cliente de traducción
        client = get_translation_client()
        
        # Realizar la traducción
        response = client.translate(
            content=[texto],
            to=[idioma_destino]
        )
        
        # Procesar la respuesta
        if response and len(response) > 0 and hasattr(response[0], 'translations'):
            return response[0].translations[0].text
        else:
            return "No se pudo obtener la traducción. Respuesta inesperada del servicio."
            
    except Exception as e:
        print(f"Error en la traducción: {str(e)}")
        return f"Error al traducir el texto: {str(e)}"
