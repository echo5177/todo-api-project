import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="My Todo API", lifespan=lifespan)

# Read allowed origins from environment or default to localhost
allowed_origins_str = os.environ.get("ALLOWED_ORIGINS", "")
allowed_origins = [
    origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()
]

# Provide a safe fallback if no ALLOWED_ORIGINS is provided
if not allowed_origins:
    allowed_origins = ["http://localhost:8000"]  # A sane default for local development

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)


@app.get("/")
def read_root():
    return {"message": "Todo API is running"}
