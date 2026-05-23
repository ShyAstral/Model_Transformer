from fastapi import APIRouter
from pydantic import BaseModel, Field

from services import db

# This defines the fields of the POST's body request
class Stat(BaseModel):
    tabcount: int = Field(..., ge=0) # Obligatory
    tipcount: int = Field(..., ge=0) # Obligatory

router = APIRouter()

@router.post("/metric")
async def insert_metric(stat: Stat):
    return db.InsertMetric(stat.tabcount, stat.tipcount)

@router.get("/metric")
async def select_metric():
    return db.SelectMetric()
