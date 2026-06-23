import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401
from .database import Base, engine
from .routers import auth, budgets, categories, dashboard, learn, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Financial Wellness API",
    description=(
        "An educational financial-wellness platform that combines personal-finance "
        "tracking with learning to build healthier money habits"
    ),
    lifespan=lifespan,
)

# Allow the frontend (Next.js dev server by default) to call the API.
cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(budgets.router)
app.include_router(dashboard.router)
app.include_router(learn.router)


@app.get("/")
def root():
    return {
        "message": "Financial Wellness API",
        "description": "An educational financial-wellness platform that pairs personal-finance tracking with gamified learning to help users build healthier money habits.",
        "features": [
            "Transaction tracking with categories",
            "Budget management periodically set with categories and alerts",
            "Spending analytics and insights",
            "Gamified financial-literacy learning with courses, lessons and quizzes",
            "XP, levels and daily streaks to keep learning fun and interactive",
            "User authentication and data security",
        ],
        "documentation": "/docs",
        "version": "2.0.0",
    }
