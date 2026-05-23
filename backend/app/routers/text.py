from fastapi import APIRouter
from pydantic import BaseModel, Field

from services import db

class Phrase(BaseModel):
    text: str = Field(..., min_length=1) # Obligatory

router = APIRouter()

@router.post("/text")
async def insert_text(phrase: Phrase):
    wordCount = len(phrase.text.split(" "))

    return db.InsertText(phrase.text, wordCount)
