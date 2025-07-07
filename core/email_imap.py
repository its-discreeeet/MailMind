import imaplib
import email
from email.header import decode_header
from typing import List, Optional
from core.state import EmailState
from utils.formatter import clean_email_body
from utils.logger import logger
import config

def _decode_header_safely(header_value) -> str:
    """
    Safely decodes an email header, handling different character sets.
    """
    if not header_value:
        return ""
    
    decoded_parts = []
    for part, charset in decode_header(header_value):
        if isinstance(part, bytes):
            # If charset is None, guess common encodings. Fallback to a forgiving one.
            try:
                decoded_parts.append(part.decode(charset or 'utf-8', errors='replace'))
            except (UnicodeDecodeError, LookupError):
                decoded_parts.append(part.decode('latin-1', errors='replace'))
        else:
            decoded_parts.append(part)
            
    return "".join(decoded_parts)

def fetch_unread_emails() -> List[EmailState]:
    """
    Fetches unread emails from the configured IMAP server with robust encoding handling.
    """
    emails_list: List[EmailState] = []
    try:
        logger.info(f"Connecting to IMAP server: {config.IMAP_SERVER}")
        mail = imaplib.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_PORT)
        mail.login(config.IMAP_USERNAME, config.IMAP_PASSWORD)
        
        mail.select("inbox")
        
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            logger.error("Failed to search for emails.")
            return []
            
        email_ids = messages[0].split()
        if not email_ids:
            logger.info("No unread emails found.")
            mail.logout()
            return []
            
        logger.info(f"Found {len(email_ids)} unread emails.")

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                logger.error(f"Failed to fetch email with ID {email_id.decode()}.")
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Safely decode subject and sender
                    subject = _decode_header_safely(msg["Subject"])
                    sender = _decode_header_safely(msg.get("From"))

                    # Get email body with proper decoding
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            
                            if "attachment" in content_disposition:
                                continue

                            if content_type in ["text/plain", "text/html"]:
                                try:
                                    payload = part.get_payload(decode=True)
                                    charset = part.get_content_charset()
                                    if charset:
                                        body = payload.decode(charset, errors='replace')
                                    else:
                                        # If no charset, try utf-8 then latin-1 as a fallback
                                        try:
                                            body = payload.decode('utf-8', errors='strict')
                                        except UnicodeDecodeError:
                                            body = payload.decode('latin-1', errors='replace')
                                    if content_type == "text/plain":
                                        break # Prefer plain text
                                except Exception as e:
                                    logger.warning(f"Could not decode part of email {email_id.decode()}: {e}")

                    else:
                        # Not a multipart email, just get the payload
                        try:
                            payload = msg.get_payload(decode=True)
                            charset = msg.get_content_charset()
                            if charset:
                                body = payload.decode(charset, errors='replace')
                            else:
                                try:
                                    body = payload.decode('utf-8', errors='strict')
                                except UnicodeDecodeError:
                                    body = payload.decode('latin-1', errors='replace')
                        except Exception as e:
                            logger.warning(f"Could not decode payload of email {email_id.decode()}: {e}")

                    cleaned_body = clean_email_body(body)

                    email_state = EmailState(
                        email_id=email_id.decode(),
                        subject=subject,
                        sender=sender,
                        body=body,
                        cleaned_body=cleaned_body,
                    )
                    emails_list.append(email_state)
                    logger.info(f"Successfully parsed email from {sender} with subject '{subject}'")

        mail.logout()
        return emails_list

    except Exception as e:
        logger.error(f"An error occurred while fetching emails: {e}")
        return []