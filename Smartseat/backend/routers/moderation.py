from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/moderate", tags=["moderation"])

class TextIn(BaseModel):
    text: str

@router.post("")
def moderate(payload: TextIn):
    # trivial rule-based classifier; replace with ML later
    banned = {"spam", "abuse", "hate", "violent", "weapon", "爆炸", "辱骂", "仇恨"}
    text = payload.text.lower()
    violated = any(word in text for word in banned)
    return {"label": "violated" if violated else "compliant", "violated": violated}
