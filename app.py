from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBasicCredentials
import hmac
import hashlib
import json
import logging
from typing import Dict
from ticket_processor import TicketAnalyzer
from config import get_settings

app = FastAPI()
settings = get_settings()
logger = logging.getLogger(__name__)

@app.post("/")
async def jira_webhook(request: Request):
    """Handle incoming Jira webhook events"""
    try:
        # Get the raw request body
        body = await request.body()
        
        # Verify webhook signature (if configured in Jira)
        signature = request.headers.get("X-Hub-Signature-256")
        if signature and not verify_webhook_signature(body, signature.split('=')[1]):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse the webhook payload
        event = json.loads(body)
        
        # If the ticket is updated and has been marked as "Ready for Kickoff"
        if (event['webhookEvent'] == 'jira:issue_updated' 
            and 'status' in event['changelog']['items'][0]['field'] 
            and event['changelog']['items'][0]['to'] == '12809'):
            
            logger.info(f"Ticket was marked as Ready for Kickoff. Analyzing...")

            analyzer = TicketAnalyzer()
            await analyzer.process_ticket(event['issue'])

        # If someone has tagged the PM coach in a comment - read and respond
        if event['webhookEvent'] == 'comment_created':
            # TODO - use OpenAI to read the comment and respond
            pass

        return {"status": "success", "message": "Webhook processed successfully"}
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON payload received")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def verify_webhook_signature(request_body: bytes, signature: str) -> bool:
    """Verify the webhook signature from Jira"""
    computed_hash = hmac.new(
        settings.WEBHOOK_SECRET.encode('utf-8'),
        request_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_hash, signature)

# Add logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) 