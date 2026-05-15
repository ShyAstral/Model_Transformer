from contextlib import asynccontextmanager
from fastapi import FastAPI

from services import model
from routers import generate

# This code will be executed once before the application starts receiving requests
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the AI model
    model.InitModel()

    yield
    # Clean up the ML models and release the resources


app = FastAPI(lifespan=lifespan)

app.include_router(generate.router)

@app.get("/")
async def root():
    return {"message": "Backend Running Fine"}
