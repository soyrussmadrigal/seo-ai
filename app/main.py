from app.gsc_fetcher import extraer_datos_gsc
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import openai
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Cargar variables del .env
load_dotenv()

# Verificamos si la API Key existe
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("❌ OPENAI_API_KEY is not set in environment variables")

# Inicializar FastAPI
app = FastAPI(title="SEO Intent Classifier")

# ✅ CORS para permitir conexión con frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Esquema de entrada


class KeywordRequest(BaseModel):
    keywords: List[str]

# Esquema de salida


class KeywordResponse(BaseModel):
    query: str
    intent: str
    recommended_format: str

# Clasificación individual usando OpenAI


def clasificar_keyword(query: str) -> dict:
    prompt = f"""
Given the following user search query: "{query}", respond in JSON with two fields:
- "intent": choose from ["informational", "transactional", "navigational"]
- "recommended_format": choose from ["article", "tool", "comparator", "landing page", "guide", "FAQ", "other"]

Example output:
{{"intent": "informational", "recommended_format": "article"}}

Response:
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        return eval(content)  # Para producción usar `json.loads`
    except Exception as e:
        print(f"❌ Error al clasificar '{query}': {e}")
        return {"intent": "desconocido", "recommended_format": "otro"}

# Ruta principal para clasificar


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


@app.get("/extraer-datos")
def extraer_datos():
    try:
        datos = extraer_datos_gsc()
        return {"status": "success", "rows": len(datos), "data": datos}
    except Exception as e:
        return {"status": "error", "message": str(e)}
