from typing import Dict
import asyncio
from jira import JIRA
from config import get_settings
import logging
from notifications import add_feedback_comment

logger = logging.getLogger(__name__)

class TicketAnalyzer:
    def __init__(self):
        self.settings = get_settings()
        self.jira = JIRA(
            server=self.settings.JIRA_SERVER,
            basic_auth=(self.settings.JIRA_EMAIL, self.settings.JIRA_API_TOKEN)
        )
        
    async def process_ticket(self, issue: Dict) -> None:
        """
        Process a newly created Jira ticket
        
        Args:
            issue: Dictionary containing the Jira issue data
        """
        try:
            # Get ticket details for logging
            ticket_key = issue['key']
            reporter = issue['fields']['reporter']
            
            logger.info(f"Processing new ticket {ticket_key}")
            
            # Analyze the ticket for basic hygiene (mandantory fields filled in)
            feedback = await self.basic_ticket_check(issue)

            # TODO - read the description with OpenAI and provide feedback
            
            # Add comment with feedback to the ticket
            try:
                await add_feedback_comment(ticket_key, feedback)
                logger.info(f"Feedback added to ticket {ticket_key}")
            except Exception as e:
                logger.error(f"Failed to add comment to ticket {ticket_key}: {str(e)}")
                        
            logger.info(f"Successfully processed ticket {ticket_key}")
            
        except Exception as e:
            logger.error(f"Error processing ticket: {str(e)}")
            raise

    async def basic_ticket_check(self, issue: Dict) -> str:
        """Analyze a ticket and return feedback"""
        feedback = []
        
        # Check description
        if not issue['fields']['description']:
            feedback.append("❌ Description is missing")
        else:
            # if the description is not empty, then we need to read it with OpenAI and provide feedback
            pass
            
        # Check quarter
        if not issue['fields'].get('customfield_17052'):
            feedback.append("❌ Quarter not specified")
            
        # Check launch tier
        if issue['fields'].get('customfield_17213') is None:
            feedback.append("❌ Launch tier not specified")
            
        # Check product area
        if issue['fields'].get('customfield_17069') is None:
            feedback.append("❌ Product area not specified")
            
        # Check SKU
        if issue['fields'].get('customfield_17113') is None:
            feedback.append("❌ SKU not specified")
            
        # Check layer cake assignment
        if issue['fields'].get('customfield_17099') is None:
            feedback.append("❌ Layer cake classification missing")
            
        return "\n".join(feedback) if feedback else "✅ Ticket looks good!"
    