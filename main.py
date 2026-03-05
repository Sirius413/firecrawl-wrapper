from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import requests
import os
from fastapi.middleware.cors import CORSMiddleware

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

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
FIRECRAWL_API_URL = "http://api:3002/v1/scrape"

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
        response = requests.post(FIRECRAWL_API_URL, json=payload, headers=headers, timeout=40)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            # edit here to change the return format of the API
            return {"markdown": data["data"]["markdown"], "metadata": data["data"].get("metadata", {})}
        else:
            raise HTTPException(status_code=500, detail="Firecrawl failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}