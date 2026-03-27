import asyncio
from datetime import datetime, timedelta
from typing import List
from ..services.reply_service import ReplyService
from ..utils.logger import logger

class MonitoringService:
    def __init__(self, db):
        self.db = db
        self.reply_service = ReplyService(db)
        self.is_running = False
    
    async def start_monitoring(self):
        """Start monitoring all pages"""
        self.is_running = True
        logger.info("Starting monitoring service...")
        
        while self.is_running:
            try:
                # Get all active pages
                pages = await self.db.pages.find().to_list(length=100)
                
                for page in pages:
                    if page.get('auto_reply_enabled', True):
                        await self.process_page(page)
                
                # Reset daily counters at midnight
                if datetime.utcnow().hour == 0 and datetime.utcnow().minute == 0:
                    await self.reset_daily_counters()
                
                # Wait before next monitoring cycle
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring service: {str(e)}")
                await asyncio.sleep(60)
    
    async def process_page(self, page):
        """Process a single page"""
        try:
            # Process new comments
            new_comments = await self.reply_service.process_new_comments(page)
            
            if new_comments:
                logger.info(f"Found {len(new_comments)} new comments for page {page['page_name']}")
                
        except Exception as e:
            logger.error(f"Error processing page {page['page_name']}: {str(e)}")
    
    async def reset_daily_counters(self):
        """Reset daily reply counters"""
        await self.db.pages.update_many(
            {},
            {'$set': {'replies_count_today': 0}}
        )
        logger.info("Reset daily reply counters")
    
    async def stop_monitoring(self):
        """Stop monitoring service"""
        self.is_running = False
        logger.info("Stopping monitoring service...")
