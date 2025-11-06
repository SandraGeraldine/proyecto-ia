import os
from dotenv import load_dotenv
from servicio_language import analizar_sentimiento
from servicio_translator import traducir_texto
from servicio_vision import describir_imagen

load_dotenv()

def test_servicios():
    print("=== Probando Servicios de Azure ===")
    
    # Probar Text Analytics
    try:
        print("\n1. Probando Text Analytics...")
        resultado = analizar_sentimiento("Me encanta este producto, es increíble!")
        print("✅ Text Analytics funcionando correctamente")
        print(f"Resultado: {resultado}")
    except Exception as e:
        print(f"❌ Error en Text Analytics: {str(e)}")
    
    
    # Probar Translator
    try:
        print("\n2. Probando Translator...")
        traduccion = traducir_texto("Hola, ¿cómo estás?", "en")
        print("✅ Translator funcionando correctamente")
        print(f"Traducción: {traduccion}")
    except Exception as e:
        print(f"❌ Error en Translator: {str(e)}")
    
    # Probar Computer Vision (necesita una URL de imagen)
    try:
        print("\n3. Probando Computer Vision...")
        # Usa una URL de imagen pública para pruebas
        url_imagen = "https://learn.microsoft.com/es-es/azure/ai-services/computer-vision/media/quickstarts/presentation.png"
        descripcion = describir_imagen(url_imagen)
        print("✅ Computer Vision funcionando correctamente")
        print(f"Descripción: {descripcion}")
    except Exception as e:
        print(f"❌ Error en Computer Vision: {str(e)}")

if __name__ == "__main__":
    test_servicios()