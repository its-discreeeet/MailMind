from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek
from utils.logger import logger
from core.state import EmailState

def generate_response(state: EmailState, llm: ChatDeepSeek) -> dict:
    """
    Generates a draft response for an email based on its content and summary.
    """
    if state.category not in ["urgent", "needs_review"]:
        logger.info(f"Skipping response generation for email ID: {state.email_id} (Category: {state.category})")
        return {"status": "processed"}

    logger.info(f"Generating response for email ID: {state.email_id}")
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
             "You are a professional and helpful email assistant. Your task is to draft a response to the following email. "
             "The response should be polite, professional, and address the main points of the email. "
             "Based on the content, decide if the generated draft is simple enough for immediate sending or if it requires human review. "
             "If the query is complex, sensitive, or requires information you don't have, flag it for human review. "
             "Provide ONLY the email body as a response, nothing else."
            ),
            ("human", 
             "Here is the email to respond to:\n"
             "Sender: {sender}\n"
             "Subject: {subject}\n"
             "Body:\n{body}\n\n"
             "A summary of the email is: {summary}\n\n"
             "Please draft a response."
            ),
        ]
    )
    
    chain = prompt | llm

    try:
        response = chain.invoke({
            "sender": state.sender,
            "subject": state.subject,
            "body": state.cleaned_body,
            "summary": state.summary
        })
        draft = response.content

        # Simple logic to decide if review is needed. More complex logic can be added.
        review_keywords = ["confirm", "password", "invoice", "urgent", "complaint", "issue"]
        needs_review = any(keyword in state.subject.lower() or keyword in state.cleaned_body.lower() for keyword in review_keywords)
        
        # Always flag 'needs_review' category for review
        if state.category == "needs_review":
            needs_review = True
            
        logger.info(f"Generated draft for email {state.email_id}. Needs review: {needs_review}")
        return {"draft_response": draft, "needs_human_review": needs_review}
    except Exception as e:
        logger.error(f"Error generating response for email {state.email_id}: {e}")
        return {"draft_response": "Error during response generation.", "needs_human_review": True}