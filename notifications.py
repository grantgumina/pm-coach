from email.mime.text import MIMEText
import smtplib
import asyncio
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

async def notify_pm(reporter: Dict, feedback: str, issue_key: str):
    """Send email notification to the PM"""
    settings = get_settings()
    sender = settings.BOT_EMAIL
    msg = MIMEText(f"""
    Hello {reporter['displayName']},
    
    Your Jira ticket {issue_key} needs some improvements:
    
    {feedback}
    
    Please update the ticket accordingly.
    
    Best regards,
    Ticket Review Bot
    """)
    
    msg['Subject'] = f'Feedback for Jira ticket {issue_key}'
    msg['From'] = sender
    msg['To'] = reporter['emailAddress']
    
    # Updated SMTP connection
    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg) 