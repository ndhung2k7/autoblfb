from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.post("/{page_id}")
async def create_template(page_id: str, template_data: dict):
    """Create a reply template for a page"""
    template = {
        'page_id': page_id,
        'template_type': template_data['template_type'],
        'content': template_data['content'],
        'keywords': template_data.get('keywords', []),
        'priority': template_data.get('priority', 1),
        'is_active': template_data.get('is_active', True),
        'created_at': datetime.utcnow()
    }
    
    result = await request.app.db.reply_templates.insert_one(template)
    return {"success": True, "template_id": str(result.inserted_id)}

@router.get("/{page_id}")
async def get_templates(page_id: str):
    """Get all templates for a page"""
    templates = await request.app.db.reply_templates.find(
        {'page_id': page_id}
    ).to_list(length=100)
    
    return {"templates": templates}

@router.put("/{template_id}")
async def update_template(template_id: str, template_data: dict):
    """Update a template"""
    result = await request.app.db.reply_templates.update_one(
        {'_id': ObjectId(template_id)},
        {'$set': template_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"success": True}

@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """Delete a template"""
    result = await request.app.db.reply_templates.delete_one(
        {'_id': ObjectId(template_id)}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"success": True}
