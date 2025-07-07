import json
from typing import List
from core.state import EmailState
from utils.formatter import clean_email_body
from utils.logger import logger

def load_emails_from_json(file_path: str) -> List[EmailState]:
    """
    Loads email data from a JSON file and returns a list of EmailState objects.
    """
    logger.info(f"Loading emails from local JSON file: {file_path}")
    emails_list: List[EmailState] = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                cleaned_body = clean_email_body(item.get("body", ""))
                email_state = EmailState(
                    email_id=item.get("email_id", "local-id"),
                    subject=item.get("subject", ""),
                    sender=item.get("sender", ""),
                    body=item.get("body", ""),
                    cleaned_body=cleaned_body
                )
                emails_list.append(email_state)
        logger.info(f"Successfully loaded {len(emails_list)} emails from JSON.")
    except FileNotFoundError:
        logger.error(f"JSON file not found at {file_path}")
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {file_path}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        
    return emails_list