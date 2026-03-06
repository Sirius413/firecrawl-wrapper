from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import crawl_router, health_router, scrape_router


def create_app() -> FastAPI:
    """Application factory for creating the FastAPI app."""
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
    )

    # Allow CORS for Dify
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict this to your Dify domain in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(crawl_router)
    app.include_router(health_router)
    app.include_router(scrape_router)

    return app


app = create_app()
