import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    # Facebook App Config
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
    FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
    
    # MongoDB Config
    MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'facebook_comment_assistant')
    
    # OpenAI Config (optional)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    USE_AI = os.getenv('USE_AI', 'False').lower() == 'true'
    
    # Rate Limiting
    MAX_REPLIES_PER_HOUR = int(os.getenv('MAX_REPLIES_PER_HOUR', '60'))
    DELAY_MIN = int(os.getenv('DELAY_MIN', '30'))
    DELAY_MAX = int(os.getenv('DELAY_MAX', '120'))
    
    # Monitoring
    MONITOR_INTERVAL = int(os.getenv('MONITOR_INTERVAL', '60'))  # seconds
    
    # API Config
    API_VERSION = 'v18.0'
    API_BASE_URL = f'https://graph.facebook.com/{API_VERSION}'
    
    # JWT Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

config = Config()
