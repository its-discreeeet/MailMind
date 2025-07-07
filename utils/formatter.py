import re
from bs4 import BeautifulSoup

def clean_email_body(body: str) -> str:
    """
    Cleans email body by removing HTML tags and extra whitespace.
    """
    if not body:
        return ""
    
    # Use BeautifulSoup to parse HTML and get text
    soup = BeautifulSoup(body, "html.parser")
    text = soup.get_text()
    
    # Remove excessive newlines and whitespace
    text = re.sub(r'\s*\n\s*', '\n', text).strip()
    text = re.sub(r'[ \t]{2,}', ' ', text)
    
    return text

def format_email_preview(subject: str, sender: str, body: str, max_len: int = 100) -> str:
    """
    Formats a short preview of an email.
    """
    body_preview = (body[:max_len] + '...') if len(body) > max_len else body
    return f"From: {sender}\nSubject: {subject}\nBody: {body_preview.replace(chr(10), ' ')}"