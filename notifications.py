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
    print(dir(issue.fields.reporter))
    reporter_id = issue.fields.reporter.accountId
    
    # Format the mention using Jira's [~username] syntax
    reporter_mention = f"[~accountid:{reporter_id}]"
    print(reporter_mention)

    comment_body = f"""
    🤖 Automated Ticket Review
    
    {feedback}
    
    // cc {reporter_mention}
    """

    print(comment_body)
    
    jira.add_comment(issue_key, comment_body)
