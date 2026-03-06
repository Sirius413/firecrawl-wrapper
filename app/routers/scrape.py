from fastapi import APIRouter, HTTPException
import requests

from app.schemas import ScrapeRequest, ScrapeResponse
from app.config import settings

router = APIRouter()

@router.post("/scrape", response_model=ScrapeResponse)
def scrape_url(request: ScrapeRequest):
    """Scrape the given url
    """
    headers = {
        "Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": request.url,
        "formats": ["markdown"],
        "onlyMainContent": False
    }

    try:
        response = requests.post(
            f"{settings.FIRECRAWL_API_URL}/scrape", 
            headers=headers, 
            json=payload, 
            timeout=40
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            return {"markdown": data["data"]["markdown"], "metadata": data["data"].get("metadata", {})}
        else:
            raise HTTPException(status_code=500, detail="Firecrawl failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))