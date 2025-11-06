from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Importar los servicios
import requests
from servicio_language import analizar_sentimiento, conectar_language
from servicio_translator import traducir_texto
from servicio_vision import describir_imagen
from servicio_bot import bot as chat_bot

# Obtener la ruta absoluta del directorio actual
current_dir = Path(__file__).parent.absolute()
dotenv_path = current_dir / '.env'

# Cargar variables de entorno
load_dotenv(dotenv_path=dotenv_path, override=True)

# Mensajes de depuración
print(f"\n=== main.py ===")
print(f"Directorio actual: {current_dir}")
print(f"Ruta del archivo .env: {dotenv_path}")
print(f"¿Existe .env? {dotenv_path.exists()}")
print(f"LANGUAGE_KEY: {'Configurada' if os.getenv('LANGUAGE_KEY') else 'No configurada'}")
print(f"LANGUAGE_ENDPOINT: {'Configurado' if os.getenv('LANGUAGE_ENDPOINT') else 'No configurado'}")
print(f"VISION_KEY: {'Configurada' if os.getenv('VISION_KEY') else 'No configurada'}")
print(f"VISION_ENDPOINT: {'Configurado' if os.getenv('VISION_ENDPOINT') else 'No configurado'}")
print(f"TRANSLATOR_KEY: {'Configurada' if os.getenv('TRANSLATOR_KEY') else 'No configurada'}")
print(f"TRANSLATOR_ENDPOINT: {'Configurado' if os.getenv('TRANSLATOR_ENDPOINT') else 'No configurado'}")
print(f"TRANSLATOR_REGION: {'Configurada' if os.getenv('TRANSLATOR_REGION') else 'No configurada'}")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max-limit

# Crear carpeta de subidas si no existe
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print(f"✓ Carpeta de subidas: {app.config['UPLOAD_FOLDER']}")
except Exception as e:
    print(f"✗ Error al crear carpeta de subidas: {str(e)}")
    raise

# 1. Servicio de Análisis de Sentimiento
@app.route('/api/analizar-sentimiento', methods=['POST'])
def analizar_sentimiento_endpoint():
    try:
        datos = request.get_json()
        texto = datos.get('texto', '')
        
        if not texto:
            return jsonify({'error': 'No se proporcionó texto'}), 400

        resultado = analizar_sentimiento(texto)
        return jsonify({
            'estado': 'éxito',
            'resultado': resultado
        })

    except Exception as e:
        return jsonify({
            'estado': 'error',
            'mensaje': str(e)
        }), 500

# 2. Servicio de Traducción
@app.route('/api/traducir', methods=['POST'])
def traducir():
    try:
        datos = request.get_json()
        texto = datos.get('texto', '')
        idioma_destino = datos.get('idioma', 'en')  # Por defecto a inglés
        
        if not texto:
            return jsonify({'error': 'No se proporcionó texto para traducir'}), 400

        resultado = traducir_texto(texto, idioma_destino)
        return jsonify({
            'estado': 'éxito',
            'traduccion': resultado
        })

    except Exception as e:
        return jsonify({
            'estado': 'error',
            'mensaje': str(e)
        }), 500

# 3. Servicio de Análisis de Imágenes
@app.route('/api/analizar-imagen', methods=['POST'])
def analizar_imagen():
    filepath = None
    try:
        print("\n=== Inicio de análisis de imagen ===")
        print(f"Archivos recibidos: {request.files}")
        
        if 'imagen' not in request.files:
            print("Error: No se encontró el campo 'imagen' en la solicitud")
            return jsonify({
                'estado': 'error',
                'mensaje': 'No se proporcionó ninguna imagen o el campo no se llama \'imagen\''
            }), 400
        
        archivo = request.files['imagen']
        print(f"Archivo recibido: {archivo.filename} (tipo: {archivo.content_type})")
        
        if archivo.filename == '':
            print("Error: Nombre de archivo vacío")
            return jsonify({
                'estado': 'error',
                'mensaje': 'No se seleccionó ningún archivo'
            }), 400
        
        # Asegurar que el nombre del archivo sea seguro
        filename = secure_filename(archivo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        print(f"Guardando archivo temporal en: {filepath}")
        archivo.save(filepath)
        
        # Verificar que el archivo se haya guardado correctamente
        if not os.path.exists(filepath):
            raise Exception("No se pudo guardar el archivo temporal")
            
        print("Archivo guardado correctamente, analizando...")
        
        # Analizar imagen (pasamos el archivo directamente)
        archivo.seek(0)  # Asegurarse de que estamos al inicio del archivo
        descripcion = describir_imagen(archivo)
        
        print(f"Análisis completado: {descripcion[:100]}...")
        
        return jsonify({
            'estado': 'éxito',
            'descripcion': descripcion,
            'nombre_archivo': filename
        })
        
    except Exception as e:
        print(f"Error en analizar_imagen: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'estado': 'error',
            'mensaje': f'Error al procesar la imagen: {str(e)}',
            'tipo_error': str(type(e).__name__)
        }), 500
        
    finally:
        # Limpieza: eliminar archivo temporal si existe
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Archivo temporal eliminado: {filepath}")
            except Exception as e:
                print(f"Error al eliminar archivo temporal: {e}")

