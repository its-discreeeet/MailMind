import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Deepseek API Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# SMTP (Sending) Email Configuration
EMAIL_SERVER = os.getenv("EMAIL_SERVER")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# IMAP (Fetching) Email Configuration
IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
IMAP_USERNAME = os.getenv("IMAP_USERNAME")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")

# Basic validation
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found in environment variables.")
if not EMAIL_USERNAME or not EMAIL_PASSWORD:
    print("Warning: Email credentials not found. Sending/fetching emails will fail.")