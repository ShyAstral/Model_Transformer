from fastapi import APIRouter
from pydantic import BaseModel, Field

from services import model

# This defines the fields of the post's body request
class Input(BaseModel):
    text: str = Field(..., min_length=1)    # Obligatory
    maxtokens: int = Field(default=2, ge=1) # Optional

router = APIRouter()

@router.post("/generate")
async def generate(input: Input):
    prediction = model.GenerateText(input.text, input.maxtokens)

    return {"prediction": prediction}
