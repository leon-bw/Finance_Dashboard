from contextlib import asynccontextmanager

from fastapi import FastAPI

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
