import asyncio
from jira import JIRA
from config import get_settings

async def add_feedback_comment(issue_key: str, feedback: str):
    """Add feedback as a comment on the Jira ticket"""
    settings = get_settings()
    
    jira = JIRA(
        server=settings.JIRA_SERVER,
        basic_auth=(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
    )
    
    comment_body = f"""
    🤖 Automated Ticket Review
    
    {feedback}
    
    This is an automated message. Please improve the ticket based on the feedback above.
    """
    
    jira.add_comment(issue_key, comment_body)
