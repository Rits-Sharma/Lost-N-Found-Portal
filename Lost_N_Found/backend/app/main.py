"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import Base, engine

# Import models so SQLAlchemy registers all tables
from app.models import user, item, claim, match
from app.routes import auth, items, claims


# Create database tables
Base.metadata.create_all(bind=engine)


# Initialize FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="College Lost & Found Portal API"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(claims.router)


@app.get("/")
def read_root():
    """Health check endpoint."""

    return {
        "message": "College Lost & Found Portal API",
        "version": settings.API_VERSION,
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""

    return {
        "status": "healthy"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )