import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional
from ..models.comment import Comment, ProcessedUser
from ..models.reply_template import ReplyTemplate
from ..services.facebook_service import FacebookService
from ..services.ai_service import AIService
from ..utils.rate_limiter import RateLimiter
from ..utils.logger import logger

class ReplyService:
    def __init__(self, db):
        self.db = db
        self.facebook_service = FacebookService()
        self.ai_service = AIService()
        self.rate_limiter = RateLimiter()
        self.processed_users = {}  # In-memory cache, should use Redis in production
    
    async def process_new_comments(self, page) -> List[Comment]:
        """Process new comments for a page"""
        # Get last processed comment time
        last_comment = await self.db.comments.find_one(
            {'page_id': page.page_id},
            sort=[('created_time', -1)]
        )
        last_time = last_comment['created_time'] if last_comment else None
        
        # Fetch new comments
        new_comments = await self.facebook_service.get_new_comments(page, last_time)
        
        for comment in new_comments:
            # Check if already processed
            existing = await self.db.comments.find_one({'comment_id': comment.comment_id})
            if existing:
                continue
            
            # Save comment to database
            await self.db.comments.insert_one(comment.dict())
            
            # Check if we should reply
            if page.auto_reply_enabled and await self.should_reply_to_comment(comment, page):
                # Process with delay
                asyncio.create_task(self.reply_with_delay(comment, page))
        
        return new_comments
    
    async def should_reply_to_comment(self, comment: Comment, page) -> bool:
        """Check if we should reply to this comment"""
        # Check if already replied to this user recently
        user_key = f"{page.page_id}_{comment.user_id}"
        if user_key in self.processed_users:
            last_reply = self.processed_users[user_key]
            if datetime.utcnow() - last_reply < timedelta(hours=1):
                logger.info(f"Skip replying to user {comment.user_name} - replied within 1 hour")
                return False
        
        # Check rate limit
        if not self.rate_limiter.can_reply(page.page_id, page.rate_limit_hour):
            logger.warning(f"Rate limit reached for page {page.page_name}")
            return False
        
        # Check for spam keywords
        spam_keywords = ['spam', 'viagra', 'casino', 'lottery']
        if any(keyword in comment.message.lower() for keyword in spam_keywords):
            logger.info(f"Skipping spam comment: {comment.message[:50]}")
            return False
        
        return True
    
    async def reply_with_delay(self, comment: Comment, page):
        """Reply to comment with random delay"""
        # Random delay between 30-120 seconds
        delay = random.randint(config.DELAY_MIN, config.DELAY_MAX)
        logger.info(f"Will reply to comment {comment.comment_id} in {delay} seconds")
        await asyncio.sleep(delay)
        
        # Select reply template
        reply_text = await self.select_reply_template(comment, page)
        
        if reply_text:
            # Send reply
            success = await self.facebook_service.reply_to_comment(
                comment.comment_id,
                reply_text,
                page.access_token
            )
            
            if success:
                # Update comment record
                await self.db.comments.update_one(
                    {'comment_id': comment.comment_id},
                    {
                        '$set': {
                            'replied': True,
                            'replied_time': datetime.utcnow(),
                            'reply_message': reply_text
                        }
                    }
                )
                
                # Update processed users
                user_key = f"{page.page_id}_{comment.user_id}"
                self.processed_users[user_key] = datetime.utcnow()
                
                # Update page stats
                await self.db.pages.update_one(
                    {'page_id': page.page_id},
                    {
                        '$inc': {'replies_count_today': 1},
                        '$set': {'last_reply_time': datetime.utcnow()}
                    }
                )
                
                logger.info(f"Successfully replied to comment {comment.comment_id}")
            else:
                logger.error(f"Failed to reply to comment {comment.comment_id}")
    
    async def select_reply_template(self, comment: Comment, page) -> str:
        """Select appropriate reply template based on comment analysis"""
        # Analyze comment with AI
        analysis = await self.ai_service.analyze_comment(comment.message)
        
        # Get templates from database
        templates = await self.db.reply_templates.find({
            'page_id': page.page_id,
            'is_active': True
        }).to_list(length=100)
        
        # Filter templates by intent
        intent = analysis.get('intent', 'general')
        filtered_templates = [t for t in templates if t['template_type'] == intent]
        
        if not filtered_templates:
            filtered_templates = [t for t in templates if t['template_type'] == 'general']
        
        if not filtered_templates:
            return "Cảm ơn bạn đã bình luận! Chúng tôi sẽ phản hồi sớm nhất có thể."
        
        # Select random template
        import random
        selected = random.choice(filtered_templates)
        
        # Use AI to generate personalized reply if available
        if self.ai_service.enabled:
            ai_reply = await self.ai_service.generate_reply(
                comment.message,
                [t['content'] for t in filtered_templates[:5]],
                analysis
            )
            if ai_reply:
                return ai_reply
        
        return selected['content']
