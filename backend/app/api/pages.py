from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.page import FacebookPage
from ..services.facebook_service import FacebookService
from ..utils.logger import logger
from ..config import config

router = APIRouter(prefix="/api/pages", tags=["pages"])
facebook_service = FacebookService()

@router.post("/add")
async def add_page(page_data: dict):
    """Add a new Facebook page"""
    try:
        # Validate access token
        is_valid = await facebook_service.validate_token(page_data['access_token'])
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid access token")
        
        # Get page info
        page_info = await facebook_service.get_page_info(
            page_data['page_id'],
            page_data['access_token']
        )
        
        if not page_info:
            raise HTTPException(status_code=400, detail="Cannot fetch page info")
        
        # Check if page already exists
        existing = await request.app.db.pages.find_one({'page_id': page_data['page_id']})
        if existing:
            raise HTTPException(status_code=400, detail="Page already added")
        
        # Create page object
        page = FacebookPage(
            page_id=page_data['page_id'],
            page_name=page_info['name'],
            access_token=page_data['access_token'],
            category=page_info.get('category')
        )
        
        # Save to database
        result = await request.app.db.pages.insert_one(page.dict())
        
        return {"success": True, "page_id": str(result.inserted_id)}
        
    except Exception as e:
        logger.error(f"Error adding page: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_pages():
    """List all pages"""
    pages = await request.app.db.pages.find().to_list(length=100)
    return {"pages": pages}

@router.put("/{page_id}/toggle-reply")
async def toggle_auto_reply(page_id: str, enabled: bool):
    """Toggle auto reply for a page"""
    result = await request.app.db.pages.update_one(
        {'page_id': page_id},
        {'$set': {'auto_reply_enabled': enabled}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {"success": True, "auto_reply_enabled": enabled}

@router.delete("/{page_id}")
async def remove_page(page_id: str):
    """Remove a page"""
    result = await request.app.db.pages.delete_one({'page_id': page_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {"success": True}
