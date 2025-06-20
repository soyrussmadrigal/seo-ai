# === Organized Imports ===

# Built-in
import os
import json
from datetime import datetime
from typing import List

# Third-party
from fastapi import FastAPI, Depends
from fastapi import HTTPException 
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

# Load .env variables
load_dotenv()

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("❌ OPENAI_API_KEY is not set in environment variables")

# Initialize FastAPI app
app = FastAPI(title="SEO Intent Classifier")

# Enable CORS for frontend communication
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


# === Intent Classification Function ===

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
        return json.loads(content)
    except Exception as e:
        print(f"❌ Error classifying '{query}': {e}")
        return {"intent": "unknown", "recommended_format": "other"}


# === Database Dependency ===

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === API Routes ===

@app.post("/clasificar", response_model=List[KeywordResponse])
def clasificar_keywords(request: KeywordRequest):
    results = []
    for query in request.keywords:
        print(f"📌 Classifying: {query}")
        result = clasificar_keyword(query)
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
def save_keywords(data: List[KeywordInput], db: Session = Depends(get_db)):
    for item in data:
        record = KeywordHistory(**item.dict())
        db.add(record)
    db.commit()
    return {"status": "ok"}


# === Keyword History Endpoint ===

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

    model_config = {
    "from_attributes": True
}

@app.get("/history", response_model=List[KeywordHistoryResponse])
def read_history(db: Session = Depends(get_db)):
    data = db.query(KeywordHistory).order_by(KeywordHistory.created_at.desc()).all()
    if not data:
        raise HTTPException(status_code=204, detail="No keyword history found")
    return data


# === DB Table Creation ===

Base.metadata.create_all(bind=engine)

@app.get("/fetch-and-save")
def fetch_and_save(db: Session = Depends(get_db)):
    try:
        raw_data = extraer_datos_gsc()
        if not raw_data:
            raise HTTPException(status_code=204, detail="No data extracted from GSC")

        for row in raw_data:
            record = KeywordHistory(
                keyword=row["query"],
                intent="pending",  # or default
                format="pending",  # or default
                clicks=row.get("clicks", 0),
                impressions=row.get("impressions", 0),
                ctr=row.get("ctr", 0.0),
                position=row.get("position", 0.0),
            )
            db.add(record)

        db.commit()
        return {"status": "success", "saved_records": len(raw_data)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
  # === Endpoint to classify unprocessed keywords ===

@app.post("/classify-pending")
def classify_pending_keywords(db: Session = Depends(get_db)):
    pending_keywords = db.query(KeywordHistory).filter(KeywordHistory.intent == None).all()
    print(f"🔍 Found {len(pending_keywords)} pending keywords")  # ← este print es clave

    if not pending_keywords:
        return {"status": "success", "saved": 0}

    count = 0
    for row in pending_keywords:
        result = clasificar_keyword(row.keyword)
        print(f"🧠 Classifying '{row.keyword}' → {result}")  # ← este también

        row.intent = result.get("intent")
        row.format = result.get("recommended_format")
        count += 1

    db.commit()
    return {"status": "success", "saved": count}
