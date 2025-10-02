# Configuración para Honda 360° Extractor con IA
# Copia este archivo como config.py y configura tu API key

import os

# Configuración de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "tu_openai_api_key_aqui")

# Ejemplo de configuración:
# OPENAI_API_KEY = "sk-1234567890abcdef..."

# Para configurar la variable de entorno:
# Windows: set OPENAI_API_KEY=tu_key_aqui
# Linux/Mac: export OPENAI_API_KEY=tu_key_aqui

