from supabase import create_client
from config import get_settings
from typing import Optional, List, Dict

settings = get_settings()

class SupabaseManager:
    def __init__(self):
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        
    async def store_ticket_feedback(self, 
                                  ticket_key: str, 
                                  description: str, 
                                  feedback: str,
                                  version: int = 1) -> None:
        """Store ticket feedback and description in Supabase"""
        data = {
            'ticket_key': ticket_key,
            'description': description,
            'feedback': feedback,
            'version': version
        }
        self.client.table('ticket_history').insert(data).execute()

    async def get_ticket_history(self, ticket_key: str) -> List[Dict]:
        """Retrieve previous versions of a ticket"""
        response = self.client.table('ticket_history')\
            .select('*')\
            .eq('ticket_key', ticket_key)\
            .order('version', desc=True)\
            .execute()
        return response.data

    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding using OpenAI API"""
        response = await openai.Embedding.acreate(
            input=text,
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']

    async def search_similar_tickets(self, 
                                   description: str, 
                                   limit: int = 5) -> List[Dict]:
        """Search for similar tickets using embeddings"""
        embedding = await self.create_embedding(description)
        response = self.client.rpc(
            'match_tickets',
            {'query_embedding': embedding, 'match_threshold': 0.7, 'match_count': limit}
        ).execute()
        return response.data 