from pydantic import BaseModel

class KeywordRequest(BaseModel):
    keyword: str

class PredictionResponse(BaseModel):
    intent: str
    recommended_format: str
    title_suggestion: str
