from typing import Dict, Any, Optional
import os
import random
from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

class InnovVentasBot:
    """
    Chatbot para E-commerce InnovVentas
    Utiliza Azure Language Service para análisis de sentimientos
    y respuestas predefinidas para preguntas frecuentes
    """
    
    def __init__(self):
        self.language_key = os.getenv('LANGUAGE_KEY')
        self.language_endpoint = os.getenv('LANGUAGE_ENDPOINT')
        self._welcome_shown = False
        
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
            
            return {'sentiment': 'neutral'}
            
        except Exception as e:
            print(f"Error en análisis de sentimiento: {str(e)}")
            return {'sentiment': 'neutral'}
    
    def generate_response(self, message: str) -> Dict[str, Any]:
        """
        Genera una respuesta basada en el mensaje del usuario
        """
        # Convertir el mensaje a minúsculas para facilitar la comparación
        message_lower = message.lower()
        
        # Si es el primer mensaje, mostrar el mensaje de bienvenida
        if not self._welcome_shown:
            self._welcome_shown = True
            return self._get_welcome_message()
            
        # Análisis de sentimiento
        sentiment = self.analyze_sentiment(message)
        
        # Diccionario de preguntas y respuestas frecuentes
        faqs = {
            # Saludos
            'hola': '¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?',
            'buenos días': '¡Buenos días! ¿Cómo puedo ayudarte hoy?',
            'buenas tardes': '¡Buenas tardes! ¿En qué puedo asistirte?',
            'buenas noches': '¡Buenas noches! ¿En qué te puedo ayudar?',
            
            # Preguntas generales
            'quién eres': 'Soy un asistente virtual diseñado para ayudarte con tus consultas. Estoy aquí para hacerte la vida más fácil.',
            'qué puedes hacer': 'Puedo ayudarte con información sobre productos, seguimiento de pedidos, asistencia técnica y más. ¿En qué necesitas ayuda?',
            'ayuda': '¡Claro! Estoy aquí para ayudarte. ¿Necesitas información sobre productos, seguimiento de pedidos o asistencia técnica?',
            
            # Información de contacto
            'contacto': '📧 Email: contacto@innovventas.com\n📞 Teléfono: +1 234 567 890\n🏢 Dirección: Av. Principal 123, Ciudad',
            'horario': '⏰ Horario de atención:\nLunes a Viernes: 9:00 AM - 6:00 PM\nSábados: 9:00 AM - 1:00 PM',
            
            # Productos y servicios
            'productos': 'Ofrecemos una amplia gama de productos. ¿Te gustaría saber sobre electrónicos, electrodomésticos o tecnología?',
            'servicios': 'Nuestros servicios incluyen envíos a domicilio, garantía extendida y soporte técnico. ¿Sobre cuál necesitas información?',
            
            # Agradecimientos
            'gracias': '¡De nada! 😊 ¿Hay algo más en lo que pueda ayudarte hoy?',
            
            # Despedidas
            'adiós': '¡Hasta luego! Que tengas un excelente día. 😊',
            'hasta luego': '¡Hasta pronto! Si tienes más preguntas, aquí estaré para ayudarte.',
            
            # Estado de pedidos
            'seguimiento': 'Para dar seguimiento a tu pedido, necesitaré el número de orden. ¿Lo tienes a la mano?',
            'pedido': 'Para ayudarte con tu pedido, necesitaré el número de orden. También puedo ayudarte a realizar un nuevo pedido si lo deseas.',
            
            # Devoluciones y garantías
            'devolución': 'Nuestra política de devoluciones permite devoluciones hasta 30 días después de la compra. ¿Necesitas ayuda para iniciar una devolución?',
            'garantía': 'La mayoría de nuestros productos tienen una garantía de 1 año. ¿Podrías indicarme el producto sobre el que necesitas información de garantía?',
            
            # Formas de pago
            'pago': 'Aceptamos diferentes métodos de pago: tarjetas de crédito/débito, transferencias bancarias y billeteras digitales. ¿Neitas ayuda con algún método en particular?',
            
            # Envíos
            'envío': 'Realizamos envíos a todo el país. El tiempo y costo de envío varían según la ubicación. ¿Podrías indicarme tu código postal?',
            
            # Ofertas
            'oferta': '¡Claro! Actualmente tenemos promociones especiales. ¿Te interesa alguna categoría en particular?',
            
            # Soporte técnico
            'soporte': 'Para asistencia técnica, por favor describe el problema que estás experimentando y con gusto te ayudaré a resolverlo.',
            'problema': 'Lamento escuchar que tienes un problema. Por favor, cuéntame más detalles para poder ayudarte mejor.'
        }
        
        # Buscar coincidencias en las preguntas frecuentes
        for pregunta, respuesta in faqs.items():
            if pregunta in message_lower:
                return {
                    'success': True,
                    'response': respuesta,
                    'intent': 'faq',
                    'sentiment': sentiment
                }
        
        # Si no hay coincidencia, usar la lógica de análisis de sentimiento
        if sentiment.get('sentiment') == 'positive':
            return {
                'success': True,
                'response': '¡Me alegra que estés teniendo una buena experiencia! ¿Hay algo más en lo que pueda ayudarte hoy?',
                'intent': 'positive_feedback',
                'sentiment': sentiment
            }
        elif sentiment.get('sentiment') == 'negative':
            return {
                'success': True,
                'response': 'Lamento escuchar que no estás satisfecho. Por favor, cuéntame más sobre el problema para poder ayudarte mejor.',
                'intent': 'negative_feedback',
                'sentiment': sentiment
            }
        
        # Respuesta por defecto
        default_responses = [
            '¿Podrías darme más detalles sobre lo que necesitas?',
            'No estoy seguro de entender. ¿Podrías reformular tu pregunta?',
            '¿Te gustaría que te ayude con información sobre productos, seguimiento de pedidos o asistencia técnica?',
            '¿En qué más puedo ayudarte hoy?'
        ]
        
        return {
            'success': True,
            'response': random.choice(default_responses),
            'intent': 'general_inquiry',
            'sentiment': sentiment,
            'suggestions': [
                '¿Cómo hago un pedido?',
                '¿Cuál es el estado de mi envío?',
                '¿Tienen este producto en stock?',
                '¿Cuáles son las formas de pago?'
            ]
        }
    
    def _get_welcome_message(self) -> Dict[str, Any]:
        """
        Devuelve el mensaje de bienvenida con sugerencias
        """
        welcome_message = """
¡Hola! 👋 Soy tu asistente virtual de InnovVentas. Estoy aquí para ayudarte con:

📦 **Seguimiento de pedidos**
💳 **Información de productos**
❓ **Preguntas frecuentes**
🛒 **Asistencia en compras**

Por ejemplo, puedes preguntarme:
• "¿Cómo hago un pedido?"
• "¿Cuál es el estado de mi envío?"
• "¿Tienen este producto en stock?"
• "¿Cuáles son las formas de pago?"

¿En qué puedo ayudarte hoy?
"""
        
        return {
            'success': True,
            'response': welcome_message,
            'intent': 'welcome',
            'suggestions': [
                '¿Cómo hago un pedido?',
                '¿Cuál es el estado de mi envío?',
                '¿Tienen este producto en stock?',
                '¿Cuáles son las formas de pago?'
            ]
        }

# Instancia global del bot
bot = InnovVentasBot()
