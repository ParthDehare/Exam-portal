import smtplib
from email.message import EmailMessage
import logging
from config import settings
import asyncio

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # We can add these to config.py later if the user provides real credentials
        self.smtp_server = getattr(settings, 'smtp_server', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_user = getattr(settings, 'smtp_user', '')
        self.smtp_pass = getattr(settings, 'smtp_pass', '')

    def _send_sync(self, to_email: str, subject: str, html_content: str):
        if not self.smtp_user or not self.smtp_pass:
            logger.info(f"[MOCK EMAIL] To: {to_email} | Subject: {subject}")
            logger.debug(f"[MOCK EMAIL CONTENT]\n{html_content}")
            return

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.smtp_user
        msg['To'] = to_email
        msg.add_alternative(html_content, subtype='html')

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            logger.info(f"Email sent successfully to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")

    async def send_email(self, to_email: str, subject: str, html_content: str):
        # Run synchronous SMTP code in a thread pool to avoid blocking FastAPI
        await asyncio.to_thread(self._send_sync, to_email, subject, html_content)

email_service = EmailService()
