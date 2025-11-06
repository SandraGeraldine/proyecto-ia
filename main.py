from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Importar los servicios
from servicio_language import analizar_sentimiento, conectar_language
from servicio_translator import traducir_texto
from servicio_vision import describir_imagen

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
