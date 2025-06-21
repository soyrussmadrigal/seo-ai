from pydantic import BaseModel
from typing import Optional
from datetime import date


class KeywordResponse(BaseModel):
    keyword: str
    clicks: int
    impressions: int
    ctr: float
    position: float
    gsc_date: date
    intent: Optional[str] = None
    format: Optional[str] = None

    class Config:
        orm_mode = True  # 🔥 Necesario para que Pydantic entienda los modelos ORM
