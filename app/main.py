# === Imports ===

# Built-in
import os
import json
import asyncio
from datetime import datetime, date
from typing import List, Optional

# Third-party
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import openai

# Internal
from app.db import SessionLocal
from app.models import KeywordHistory
from app.gsc_fetcher import extraer_datos_gsc

# === App Initialization ===

load_dotenv()
print("✅ Ruta JSON:", os.getenv("GSC_SERVICE_ACCOUNT_FILE"))
print("🧪 Existe archivo:", os.path.exists(
    os.getenv("GSC_SERVICE_ACCOUNT_FILE")))

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("❌ OPENAI_API_KEY is missing from environment variables")

app = FastAPI(title="SEO AI Classifier")

# === CORS Configuration ===

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # durante desarrollo puedes usar "*"
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
    date: str


class KeywordHistoryResponse(BaseModel):
    id: int
    keyword: str
    intent: Optional[str] = None    # ahora acepta null
    format: Optional[str] = None
    clicks: int
    impressions: int
    ctr: float
    position: float
    created_at: datetime
    gsc_date: Optional[date] = None

    class Config:
        orm_mode = True

# === Database Dependency ===


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === AI Classification Function ===


def classify_keyword_with_ai(query: str) -> dict:
    prompt = f"""
Given the following user search query: \"{query}\", respond in JSON with two fields:
- \"intent\": choose from [\"informational\", \"transactional\", \"navigational\"]
- \"recommended_format\": choose from [\"article\", \"tool\", \"comparator\", \"landing page\", \"guide\", \"FAQ\", \"other\"]

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
        print(f"📌 Classifying: {query}")
        result = classify_keyword_with_ai(query)
        results.append({
            "query": query,
            "intent": result["intent"],
            "recommended_format": result["recommended_format"]
        })
    return results


@app.get("/extraer-datos")
def extraer_datos(days: int = Query(default=1, ge=1, le=90)):
    try:
        print("➡️ Starting extraction...")
        data = extraer_datos_gsc(days)
        print(f"✅ Extracted {len(data)} rows")
        return {"status": "success", "rows": len(data), "data": data}
    except Exception as e:
        print(f"❌ Error extracting GSC data: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/save_history")
def save_history(data: List[KeywordInput], db: Session = Depends(get_db)):
    saved = 0
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
            gsc_date=datetime.fromisoformat(item.date).date()
        )
        db.add(record)
        saved += 1
    db.commit()
    return {"status": "ok", "saved": saved}


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

@app.get("/history/keyword")
def get_keyword_timeseries(text: str, db: Session = Depends(get_db)):
    results = (
        db.query(KeywordHistory)
        .filter(KeywordHistory.keyword == text)
        .order_by(KeywordHistory.gsc_date.asc())
        .all()
    )

    return [
        {
            "gsc_date": r.gsc_date.isoformat(),
            "clicks": r.clicks,
            "ctr": r.ctr,
            "position": r.position,
        }
        for r in results
    ]
