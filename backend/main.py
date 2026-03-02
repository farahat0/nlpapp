from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.database import engine, Base

# Import all models so SQLAlchemy knows about them
from backend.modules.auth.model import User  # noqa: F401
from backend.modules.reviews.model import ReviewRecord  # noqa: F401

# Import routers
from backend.modules.auth.router import router as auth_router
from backend.modules.nlp.router import router as nlp_router
from backend.modules.reviews.router import router as reviews_router
from backend.modules.analytics.router import router as analytics_router

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HR NLP Application",
    description="AI-powered HR review analysis with sentiment analysis, skill extraction, performance scoring, and recommendation generation.",
    version="0.1.0",
)

# CORS — allow React frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all module routers
app.include_router(auth_router)
app.include_router(nlp_router)
app.include_router(reviews_router)
app.include_router(analytics_router)


@app.get("/")
async def root():
    return {
        "message": "HR NLP Application API",
        "docs": "/docs",
        "version": "0.1.0",
    }
