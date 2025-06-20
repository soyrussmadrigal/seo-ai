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
    raise ValueError("❌ OPENAI_API_KEY is not set")

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

# === DB Dependency ===

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Intent Classification Function ===

def classify_keyword_with_ai(query: str) -> dict:
    prompt = f"""
Given the following user search query: "{query}", respond in JSON with two fields:
- "intent": choose from ["informational", "transactional", "navigational"]
- "format": choose from ["article", "tool", "comparator", "landing page", "guide", "FAQ", "other"]

Example:
{{"intent": "informational", "format": "article"}}
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
        return {"intent": "unknown", "format": "other"}

# === API Routes ===

@app.post("/classify-pending")
async def classify_pending_keywords(db: Session = Depends(get_db)):
    pending_keywords = db.query(KeywordHistory).filter(
        KeywordHistory.intent == "pending",
        KeywordHistory.format == "pending"
    ).limit(10).all()

    saved_count = 0

    for kw in pending_keywords:
        print(f"🔍 Classifying: {kw.keyword}")
        try:
            result = classify_keyword_with_ai(kw.keyword)
            kw.intent = result["intent"]
            kw.format = result["format"]
            db.add(kw)
            saved_count += 1
            await asyncio.sleep(1.2)  # evita rate limit
        except Exception as e:
            print(f"❌ Error classifying '{kw.keyword}':", e)

    db.commit()
    return {"status": "success", "saved": saved_count}

@app.get("/history", response_model=List[KeywordHistoryResponse])
def read_history(db: Session = Depends(get_db)):
    data = db.query(KeywordHistory).order_by(KeywordHistory.created_at.desc()).all()
    if not data:
        raise HTTPException(status_code=204, detail="No keyword history found")
    return data