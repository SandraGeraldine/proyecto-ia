#!/bin/bash

# Este archivo inicia la aplicación Flask usando Gunicorn
# Configura el puerto para Azure App Service
export PORT=8000

# Crea la carpeta de sesiones si no existe
mkdir -p sessions

# Inicia la aplicación con Gunicorn
exec gunicorn --bind=0.0.0.0:$PORT \
              --timeout 600 \
              --workers 4 \
              --threads 2 \
              --access-logfile - \
              --error-logfile - \
              main:app
