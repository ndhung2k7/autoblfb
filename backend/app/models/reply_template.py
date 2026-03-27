from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from bson import ObjectId

class ReplyTemplate(BaseModel):
    id: Optional[ObjectId]
    page_id: str
    template_type: str  # 'greeting', 'price_inquiry', 'info', 'complaint', 'spam', 'toxic', 'general'
    content: str
    keywords: List[str] = []
    priority: int = 1  # 1-5, higher priority for specific cases
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
