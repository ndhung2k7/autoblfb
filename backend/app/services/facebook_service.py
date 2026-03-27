import requests
import aiohttp
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..config import config
from ..models.page import FacebookPage
from ..models.comment import Comment

class FacebookService:
    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.app_access_token = f"{config.FACEBOOK_APP_ID}|{config.FACEBOOK_APP_SECRET}"
    
    async def get_page_posts(self, page_id: str, access_token: str, limit: int = 10) -> List[Dict]:
        """Get latest posts from a Facebook page"""
        url = f"{self.base_url}/{page_id}/posts"
        params = {
            'access_token': access_token,
            'fields': 'id,message,created_time,comments.limit(50){id,message,from,created_time}',
            'limit': limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                else:
                    error_text = await response.text()
                    raise Exception(f"Error fetching posts: {error_text}")
    
    async def get_new_comments(self, page: FacebookPage, last_comment_time: Optional[datetime] = None) -> List[Comment]:
        """Get new comments from a page's posts"""
        try:
            posts = await self.get_page_posts(page.page_id, page.access_token)
            new_comments = []
            
            for post in posts:
                if 'comments' in post and 'data' in post['comments']:
                    for comment_data in post['comments']['data']:
                        comment_time = datetime.strptime(comment_data['created_time'], 
                                                        '%Y-%m-%dT%H:%M:%S%z')
                        
                        # Only get comments after last processed time
                        if last_comment_time and comment_time <= last_comment_time:
                            continue
                        
                        comment = Comment(
                            page_id=page.page_id,
                            post_id=post['id'],
                            comment_id=comment_data['id'],
                            user_id=comment_data['from']['id'],
                            user_name=comment_data['from']['name'],
                            message=comment_data['message'],
                            created_time=comment_time
                        )
                        new_comments.append(comment)
            
            return new_comments
        except Exception as e:
            print(f"Error getting new comments for page {page.page_name}: {str(e)}")
            return []
    
    async def reply_to_comment(self, comment_id: str, message: str, access_token: str) -> bool:
        """Reply to a comment"""
        url = f"{self.base_url}/{comment_id}"
        params = {
            'access_token': access_token,
            'message': message
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                if response.status == 200:
                    return True
                else:
                    error_text = await response.text()
                    print(f"Error replying to comment: {error_text}")
                    return False
    
    async def validate_token(self, access_token: str) -> bool:
        """Validate Facebook access token"""
        url = f"{self.base_url}/me"
        params = {
            'access_token': access_token,
            'fields': 'id,name'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return response.status == 200
    
    async def get_page_info(self, page_id: str, access_token: str) -> Dict:
        """Get page information"""
        url = f"{self.base_url}/{page_id}"
        params = {
            'access_token': access_token,
            'fields': 'id,name,category,fan_count'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
