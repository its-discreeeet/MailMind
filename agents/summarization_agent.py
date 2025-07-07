from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek
from utils.logger import logger
from core.state import EmailState

def summarize_email(state: EmailState, llm: ChatDeepSeek) -> dict:
    """
    Summarizes the content of an email.
    """
    if state.category == "spam":
        logger.info(f"Skipping summarization for spam email ID: {state.email_id}")
        return {}

    logger.info(f"Summarizing email ID: {state.email_id}")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert at summarizing emails. Generate a concise, 2-3 sentence summary of the following email content."),
            ("human", "Email Body:\n{body}"),
        ]
    )

    chain = prompt | llm
    
    try:
        response = chain.invoke({"body": state.cleaned_body})
        summary = response.content
        logger.info(f"Generated summary for email {state.email_id}: {summary}")
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error summarizing email {state.email_id}: {e}")
        return {"summary": "Error during summarization."}