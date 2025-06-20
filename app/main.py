# === Organized Imports ===

# Built-in
import os
import json
import asyncio
from datetime import datetime
from typing import List

# Third-party
from fastapi import FastAPI, Depends, HTTPException
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

# 1) Real-time classification (e.g. frontend form)
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


# 2) Fetch raw data from Google Search Console
@app.get("/extraer-datos")
def extraer_datos():
    try:
        data = extraer_datos_gsc()
        return {"status": "success", "rows": len(data), "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# 3) Save history with classification at save time
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


# 4) Optional: classify up to 10 pending records (manual trigger)
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


# 5) Read history (for your `/history` page)
@app.get("/history", response_model=List[KeywordHistoryResponse])
def read_history(db: Session = Depends(get_db)):
    # 1) Traer hasta 10 registros todavía en pending
    to_classify = (
        db.query(KeywordHistory)
          .filter(KeywordHistory.intent == "pending",
                  KeywordHistory.format == "pending")
          .order_by(KeywordHistory.created_at.desc())
          .limit(10)
          .all()
    )

    # 2) Clasificamos y guardamos esos 10
    if to_classify:
        for kw in to_classify:
            print(f"🔄 On-the-fly classify (limit 10): {kw.keyword}")
            result = classify_keyword_with_ai(kw.keyword)
            kw.intent = result["intent"]
            kw.format = result["recommended_format"]
            db.add(kw)
        db.commit()

    # 3) Ahora sí devolvemos todo el historial, ya sin esos 10 pendings
    all_rows = (
        db.query(KeywordHistory)
          .order_by(KeywordHistory.created_at.desc())
          .all()
    )
    return all_rows
