from typing import Dict
import asyncio
from jira import JIRA
from config import get_settings
import logging
from notifications import add_feedback_comment
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

class TicketAnalyzer:
    def __init__(self):
        self.settings = get_settings()
        self.jira = JIRA(
            server=self.settings.JIRA_SERVER,
            basic_auth=(self.settings.JIRA_EMAIL, self.settings.JIRA_API_TOKEN)
        )
        self.llm = ChatOpenAI(temperature=0, openai_api_key=self.settings.OPENAI_API_KEY)

    async def analyze_prfaq(self, description: str) -> str:
        """
        Analyze a PRFAQ document and provide detailed feedback
        """
        template = """You are an expert at reviewing PRFAQ (Press Release/FAQ) documents. 
        Analyze the following PRFAQ and provide specific, actionable feedback to improve it. 
        For each issue identified, include a concrete example of how it could be better.

        Focus on:
        - Clarity of the customer benefit
        - Specificity of the solution
        - Are artifacts like links to Google Docs or mockups included. Look specifically for "google.com" 
        and "figma.com" links. If any are included, assume you don't need to comment on this evaluation criteria.
        - Included customer quotes and testimonials
        - Measurable outcomes and success metrics

        If each of these criteria are met, feel free to say nothing.'
        
        PRFAQ:
        {description}

        Just put your feedback here. Don't add any headings or summary up front. 
        Provide a concise easy to read summary of the feedback, using markdown formatting and bold 
        important sentences which possibly summarize your bullet points."""

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        result = await chain.ainvoke({"description": description})
        return result.content

    async def analyze_prfaq_with_history(self, 
                                       ticket_key: str, 
                                       current_description: str) -> str:
        """
        Analyze PRFAQ with historical context
        """
        # Get ticket history
        history = await self.supabase.get_ticket_history(ticket_key)
        
        # Find similar tickets
        similar_tickets = await self.supabase.search_similar_tickets(current_description)
        
        template = """You are an expert at reviewing PRFAQ documents.
        
        {history_context}
        
        {similar_tickets_context}
        
        Analyze the following PRFAQ and provide specific, actionable feedback to improve it.
        
        Current PRFAQ:
        {description}
        
        Focus on:
        - Clarity of the customer benefit
        - Specificity of the solution
        - Are artifacts like links to Google Docs or mockups included. Look specifically for "google.com" 
        and "figma.com" links. If any are included, assume you don't need to comment on this evaluation criteria.
        - Included customer quotes and testimonials
        - Measurable outcomes and success metrics
        
        Provide feedback in this format:
        1. Previous Feedback Status (if applicable)
        2. Improvements from Last Version (if applicable)
        3. New Feedback Points
        """
        
        # Prepare context from history
        history_context = ""
        if history:
            previous_version = history[0]  # Most recent version
            history_context = f"""
            Previous version feedback:
            {previous_version['feedback']}
            
            Previous description:
            {previous_version['description']}
            """
            
        # Prepare context from similar tickets
        similar_tickets_context = ""
        if similar_tickets:
            similar_tickets_context = "Similar successful PRFAQs patterns:\n"
            for ticket in similar_tickets:
                similar_tickets_context += f"- {ticket['key']}: {ticket['summary']}\n"
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm
        
        result = await chain.ainvoke({
            "description": current_description,
            "history_context": history_context,
            "similar_tickets_context": similar_tickets_context
        })
        
        return result.content


    async def process_ticket(self, issue: Dict) -> None:
        try:
            ticket_key = issue['key']
            reporter = issue['fields']['reporter']
            
            logger.info(f"Processing new ticket {ticket_key}")
            
            # Analyze the ticket for basic hygiene
            feedback = await self.basic_ticket_check(issue)
            feedback_points = feedback.split('\n')

            # Analyze PRFAQ with LangChain
            description = issue['fields']['description']
            if description and "❌" not in feedback:
                try:
                    prfaq_feedback = await self.analyze_prfaq(description)
                    feedback_points.append("\nPRFAQ Analysis:")
                    feedback_points.append(prfaq_feedback)
                except Exception as e:
                    logger.error(f"Failed to analyze PRFAQ: {str(e)}")
                    feedback_points.append("\n⚠️ Unable to analyze PRFAQ content. Please ensure it follows the PRFAQ format.")
            
            # Join all feedback points
            final_feedback = "\n".join(feedback_points)
            
            # Add comment with feedback
            try:
                await add_feedback_comment(ticket_key, final_feedback)
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
        
        # Check assignee
        if issue['fields']['assignee'] is None:
            feedback.append("❌ Assignee is missing")

        # Check description
        if not issue['fields']['description']:
            feedback.append("❌ Description is missing")
            
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
            
        return "\n".join(feedback) if feedback else "✅ All required fields are filled out."
    