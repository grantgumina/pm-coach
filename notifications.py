from email.mime.text import MIMEText
import smtplib
import asyncio

async def add_feedback_comment(issue_key: str, feedback: str):
    """Add feedback as a comment on the Jira ticket"""
    jira = JIRA(
        server='https://your-domain.atlassian.net',
        basic_auth=('your_email', 'your_api_token')
    )
    
    comment_body = f"""
    🤖 Automated Ticket Review
    
    {feedback}
    
    This is an automated message. Please improve the ticket based on the feedback above.
    """
    
    jira.add_comment(issue_key, comment_body)

async def notify_pm(reporter: Dict, feedback: str, issue_key: str):
    """Send email notification to the PM"""
    sender = "bot@yourcompany.com"
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
    
    # Send email (implement your email sending logic here)
    # This is a simplified example
    with smtplib.SMTP('smtp.yourcompany.com') as server:
        server.send_message(msg) 