# Ruta principal que sirve la interfaz web
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint para obtener token de Direct Line
@app.route('/api/directline/token', methods=['GET', 'POST'])
def generate_directline_token():
    """
    Genera un token de Direct Line para la conexión con el bot.
    
    Returns:
        JSON con el token de conexión o un mensaje de error detallado.
    """
    try:
        print("\n=== Iniciando generación de token Direct Line ===")
        
        # 1. Validar la clave secreta
        DIRECT_LINE_SECRET = os.getenv('DIRECT_LINE_SECRET')
        if not DIRECT_LINE_SECRET:
            error_msg = 'No se encontró la clave secreta de Direct Line en las variables de entorno'
            print(f"Error: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg,
                'hint': 'Verifica que la variable DIRECT_LINE_SECRET esté configurada en Azure App Service',
                'solution': '1. Ve a Azure Portal > App Service > Configuración > Configuración de la aplicación\n' +
                           '2. Agrega una nueva configuración con nombre DIRECT_LINE_SECRET\n' +
                           '3. Usa el valor de la clave secreta de tu canal Direct Line'
            }), 500

        # 2. Validar formato de la clave
        if not DIRECT_LINE_SECRET.startswith('DLSECRET_'):
            print(f"Advertencia: La clave no tiene el formato esperado. Valor: {DIRECT_LINE_SECRET[:10]}...")

        # 3. Configurar headers con validación
        headers = {
            'Authorization': f'Bearer {DIRECT_LINE_SECRET}',
            'Content-Type': 'application/json'
        }
        
        # 4. Configurar datos con origen confiable
        data = {
            'user': {
                'id': f"user_{os.urandom(8).hex()}"
            },
            'trustedOrigins': [
                'https://sandra-servicio-akenaacucyavbug9.brazilsouth-01.azurewebsites.net',
                'http://localhost:8000',  # Para pruebas locales
                'http://localhost:5000'   # Puerto alternativo para pruebas
            ]
        }

        # 5. Configurar URL y timeout
        url = 'https://directline.botframework.com/v3/directline/tokens/generate'
        
        # 6. Log de depuración (sin exponer la clave secreta)
        debug_info = {
            'url': url,
            'headers': {k: '***' if k == 'Authorization' else v for k, v in headers.items()},
            'data': data,
            'direct_line_secret_length': len(DIRECT_LINE_SECRET),
            'direct_line_secret_prefix': DIRECT_LINE_SECRET[:10] + '...' if DIRECT_LINE_SECRET else None
        }
        print(f"\n=== Debug Info ===\n{json.dumps(debug_info, indent=2)}\n")

        # 7. Hacer la petición con timeout
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=15  # Aumentado a 15 segundos
        )
        
        # 8. Manejar respuesta
        print(f"Respuesta de Direct Line - Estado: {response.status_code}")
        response.raise_for_status()
        
        result = response.json()
        
        if not result.get('token'):
            error_msg = 'La respuesta no contiene un token válido'
            print(f"Error: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg,
                'response': result,
                'hint': 'Verifica que el bot esté publicado y que la clave secreta sea correcta',
                'solution': '1. Asegúrate de que el bot esté publicado en Azure\n' +
                           '2. Verifica que la clave secreta sea la correcta\n' +
                           '3. Revisa los registros del bot en Azure Portal para ver si hay errores'
            }), 500
            
        # 9. Retornar respuesta exitosa (sin exponer información sensible)
        response_data = {
            'success': True,
            'token': result.get('token'),
            'expires_in': result.get('expires_in', 3600),
            'hint': 'Token generado correctamente',
            'debug': {
                'token_length': len(result.get('token', '')),
                'expires_in': result.get('expires_in')
            }
        }
        
        print(f"Token generado con éxito. Longitud: {len(result.get('token', ''))} caracteres")
        return jsonify(response_data)

    except requests.exceptions.RequestException as e:
        # Manejo detallado de errores de red
        error_info = {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'request_url': getattr(e, 'request', {}).get('url', 'N/A'),
            'response_status': None,
            'response_text': None
        }
        
        if hasattr(e, 'response') and e.response is not None:
            error_info.update({
                'response_status': e.response.status_code,
                'response_text': e.response.text[:500] + '...' if e.response.text else None,
                'response_headers': dict(e.response.headers)
            })
        
        print(f"\n=== Error de conexión ===\n{json.dumps(error_info, indent=2)}\n")
        
        return jsonify({
            'success': False,
            'error': f'Error al conectar con Direct Line: {str(e)}',
            'details': error_info,
            'hint': 'Verifica tu conexión a internet y la configuración del bot',
            'solution': '1. Verifica que el bot esté publicado y en ejecución\n' +
                       '2. Comprueba que la clave secreta sea correcta\n' +
                       '3. Revisa la configuración de red y firewall'
        }), 500 if not hasattr(e, 'response') or e.response is None else e.response.status_code

    except Exception as e:
        # Manejo de errores inesperados
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n=== Error inesperado ===\n{error_trace}")
        
        return jsonify({
            'success': False,
            'error': f'Error inesperado: {str(e)}',
            'error_type': type(e).__name__,
            'hint': 'Consulta los registros del servidor para más detalles',
            'solution': '1. Revisa los registros de la aplicación en Azure Portal\n' +
                       '2. Verifica que todas las dependencias estén instaladas\n' +
                       '3. Contacta al soporte técnico si el problema persiste',
            'traceback': error_trace if os.getenv('FLASK_DEBUG') == '1' else None
        }), 500

# Endpoint para el chatbot
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'El mensaje no puede estar vacío'
            }), 400
            
        # Obtener respuesta del bot
        response = chat_bot.generate_response(message)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al procesar el mensaje: {str(e)}'
        }), 500

# Ruta para servir archivos estáticos
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Verificar conexión con los servicios al iniciar
    try:
        conectar_language()
        print("✅ Servicios listos en http://localhost:5000")
        print("\nEndpoints disponibles:")
        print("1. POST /api/analizar-sentimiento - Analiza el sentimiento de un texto")
        print("2. POST /api/traducir - Traduce un texto a otro idioma")
        print("3. POST /api/analizar-imagen - Analiza una imagen")
    except Exception as e:
        print(f"❌ Error al conectar con los servicios: {e}")
    
    app.run(debug=True, port=5000)
