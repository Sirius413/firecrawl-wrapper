from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import requests
import os
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List

app = FastAPI()

# Allow CORS for Dify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this to your Dify domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: str
    
class CrawlRequest(BaseModel):
    url: str
    maxDepth: Optional[int] = 1
    limit: Optional[int] = 20
    allowExternalLinks: Optional[bool] = False
    ignoreSitemap: Optional[bool] = False
    includePaths: Optional[List[str]] = None
    excludePaths: Optional[List[str]] = None

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
FIRECRAWL_API_URL = "http://api:3002/v1"

@app.post("/scrape")
def scrape_url(request: ScrapeRequest):
    payload = {
        "url": request.url,
        "formats": ["markdown"],
        "onlyMainContent": False
    }
    
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{FIRECRAWL_API_URL}/scrape", 
            json=payload, 
            headers=headers, 
            timeout=40
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            # edit here to change the return format of the API
            return {"markdown": data["data"]["markdown"], "metadata": data["data"].get("metadata", {})}
        else:
            raise HTTPException(status_code=500, detail="Firecrawl failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crawl")
def crawl_url(request: CrawlRequest):
    """
    Start a crawl job (async). Returns job ID.
    Use /crawl/status/{job_id} to check progress.
    """
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
    
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{FIRECRAWL_API_URL}/crawl",
            json=payload,
            headers=headers,
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


@app.get("/crawl/status/{job_id}")
def crawl_status(job_id: str):
    """
    Check crawl job status and get results if complete.
    """
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{FIRECRAWL_API_URL}/crawl/{job_id}",
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

@app.get("/health")
def health_check():
    return {"status": "healthy"}