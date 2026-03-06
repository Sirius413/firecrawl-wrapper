from fastapi import APIRouter, HTTPException
import requests

from app.schemas import CrawlRequest, CrawlResponse, CrawlStatusResponse
from app.config import settings

router = APIRouter()

@router.post("/crawl", response_model=CrawlResponse)
def crawl_url(request: CrawlRequest):
    """
    Start a crawl job (async). Returns job ID.
    Use /crawl/status/{job_id} to check progress.
    """
    headers = {
        "Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": request.url,
        "limit": request.limit,
        "maxDiscoveryDepth": request.maxDepth,
        "includePaths": request.includePaths or [],
        "excludePaths": request.excludePaths or [],
        "scrapeOptions": {
            "formats": ["markdown"]
        }
    }

    try:
        response = requests.post(
            f"{settings.FIRECRAWL_API_URL}/crawl",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            return {
                "job_id": data.get("id"),
                "status": "processing",
                "message": f"Crawl job started for {request.url}"
            }
        else:
            raise HTTPException(status_code=500, detail="Firecrawl crawl failed to start")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crawl/status/{job_id}", response_model=CrawlStatusResponse)
def crawl_status(job_id: str):
    """
    Check crawl job status and get results if complete.
    """
    headers = {
        "Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{settings.FIRECRAWL_API_URL}/crawl/{job_id}",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        return {
            "job_id": job_id,
            "status": data.get("status", "unknown"),
            "total": data.get("total", 0),
            "completed": data.get("completed", 0),
            "data": data.get("data", []),
            "error": data.get("error")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
