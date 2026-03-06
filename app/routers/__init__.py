from .crawl import router as crawl_router
from .health import router as health_router
from .scrape import router as scrape_router

__all__ = ["crawl_router", "health_router", "scrape_router"]
