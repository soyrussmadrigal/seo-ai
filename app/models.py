from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db import Base  # ✅ Este es el import correcto

class KeywordHistory(Base):
    __tablename__ = "keyword_history"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True)
    intent = Column(String)
    format = Column(String)
    clicks = Column(Integer)
    impressions = Column(Integer)
    ctr = Column(Float)
    position = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
