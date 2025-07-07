from pydantic import BaseModel, Field
from typing import List, Optional

class EmailState(BaseModel):
    """
    Represents the state of an email as it moves through the processing pipeline.
    """
    email_id: str
    subject: str
    sender: str
    body: str
    cleaned_body: str = ""
    category: str = "new"
    summary: str = ""
    draft_response: str = ""
    needs_human_review: bool = False
    final_response: Optional[str] = None
    status: str = "pending"  # e.g., pending, processed, rejected, sent