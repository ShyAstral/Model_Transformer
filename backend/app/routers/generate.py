from fastapi import APIRouter
from pydantic import BaseModel, Field

from services import model, db

# This defines the fields of the POST's body request
class Prompt(BaseModel):
    text: str = Field(..., min_length=1)    # Obligatory
    maxtokens: int = Field(default=2, ge=1) # Optional

router = APIRouter()

@router.post("/generate")
async def generate(prompt: Prompt):
    prediction = model.GenerateText(prompt.text, prompt.maxtokens)

    return {"prediction": prediction}

@router.get("/train")
async def train_model():
    texts = db.SelectText()

    model.TrainModel(texts)
