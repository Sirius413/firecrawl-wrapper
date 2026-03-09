import logging
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import crawl_router, health_router, scrape_router, dify_router

log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True
)

logger = logging.getLogger(__name__)

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
    app.include_router(dify_router)
    
    logger.info(f"Firecrawl Wrapper 启动成功，日志级别设置为：{log_level}")
    
    return app


app = create_app()
