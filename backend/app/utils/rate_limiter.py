from datetime import datetime, timedelta
from typing import Dict
import threading

class RateLimiter:
    def __init__(self):
        self.reply_counts = {}  # page_id -> count
        self.last_reset = datetime.utcnow()
        self.lock = threading.Lock()
    
    def can_reply(self, page_id: str, limit_per_hour: int) -> bool:
        """Check if page can reply within rate limit"""
        with self.lock:
            # Reset counters if hour has passed
            now = datetime.utcnow()
            if now - self.last_reset > timedelta(hours=1):
                self.reply_counts = {}
                self.last_reset = now
            
            current_count = self.reply_counts.get(page_id, 0)
            
            if current_count < limit_per_hour:
                self.reply_counts[page_id] = current_count + 1
                return True
            
            return False
