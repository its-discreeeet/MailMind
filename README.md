# MailMind-Email-with-a-mind-of-its-own.

## 🧠 AI-Powered Email Assistant

An automated, multi-agent email processing system built with Python, LangGraph, and the Deepseek LLM API. This assistant can fetch, filter, summarize, and draft replies to your emails, with a human-in-the-loop for final approval.

✨ Core Features
📧 Automated Email Fetching: Connects to any IMAP server to fetch unread emails in real-time.
🧪 Local Testing Mode: Ingest emails from a sample_emails.json file for development without live credentials.
🤖 AI-Powered Classification: Uses Deepseek's LLM to intelligently categorize emails into spam, urgent, informational, or needs_review.
📝 Concise Summarization: Generates short, 2-3 sentence summaries for long emails, helping you grasp the context quickly.
✍️ Automatic Response Generation: Drafts professional, context-aware replies to emails that require action.
🧠 Stateful Agent Workflow: Orchestrated by LangGraph, the system processes each email through a resilient, state-driven graph of agents.
🕵️ Human-in-the-Loop: Ensures control by flagging complex or sensitive drafts for human review. You can approve, edit, or reject any AI-generated response.
📤 SMTP Integration: Sends approved emails automatically via your configured SMTP server.
Robust Logging & Error Handling: Provides detailed logs for each step and gracefully handles common issues like API errors or email parsing failures.

## ⚙️ How It Works: The Workflow

The system processes each email through a state graph managed by LangGraph. Each node in the graph is an "agent" with a specific task.

![Untitled diagram _ Mermaid Chart-2025-07-07-221530](https://github.com/user-attachments/assets/3ddd366f-8d78-4a00-a691-c5a80e60ef5a)


## 🛠️ Tech Stack
Orchestration: LangGraph
Language Model: Deepseek API via langchain-deepseek
Core Framework: LangChain
Data Validation: Pydantic
Email Integration: imaplib2 (fetching), smtplib (sending)
Configuration: python-dotenv

## 🗂️ Project Structure

├── agents/              # Contains individual agent logic

├── config.py            # Loads environment variables

├── core/                # Core components (state, supervisor, email handlers)

├── drafts/              # Stores saved draft responses

├── .env                 # Local environment variables (API keys, credentials)

├── main.py              # Main entry point for the application

├── requirements.txt     # Project dependencies

├── sample_emails.json   # Sample data for local testing

├── test_email.py        # Unit tests for the system

└── utils/               # Helper utilities (logger, formatter)


## 🚀 Getting Started
Follow these steps to set up and run the project on your local machine.

1. Prerequisites
Python 3.8 or higher
A Deepseek API Key.
An email account with IMAP and SMTP enabled.
Note for Gmail users: You will need to generate an "App Password" to use for EMAIL_PASSWORD and IMAP_PASSWORD. Your regular password will not work.

3. Installation
Clone the repository:
```
git clone https://github.com/your-username/ai-email-assistant.git
cd ai-email-assistant
```

Install the required dependencies:
```
pip install -r requirements.txt
```

### Deepseek API Configuration
DEEPSEEK_API_KEY="your_deepseek_api_key"

###  SMTP (Sending) Email Configuration
EMAIL_SERVER="smtp.gmail.com"
EMAIL_PORT=587
EMAIL_USERNAME="your.email@gmail.com"
EMAIL_PASSWORD="your_google_app_password"

###  IMAP (Fetching) Email Configuration
IMAP_SERVER="imap.gmail.com"
IMAP_PORT=993
IMAP_USERNAME="your.email@gmail.com"
IMAP_PASSWORD="your_google_app_password"

3. Running the Application
Execute the main script to start the email assistant:
```
python main.py
```
The program will ask whether you want to fetch live emails via IMAP or use the local sample_emails.json file for a dry run.
