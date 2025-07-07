import os
from core.email_ingestion import load_emails_from_json
from core.email_imap import fetch_unread_emails
from core.email_sender import send_email, save_draft
from core.supervisor import EmailSupervisor
from utils.logger import logger
from utils.formatter import format_email_preview
import config

def main():
    """
    Main function to run the email assistant.
    """
    logger.info("🚀 Starting AI Email Assistant...")

    # Ensure drafts directory exists
    if not os.path.exists('drafts'):
        os.makedirs('drafts')

    # Choose ingestion method
    use_imap = input("Use live IMAP to fetch emails? (y/n): ").strip().lower() == 'y'
    
    if use_imap:
        if not all([config.IMAP_SERVER, config.IMAP_USERNAME, config.IMAP_PASSWORD]):
            logger.error("IMAP credentials are not configured. Exiting.")
            return
        emails = fetch_unread_emails()
    else:
        emails = load_emails_from_json("sample_emails.json")
    
    if not emails:
        logger.info("No emails to process. Exiting.")
        return

    logger.info(f"Found {len(emails)} emails to process.")
    
    # Initialize the supervisor
    supervisor = EmailSupervisor()
    
    for email_state in emails:
        print("\n" + "#"*70)
        logger.info(f"Processing email: {format_email_preview(email_state.subject, email_state.sender, email_state.cleaned_body)}")
        
        # Run the email through the state graph
        final_state = supervisor.process_email(email_state)

        logger.info(f"Finished processing email ID {final_state.email_id}. Final status: {final_state.status}")
        
        # Post-processing actions
        if final_state.status == "approved_for_sending" and final_state.final_response:
            print("\n" + "-"*50)
            print("📧 Action: Send Email")
            print(f"To: {final_state.sender}")
            print(f"Subject: Re: {final_state.subject}")
            print("Body:\n" + final_state.final_response)
            print("-" * 50)
            
            confirm_send = input("Confirm sending this email? (y/n): ").strip().lower()
            if confirm_send == 'y':
                send_email(
                    to_email=final_state.sender,
                    subject=f"Re: {final_state.subject}",
                    body=final_state.final_response
                )
            else:
                logger.warning("Sending cancelled by user.")
                draft_filename = f"{final_state.email_id}_draft.txt"
                save_draft(
                    subject=f"Re: {final_state.subject}",
                    body=final_state.final_response,
                    filename=draft_filename
                )
        elif final_state.status == "rejected":
            logger.info(f"Email {final_state.email_id} was rejected during review. No action taken.")
        else:
            logger.info(f"No response generated for email {final_state.email_id}. (Category: {final_state.category})")

    logger.info("✅ All emails processed. System shutting down.")

if __name__ == "__main__":
    main()