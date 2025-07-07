import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.logger import logger
import config

def send_email(to_email: str, subject: str, body: str):
    """
    Sends an email using the configured SMTP server.
    """
    if not all([config.EMAIL_SERVER, config.EMAIL_USERNAME, config.EMAIL_PASSWORD]):
        logger.error("SMTP configuration is incomplete. Cannot send email.")
        return

    msg = MIMEMultipart()
    msg['From'] = config.EMAIL_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        logger.info(f"Connecting to SMTP server {config.EMAIL_SERVER}:{config.EMAIL_PORT} to send email.")
        server = smtplib.SMTP(config.EMAIL_SERVER, config.EMAIL_PORT)
        server.starttls()  # Secure the connection
        server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(config.EMAIL_USERNAME, to_email, text)
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")

def save_draft(subject: str, body: str, filename: str):
    """
    Saves a draft response to the 'drafts/' directory.
    """
    try:
        with open(f"drafts/{filename}", "w") as f:
            f.write(f"Subject: {subject}\n\n{body}")
        logger.info(f"Draft saved to drafts/{filename}")
    except Exception as e:
        logger.error(f"Failed to save draft: {e}")