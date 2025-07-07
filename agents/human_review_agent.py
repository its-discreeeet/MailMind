from utils.logger import logger
from core.state import EmailState

def review_draft(state: EmailState) -> dict:
    """
    Prompts a human user to review, edit, or reject a drafted email response.
    """
    logger.info(f"Awaiting human review for email ID: {state.email_id}")
    
    print("\n" + "="*50)
    print("🕵️  HUMAN REVIEW REQUIRED 🕵️")
    print("="*50)
    print(f"From: {state.sender}")
    print(f"Subject: {state.subject}")
    print("-" * 20 + " Email Body " + "-"*20)
    print(state.cleaned_body)
    print("-" * 20 + " Draft Response " + "-"*18)
    print(state.draft_response)
    print("="*50)

    while True:
        action = input("Choose action: [A]pprove, [E]dit, [R]eject: ").strip().lower()
        if action in ['a', 'e', 'r']:
            break
        print("Invalid choice. Please enter 'A', 'E', or 'R'.")

    if action == 'a':
        logger.info(f"Draft for email {state.email_id} approved by user.")
        return {"final_response": state.draft_response, "status": "approved_for_sending"}
    elif action == 'r':
        logger.warning(f"Draft for email {state.email_id} rejected by user.")
        return {"final_response": None, "status": "rejected"}
    elif action == 'e':
        print("Enter your revised draft. Press Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) when done.")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            pass
        
        edited_draft = "\n".join(lines)
        logger.info(f"Draft for email {state.email_id} edited by user.")
        return {"final_response": edited_draft, "status": "approved_for_sending"}

    return {}