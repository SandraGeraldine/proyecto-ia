from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

class InnovVentasBot:
    """
    Chatbot simplificado para E-commerce InnovVentas
    Utiliza Azure Language Service para análisis de sentimientos
    """
    
    def __init__(self):
        self.language_key = os.getenv('LANGUAGE_KEY')
        self.language_endpoint = os.getenv('LANGUAGE_ENDPOINT')
        
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analiza el sentimiento del texto usando Azure Language Service
        """
        try:
            credential = AzureKeyCredential(self.language_key)
            client = TextAnalyticsClient(
                endpoint=self.language_endpoint, 
                credential=credential
            )
            
            response = client.analyze_sentiment(
                documents=[text],
                language="es"
            )
            
            if response and not response[0].is_error:
                doc = response[0]
                return {
                    'sentiment': doc.sentiment,
                    'confidence_scores': {
                        'positive': doc.confidence_scores.positive,
                        'neutral': doc.confidence_scores.neutral,
                        'negative': doc.confidence_scores.negative
                    }
                }
            
            return {'error': 'No se pudo analizar el sentimiento'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def detect_intent(self, text: str) -> str:
        """
        Detección simple de intención basada en palabras clave
        """
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['especificaciones', 'características', 'precio', 'producto']):
            return 'producto'
        elif any(word in text_lower for word in ['disponible', 'hay', 'stock', 'inventario']):
            return 'stock'
        elif any(word in text_lower for word in ['pagar', 'tarjeta', 'cuotas', 'transferencia']):
            return 'pago'
        elif any(word in text_lower for word in ['comprar', 'carrito', 'pedido', 'orden']):
            return 'compra'
        elif any(word in text_lower for word in ['ayuda', 'problema', 'error', 'soporte']):
            return 'soporte'
            
        return 'general'
    
    def generate_response(self, message: str) -> Dict[str, Any]:
        """
        Procesa el mensaje y genera una respuesta
        """
        # Analizar sentimiento
        sentiment = self.analyze_sentiment(message)
        
        # Detectar intención
        intent = self.detect_intent(message)
        
        # Generar respuesta según intención
        responses = {
            'producto': "Te puedo ayudar con información sobre nuestros productos. ¿Qué te gustaría saber?",
            'stock': "Puedo verificar la disponibilidad. ¿Qué producto te interesa?",
            'pago': "Aceptamos tarjeta, transferencia y efectivo. ¿Cómo prefieres pagar?",
            'compra': "¡Excelente elección! ¿Qué producto quieres agregar a tu carrito?",
            'soporte': "Lamento los inconvenientes. ¿En qué puedo ayudarte hoy?",
            'general': "¿En qué puedo ayudarte hoy? Estoy aquí para asistirte."
        }
        
        response = responses.get(intent, responses['general'])
        
        # Ajustar según sentimiento
        if 'error' not in sentiment and sentiment.get('sentiment') == 'negative':
            response = "Lamento que estés teniendo dificultades. " + response
        
        return {
            'success': 'error' not in sentiment,
            'response': response,
            'intent': intent,
            'sentiment': sentiment
        }

# Instancia global del bot
bot = InnovVentasBot()
