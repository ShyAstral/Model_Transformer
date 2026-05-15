from contextlib import asynccontextmanager
from fastapi import FastAPI

from services import model, db
from routers import generate, text

# This code will be executed once before the application starts receiving requests
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the AI model
    model.InitModel()

    # Load the database and create tables
    db.CreateTables()

    yield
    # Clean up the AI model and release the resources


app = FastAPI(lifespan=lifespan)

app.include_router(generate.router)
app.include_router(text.router)

@app.get("/")
async def root():
    return {"message": "Backend Running Fine"}
