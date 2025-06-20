# === Organized Imports ===

# Built-in
import os
import json
import asyncio
from datetime import datetime, date
from typing import List, Optional

# Third-party
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

# Internal
from app.db import SessionLocal, engine
from app.models import Base, KeywordHistory
from app.gsc_fetcher import extraer_datos_gsc


# === Initial Configuration ===

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("❌ OPENAI_API_KEY is not set in environment variables")

app = FastAPI(title="SEO Intent Classifier")


# 🟢 Aquí va el middleware CORS (justo después)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Pydantic Schemas ===

class KeywordRequest(BaseModel):
    keywords: List[str]

class KeywordResponse(BaseModel):
    query: str
    intent: str
    recommended_format: str

class KeywordInput(BaseModel):
    keyword: str
    intent: str
    format: str
    clicks: int
    impressions: int
    ctr: float
    position: float

class KeywordHistoryResponse(BaseModel):
    id: int
    keyword: str
    intent: str
    format: str
    clicks: int
    impressions: int
    ctr: float
    position: float
    created_at: datetime

    # Hazlo Optional y dale valor por defecto None
    gsc_date: Optional[date] = None

    model_config = {"from_attributes": True}


# === Database Dependency ===

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === Intent Classification with OpenAI ===

def classify_keyword_with_ai(query: str) -> dict:
    prompt = f"""
Given the following user search query: "{query}", respond in JSON with two fields:
- "intent": choose from ["informational", "transactional", "navigational"]
- "recommended_format": choose from ["article", "tool", "comparator", "landing page", "guide", "FAQ", "other"]

Example:
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
        return json.loads(content)
    except Exception as e:
        print(f"❌ Error classifying '{query}':", e)
        return {"intent": "unknown", "recommended_format": "other"}


# === API Routes ===

@app.post("/clasificar", response_model=List[KeywordResponse])
def clasificar_keywords(request: KeywordRequest):
    results = []
    for query in request.keywords:
        print(f"📌 Classifying (on-the-fly): {query}")
        result = classify_keyword_with_ai(query)
        results.append({
            "query": query,
            "intent": result["intent"],
            "recommended_format": result["recommended_format"]
        })
    return results


@app.get("/extraer-datos")
def extraer_datos():
    try:
        data = extraer_datos_gsc()
        return {"status": "success", "rows": len(data), "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/save_history")
def save_history(data: List[KeywordInput], db: Session = Depends(get_db)):
    for item in data:
        classification = classify_keyword_with_ai(item.keyword)
        record = KeywordHistory(
            keyword=item.keyword,
            intent=classification["intent"],
            format=classification["recommended_format"],
            clicks=item.clicks,
            impressions=item.impressions,
            ctr=item.ctr,
            position=item.position,
        )
        db.add(record)
    db.commit()
    return {"status": "ok"}


@app.post("/classify-pending")
async def classify_pending(db: Session = Depends(get_db)):
    pending = db.query(KeywordHistory).filter(
        KeywordHistory.intent == "pending",
        KeywordHistory.format == "pending"
    ).limit(10).all()

    saved = 0
    for kw in pending:
        print(f"🔍 Classifying pending: {kw.keyword}")
        result = classify_keyword_with_ai(kw.keyword)
        kw.intent = result["intent"]
        kw.format = result["recommended_format"]
        db.add(kw)
        saved += 1
        await asyncio.sleep(1.2)
    db.commit()
    return {"status": "success", "saved": saved}


@app.get("/history", response_model=List[KeywordHistoryResponse])
def read_history(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    intent: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
):
    query = db.query(KeywordHistory)

    if start_date:
        query = query.filter(KeywordHistory.gsc_date >= start_date)
    if end_date:
        query = query.filter(KeywordHistory.gsc_date <= end_date)
    if intent:
        query = query.filter(KeywordHistory.intent == intent)
    if format:
        query = query.filter(KeywordHistory.format == format)

    return query.order_by(KeywordHistory.gsc_date.desc()).all()
