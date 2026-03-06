from .crawl import router as crawl_router
from .dify import router as dify_router
from .health import router as health_router
from .scrape import router as scrape_router

__all__ = ["crawl_router", "health_router", "scrape_router", "dify_router"]
