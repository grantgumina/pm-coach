from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBasicCredentials
import hmac
import hashlib
import json

app = FastAPI()

# Secret key for webhook validation
WEBHOOK_SECRET = "your_webhook_secret"

def verify_webhook_signature(request_body: bytes, signature: str):
    """Verify the webhook signature from Jira"""
    computed_hash = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        request_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_hash, signature)

@app.post("/webhook/jira")
async def jira_webhook(request: Request):
    # Get the raw request body
    body = await request.body()
    
    # Verify webhook signature (if configured in Jira)
    signature = request.headers.get("X-Hub-Signature-256")
    if signature and not verify_webhook_signature(body, signature.split('=')[1]):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse the webhook payload
    event = json.loads(body)
    
    # Process the event based on the webhook type
    if event['webhookEvent'] == 'jira:issue_created':
        await process_new_ticket(event['issue'])
    
    return {"status": "success"} 