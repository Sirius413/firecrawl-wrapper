from fastapi import APIRouter, HTTPException
import logging
import requests
import time

from app.schemas import DifyCrawlRequest, DifyCrawlResponse
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/dify/crawl", response_model=DifyCrawlResponse)
def dify_crawl_url(request: DifyCrawlRequest):
    """
    Start a crawl job (async) in dify. Returns job ID.
    Use /crawl/status/{job_id} to check progress.
    Upload files into a given knowledge base in dify with custom metadata.
    """
    logger.debug(f"正在请求 Firecrawl Wrapper API: {settings.FIRECRAWL_API_URL}/dify/crawl")
    
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
    
    # 1. Start the crawl mission
    logger.debug("开始 Crawl 任务")
    job_id = ""
    
    try:
        response = requests.post(
            f"{settings.FIRECRAWL_API_URL}/crawl",
            headers=headers,
            json=payload,
            timeout=30
        )
        logger.debug(f"Firecrawl API 响应状态码(Crawl 任务): {response.status_code}")

        response.raise_for_status()
        data = response.json()
        
        logger.debug(f"API 返回数据(Crawl 任务): {data}")

        if data.get("success"):
            job_id = data.get("id")
            logger.info(f"Crawl 任务启动成功, Job ID: {job_id}")
        else:
            logger.error(f"Crawl 任务失败：{data}")
            raise HTTPException(status_code=500, detail="Firecrawl crawl failed to start")
    except Exception as e:
        logger.exception(f"发生未知错误(Crawl 任务): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # 2. Check crawl mission status
    logger.debug("查看 Crawl 任务状态")
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
            logger.debug(f"Firecrawl API 响应状态码(Crawl 任务状态): {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            
            logger.debug(f"API 返回数据(Crawl 任务状态)：{data}")
            
            status = data.get("status", "unknown")
            total = data.get("total", 0)
            completed = data.get("completed", 0)
            pages_data = data.get("data", [])
            error = data.get("error")
        except Exception as e:
            logger.exception(f"发生未知错误(Crawl 任务状态): {str(e)}") 
            raise HTTPException(status_code=500, detail=str(e))

        
        if status == "completed":
            logger.info(f"Crawl 任务成功, Job ID: {job_id}")
            logger.info(f"将被抓取的网页总数: {total}, 已完成抓取的网页总数: {completed}")
            logger.error(f"未知错误：{error}")
            break
        else:
            logger.debug(f"将被抓取的网页总数: {total}, 已完成抓取的网页总数: {completed}")
            time.sleep(5)
            cnt += 1
            
            if cnt >= 10:
                logger.error(f"Crawl 任务超时: {data}")
                return {
                    "job_id": job_id,
                    "status": "failed",
                    "message": f"Failed for crawling {request.url}"
                }
    
    # 3. Query custom metadata tags in given dify knowledge base
    logger.debug("查询 dify 知识库自定义元数据")
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
        logger.debug(f"dify API 响应状态码(查询知识库自定义元数据): {response.status_code}")
        
        response.raise_for_status()
        data = response.json()
        
        logger.debug(f"API 返回数据(查询知识库自定义元数据)：{data}")
        
        doc_metadata = data.get("doc_metadata")
    except Exception as e:
        logger.exception(f"发生未知错误(查询知识库自定义元数据): {str(e)}") 
        raise HTTPException(status_code=500, detail=str(e))
    
    # 4. Add missing metadata tags
    logger.debug("添加 dify 知识库自定义元数据")
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
        # TODO: in future, can get missing tags as dict and set up the value
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
            logger.debug(f"dify API 响应状态码(添加知识库自定义元数据): {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            
            logger.debug(f"API 返回数据(添加知识库自定义元数据)：{data}")
            
            metadata_tags[tag] = data.get("id")
        except Exception as e:
            logger.exception(f"发生未知错误(添加知识库自定义元数据): {str(e)}") 
            raise HTTPException(status_code=500, detail=str(e))
    
    logger.info(f"dify 自定义元数据ID: {metadata_tags}")
    
    # TODO: 5. Upload files
    
    
    # TODO: 6. Update metadata of each file (check is doc_metadata working, there is a github issue on this)
    # if fixed, than this step can be skipped