from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Importa el middleware
from services import model, db
from routers import generate, text, metric

@asynccontextmanager
async def lifespan(app: FastAPI):
    model.InitModel()
    db.CreateTables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router)
app.include_router(text.router)
app.include_router(metric.router)

@app.get("/")
async def root():
    return {"message": "Backend Running Fine"}
