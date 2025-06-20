from dotenv import load_dotenv
load_dotenv()

import os
import time
import pandas as pd
from dotenv import load_dotenv
import openai
import json

# Cargar variables de entorno desde .env
load_dotenv()

# Inicializar cliente OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Verificar que la API Key esté presente
if not client.api_key:
    raise ValueError("❌ No se encontró OPENAI_API_KEY en las variables de entorno")

# Leer archivo CSV de entrada
df = pd.read_csv("data/gsc_keywords.csv")

# Crear columnas nuevas para etiquetado
df["intent"] = ""
df["recommended_format"] = ""

# Limitar número de filas para prueba
MAX_ROWS = 50

# Función de clasificación con OpenAI
def clasificar_keyword(query):
    prompt = f"""
Dada la siguiente consulta de búsqueda de un usuario: "{query}", responde en JSON con dos campos:
- "intent": una de estas opciones: ["informacional", "transaccional", "navegacional"]
- "recommended_format": una de estas opciones: ["artículo", "herramienta", "comparador", "landing page", "guía", "FAQ", "otro"]

Ejemplo de salida:
{{"intent": "informacional", "recommended_format": "artículo"}}

Respuesta:
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        print(f"❌ Error con query '{query}': {e}")
        return {"intent": "desconocido", "recommended_format": "otro"}

# Procesar keywords
for i, row in df.head(MAX_ROWS).iterrows():
    query = row["query"]
    print(f"📌 Clasificando: {query}")
    resultado = clasificar_keyword(query)
    df.at[i, "intent"] = resultado["intent"]
    df.at[i, "recommended_format"] = resultado["recommended_format"]
    time.sleep(1.5)  # Evitar saturar la API

# Guardar resultado
output_file = "data/gsc_keywords_labeled.csv"
df.to_csv(output_file, index=False)
print(f"✅ Archivo generado: {output_file}")
