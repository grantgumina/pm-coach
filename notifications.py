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
    # Get the issue details to find the reporter
    issue = jira.issue(issue_key)
    
    # Find the Jira user ID to tag in the comment.
    # If the ticket is assigned to a user, tag them. 
    # Otherwise assume the reporter is the PM and tag them.
    if issue.fields.assignee is not None:
        cc_id = issue.fields.assignee.accountId
    else:
        cc_id = issue.fields.reporter.accountId
    
    # Format the mention using Jira's [~accountId] syntax
    cc_mention = f"[~accountid:{cc_id}]"

    comment_body = f"""
    🤖 Automated Ticket Review
    
    {feedback}
    
    // cc {cc_mention}
    """
    
    jira.add_comment(issue_key, comment_body)
