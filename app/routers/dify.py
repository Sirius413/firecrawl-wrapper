from fastapi import APIRouter, HTTPException
import requests
import time

from app.schemas import DifyCrawlRequest, DifyCrawlResponse
from app.config import settings

router = APIRouter()

@router.post("/dify/crawl", response_model=DifyCrawlResponse)
def dify_crawl_url(request: DifyCrawlRequest):
    """
    Start a crawl job (async) in dify. Returns job ID.
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
    
    # Start the crawl
    print("Start the crawl")
    job_id = ""
    
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
            job_id = data.get("id")
        else:
            raise HTTPException(status_code=500, detail="Firecrawl crawl failed to start")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Check crawl status
    print("Check crawl status")
    headers = {
        "Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}"
    }
    
    status = ""
    total = 0
    completed = 0
    pages_data = []
    error = ""
    
    cnt = 0

    while True:
        try:
            response = requests.get(
                f"{settings.FIRECRAWL_API_URL}/crawl/{job_id}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status", "unknown")
            total = data.get("total", 0)
            completed = data.get("completed", 0)
            pages_data = data.get("data", [])
            error = data.get("error")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        
        if status == "completed":
            break
        else:
            time.sleep(5)
            cnt += 1
            
            if cnt >= 10:
                return {
                    "job_id": job_id,
                    "status": "failed",
                    "message": f"Failed for crawling {request.url}"
                }
    
    print(total)
    print(completed)
    print(error)
    
    # Check custom metadata tags in dify
    print("check custom metadata")
    headers = {
        "Authorization": f"Bearer {settings.DIFY_BACKEND_API_KEY}"
    }
    
    dataset_id = request.datasetID
    doc_metadata = []
        
    try:
        response = requests.get(
            f"{settings.DIFY_DOMAIN}/v1/datasets/{dataset_id}/metadata",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        doc_metadata = data.get("doc_metadata")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Add missing metadata tags
    headers = {
        "Authorization": f"Bearer {settings.DIFY_BACKEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    metadata_tags = {}
    missing_tags = list({tag for tag in request.metadataNames} - {item["name"] for item in doc_metadata})
    
    for tag in doc_metadata:
        if tag['name'] in list({tag for tag in request.metadataNames} - set(missing_tags)):
            metadata_tags[tag['name']] = tag['id']

    for tag in missing_tags:
        payload = {
            "value": "string",
            "name": tag
        }
        
        try:
            response = requests.post(
                f"{settings.DIFY_DOMAIN}/v1/datasets/{dataset_id}/metadata",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            metadata_tags[tag] = data.get("id")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    print(metadata_tags)
    # Upload files