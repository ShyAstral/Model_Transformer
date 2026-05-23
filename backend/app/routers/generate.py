from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel, Field
from services import model, db

class Prompt(BaseModel):
    text: str = Field(..., min_length=1)
    maxtokens: int = Field(default=2, ge=1)

router = APIRouter()

@router.post("/generate")
async def generate(prompt: Prompt):
    prediction = model.GenerateText(prompt.text, prompt.maxtokens)

    return {"prediction": prediction}

@router.get("/train")
async def train_model():
    texts = db.SelectText()

    model.TrainModel(texts)

@router.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    content = await file.read()
    lines = content.decode("utf-8").splitlines()

    db.ClearTextTable()
    for line in lines:
        if line.strip():
            db.InsertText(line.strip(), len(line.split()))
            
    model.TrainModel(lines)
    return {"message": "Dataset actualizado y modelo reentrenado con éxito"}