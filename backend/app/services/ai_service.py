import openai
from typing import Dict, List, Optional
from ..config import config

class AIService:
    def __init__(self):
        if config.USE_AI and config.OPENAI_API_KEY:
            openai.api_key = config.OPENAI_API_KEY
            self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            self.enabled = True
        else:
            self.enabled = False
    
    async def analyze_comment(self, comment_text: str) -> Dict:
        """Analyze comment sentiment and intent"""
        if not self.enabled:
            return {'sentiment': 'neutral', 'intent': 'general', 'confidence': 0.5}
        
        try:
            prompt = f"""
            Analyze this Facebook comment and provide:
            1. Sentiment (positive/neutral/negative/toxic)
            2. Intent (price_inquiry, info_request, complaint, spam, greeting, general)
            3. Key topics mentioned
            
            Comment: "{comment_text}"
            
            Return JSON format: {{"sentiment": "", "intent": "", "topics": [], "confidence": 0.0}}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Error analyzing comment: {str(e)}")
            return {'sentiment': 'neutral', 'intent': 'general', 'confidence': 0.5}
    
    async def generate_reply(self, comment_text: str, templates: List[str], context: Dict) -> Optional[str]:
        """Generate AI-powered reply based on templates"""
        if not self.enabled:
            return None
        
        try:
            prompt = f"""
            Comment: "{comment_text}"
            Sentiment: {context.get('sentiment', 'neutral')}
            Intent: {context.get('intent', 'general')}
            
            Available reply templates:
            {chr(10).join(f'- {t}' for t in templates[:5])}
            
            Generate a natural, helpful reply based on the comment and templates.
            Keep it concise and friendly.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating reply: {str(e)}")
            return None
