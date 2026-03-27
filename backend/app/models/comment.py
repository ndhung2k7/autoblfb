from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from bson import ObjectId

class Comment(BaseModel):
    id: Optional[str]
    page_id: str
    post_id: str
    comment_id: str
    user_id: str
    user_name: str
    message: str
    created_time: datetime
    replied: bool = False
    replied_time: Optional[datetime] = None
    reply_message: Optional[str] = None
    sentiment: Optional[str] = None
    processed: bool = False
    
    class Config:
        arbitrary_types_allowed = True

class ProcessedUser(BaseModel):
    page_id: str
    user_id: str
    last_replied_at: datetime
    replied_count: int = 1
