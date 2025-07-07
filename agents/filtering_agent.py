from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_deepseek import ChatDeepSeek
from utils.logger import logger
from core.state import EmailState

class EmailCategory(BaseModel):
    """Defines the category of the email."""
    category: str = Field(
        description="The category of the email. Must be one of: spam, urgent, informational, needs_review."
    )

def filter_email(state: EmailState, llm: ChatDeepSeek) -> dict:
    """
    Filters an email by classifying it into a category using the LLM.
    """
    logger.info(f"Filtering email ID: {state.email_id}")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert email classifier. Your task is to analyze an email and classify it into one of the following categories: "
                "'spam', 'urgent', 'informational', 'needs_review'. "
                "An email is 'urgent' if it requires an immediate response. "
                "It is 'informational' if it's a notification or update not requiring a reply. "
                "It 'needs_review' if it's a complex query that a human should handle. "
                "It is 'spam' if it is an unsolicited commercial email.",
            ),
            (
                "human",
                "Please classify the following email:\n"
                "Sender: {sender}\n"
                "Subject: {subject}\n"
                "Body:\n{body}",
            ),
        ]
    )

    structured_llm = llm.with_structured_output(EmailCategory)
    chain = prompt | structured_llm
    
    try:
        result = chain.invoke({
            "sender": state.sender,
            "subject": state.subject,
            "body": state.cleaned_body,
        })
        category = result.category
        logger.info(f"Email {state.email_id} classified as: {category}")
        return {"category": category}
    except Exception as e:
        logger.error(f"Error classifying email {state.email_id}: {e}")
        return {"category": "needs_review"} # Default to review on error