from botbuilder.core import BotFrameworkAdapter, TurnContext
from botbuilder.schema import Activity
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()

class InnovVentasBot:
    """
    Chatbot para E-commerce InnovVentas
    Integra Text Analytics, Translator y lógica de negocio
    """
    
    def __init__(self):
        self.luis_app_id = os.getenv('LUIS_APP_ID')
        self.luis_key = os.getenv('LUIS_KEY')
        self.luis_endpoint = os.getenv('LUIS_ENDPOINT')
        
    async def on_message_activity(self, turn_context: TurnContext) -> Dict[str, Any]:
        """
        Procesa mensajes del usuario y devuelve una respuesta
        """
        user_message = turn_context.activity.text
        
        # 1. Analizar sentimiento del mensaje
        from servicio_language import analizar_sentimiento
        sentiment = analizar_sentimiento(user_message)
        
        # 2. Detectar intención
        intent = await self.detect_intent(user_message)
        
        # 3. Generar respuesta
        response = await self.generate_response(intent, user_message, sentiment)
        
        return {
            'success': True,
            'response': response,
            'intent': intent,
            'sentiment': sentiment
        }
        
    async def detect_intent(self, text: str) -> str:
        """
        Detecta la intención del usuario
        """
        intents = {
            'producto': ['especificaciones', 'características', 'precio', 'producto'],
            'stock': ['disponible', 'hay', 'stock', 'inventario', 'quedan'],
            'pago': ['pagar', 'tarjeta', 'cuotas', 'transferencia', 'pago'],
            'compra': ['comprar', 'carrito', 'pedido', 'orden'],
            'soporte': ['ayuda', 'problema', 'error', 'soporte']
        }
        
        text_lower = text.lower()
        for intent, keywords in intents.items():
            if any(keyword in text_lower for keyword in keywords):
                return intent
        
        return 'general'
    
    async def generate_response(self, intent: str, message: str, sentiment: Dict[str, Any]) -> str:
        """
        Genera respuesta personalizada según intención
        """
        responses = {
            'producto': "Te puedo ayudar con información sobre nuestros productos. ¿Qué te gustaría saber? Puedo darte especificaciones técnicas, precios o hacer comparaciones.",
            'stock': "Déjame verificar la disponibilidad en tiempo real. ¿Qué producto te interesa?",
            'pago': "Aceptamos múltiples métodos de pago: tarjeta de crédito/débito, transferencia bancaria y efectivo. ¿Cuál prefieres?",
            'compra': "¡Excelente elección! Por favor, indícame qué producto deseas agregar a tu carrito.",
            'soporte': "Lamento los inconvenientes. Por favor, describe el problema que estás experimentando y con gusto te ayudaré.",
            'general': "¿En qué más puedo ayudarte hoy? Estoy aquí para asistirte con información de productos, compras y soporte técnico."
        }
        
        # Ajustar respuesta según el sentimiento
        if sentiment['sentiment'] == 'negative':
            return "Lamento que estés teniendo dificultades. " + responses[intent] if intent in responses else responses['general']
        
        return responses.get(intent, responses['general'])

# Instancia global del bot
bot = InnovVentasBot()
