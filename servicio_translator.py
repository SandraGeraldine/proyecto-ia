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

def conectar_translator():
    """
    Conecta al servicio de Azure Translator.
    
    Returns:
        TextTranslationClient: Cliente de Azure Translator
    """
    key = os.getenv('TRANSLATOR_KEY')
    endpoint = os.getenv('TRANSLATOR_ENDPOINT')
    region = os.getenv('TRANSLATOR_REGION', 'southcentralus')
    
    if not key or not endpoint:
        raise ValueError("TRANSLATOR_KEY o TRANSLATOR_ENDPOINT no están configuradas en las variables de entorno")
    
    credential = AzureKeyCredential(key)
    return TextTranslationClient(credential=credential, endpoint=endpoint, region=region)

def traducir_texto(texto, idioma_destino="en"):
    """
    Traduce un texto al idioma especificado.
    
    Args:
        texto (str): Texto a traducir
        idioma_destino (str): Código de idioma de destino (por defecto: "en")
        
    Returns:
        str: Texto traducido
    """
    try:
        if not texto or not isinstance(texto, str) or not texto.strip():
            return ""
            
        client = conectar_translator()
        
        # Traducir texto (el SDK manejará la detección automática del idioma)
        response = client.translate(
            body=[{"text": texto}],
            to=[idioma_destino]
        )
        
        if response and len(response) > 0 and len(response[0].translations) > 0:
            return response[0].translations[0].text
        else:
            return "No se pudo traducir el texto"
            
    except Exception as e:
        print(f"Error en la traducción: {str(e)}")
        return f"Error al traducir: {str(e)}"
