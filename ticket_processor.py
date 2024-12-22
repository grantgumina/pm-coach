from typing import Dict
import asyncio
from jira import JIRA

class TicketAnalyzer:
    def __init__(self):
        self.jira = JIRA(
            server='https://your-domain.atlassian.net',
            basic_auth=('your_email', 'your_api_token')
        )
        
    async def analyze_ticket(self, issue: Dict) -> str:
        """Analyze a ticket and return feedback"""
        feedback = []
        
        # Check description
        if not issue['fields']['description']:
            feedback.append("❌ Description is missing")
            
        # Check acceptance criteria
        if not self._has_acceptance_criteria(issue):
            feedback.append("❌ Acceptance criteria not found")
            
        # Check story points
        if not issue['fields'].get('customfield_10026'):  # Story points field
            feedback.append("❌ Story points not estimated")
            
        # Check for attachments if needed
        if self._needs_attachments(issue) and not issue['fields']['attachment']:
            feedback.append("⚠️ Consider adding mockups or diagrams")
            
        return "\n".join(feedback) if feedback else "✅ Ticket looks good!"
    
    def _has_acceptance_criteria(self, issue: Dict) -> bool:
        """Check if the ticket has acceptance criteria"""
        description = issue['fields']['description'] or ""
        return "acceptance criteria" in description.lower()
    
    def _needs_attachments(self, issue: Dict) -> bool:
        """Determine if the ticket type typically needs attachments"""
        return issue['fields']['issuetype']['name'] in ['Story', 'New Feature']

async def process_new_ticket(issue: Dict):
    """Process a newly created ticket"""
    analyzer = TicketAnalyzer()
    
    # Analyze the ticket
    feedback = await analyzer.analyze_ticket(issue)
    
    # Add comment with feedback
    await add_feedback_comment(issue['key'], feedback)
    
    # Notify PM via email if there are issues
    if "❌" in feedback:
        await notify_pm(issue['fields']['reporter'], feedback, issue['key']) 