from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("❌ OPENAI_API_KEY no encontrada en el archivo .env")

router = APIRouter()

class KeywordRequest(BaseModel):
    keywords: List[str]

class KeywordResponse(BaseModel):
    query: str
    intent: str
    recommended_format: str

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
        return json.loads(content)  # 👈 más seguro que eval
    except Exception as e:
        print(f"❌ Error al clasificar '{query}': {e}")
        return {"intent": "desconocido", "recommended_format": "otro"}

@router.post("/clasificar", response_model=List[KeywordResponse])
def clasificar_keywords(request: KeywordRequest):
    if not request.keywords:
        raise HTTPException(status_code=400, detail="La lista de keywords está vacía")

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
