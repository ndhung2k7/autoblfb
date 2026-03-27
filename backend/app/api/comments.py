from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/comments", tags=["comments"])

@router.get("/{page_id}")
async def get_comments(page_id: str, limit: int = 50, replied: Optional[bool] = None):
    """Get comments for a page"""
    query = {'page_id': page_id}
    
    if replied is not None:
        query['replied'] = replied
    
    comments = await request.app.db.comments.find(query).sort(
        '-created_time'
    ).limit(limit).to_list(length=limit)
    
    return {"comments": comments}

@router.get("/stats/{page_id}")
async def get_stats(page_id: str):
    """Get comment statistics for a page"""
    # Total comments today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_today = await request.app.db.comments.count_documents({
        'page_id': page_id,
        'created_time': {'$gte': today_start}
    })
    
    replied_today = await request.app.db.comments.count_documents({
        'page_id': page_id,
        'replied': True,
        'created_time': {'$gte': today_start}
    })
    
    # Get page info
    page = await request.app.db.pages.find_one({'page_id': page_id})
    
    return {
        "total_comments_today": total_today,
        "replied_today": replied_today,
        "reply_rate": replied_today / total_today if total_today > 0 else 0,
        "auto_reply_enabled": page.get('auto_reply_enabled', True) if page else False,
        "replies_count_today": page.get('replies_count_today', 0) if page else 0
    }
