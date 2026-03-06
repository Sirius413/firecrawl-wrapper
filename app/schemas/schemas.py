from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ScrapeRequest(BaseModel):
    """Request schema for scrape endpoint."""
    url: str


class CrawlRequest(BaseModel):
    """Request schema for crawl endpoint."""
    url: str
    maxDepth: Optional[int] = 1
    limit: Optional[int] = 20
    allowExternalLinks: Optional[bool] = False
    ignoreSitemap: Optional[bool] = False
    includePaths: Optional[List[str]] = None
    excludePaths: Optional[List[str]] = None


class DifyCrawlRequest(BaseModel):
    """Request schema for crawl endpoint."""
    url: str
    datasetID: str
    maxDepth: Optional[int] = 1
    limit: Optional[int] = 20
    allowExternalLinks: Optional[bool] = False
    ignoreSitemap: Optional[bool] = False
    includePaths: Optional[List[str]] = None
    excludePaths: Optional[List[str]] = None
    metadataNames: Optional[List[str]] = []


class ScrapeResponse(BaseModel):
    """Response schema for scrape endpoint."""
    markdown: str
    metadata: Dict[str, Any]


class CrawlResponse(BaseModel):
    """Response schema for crawl endpoint."""
    job_id: str
    status: str
    message: str


class CrawlStatusResponse(BaseModel):
    """Response schema for crawl status endpoint."""
    job_id: str
    status: str
    total: int
    completed: int
    data: List[Dict[str, Any]]
    error: Optional[str] = None


class DifyCrawlResponse(BaseModel):
    """Response schema for crawl endpoint."""
    job_id: str
    status: str
    message: str


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: str
