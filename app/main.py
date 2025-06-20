from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import openai
import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="SEO Intent Classifier")

# Modelo de entrada
class KeywordRequest(BaseModel):
    keywords: List[str]

# Modelo de respuesta individual
class KeywordResponse(BaseModel):
    query: str
    intent: str
    recommended_format: str

# Clasificador con OpenAI
def clasificar_keyword(query: str) -> dict:
    prompt = f"""
Dada la siguiente consulta de búsqueda de un usuario: "{query}", responde en JSON con dos campos:
- "intent": una de estas opciones: ["informacional", "transaccional", "navegacional"]
- "recommended_format": una de estas opciones: ["artículo", "herramienta", "comparador", "landing page", "guía", "FAQ", "otro"]

Ejemplo de salida:
{{"intent": "informacional", "recommended_format": "artículo"}}

Respuesta:
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        return eval(content)  # Usa json.loads si preferís más seguridad
    except Exception as e:
        print(f"❌ Error con query '{query}': {e}")
        return {"intent": "desconocido", "recommended_format": "otro"}

# Ruta FastAPI
@app.post("/clasificar", response_model=List[KeywordResponse])
def clasificar_keywords(request: KeywordRequest):
    resultados = []
    for query in request.keywords:
        print(f"📌 Clasificando: {query}")
        resultado = clasificar_keyword(query)
        resultados.append({
            "query": query,
            "intent": resultado["intent"],
            "recommended_format": resultado["recommended_format"]
        })
    return resultados
