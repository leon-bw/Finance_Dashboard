from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models  # noqa: F401
from .database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Personal Finance API",
    description="A financial management system for tracking transactions and budgets",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "message": "Personal Finance API",
        "description": "A comprehensive financial management system designed to help users track expenses, manage budgets, and gain actionable insights into their spending habits.",
        "features": [
            "Transaction tracking with categories",
            "Budget management periodically set with categories and alerts",
            "Spending analytics and insights",
            "User authentication and data security",
        ],
        "documentation": "/docs",
        "version": "1.0.0",
    }
