from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

from models.result import ToolResult, ErrorInfo
from utils import errors
from settings import Settings


class EmailService:
    def __init__(self, settings: Settings):
        self.settings = settings
        
        
    def send(self, to: str, subject: str, body: str) -> ToolResult:
        if not all([self.settings.SMTP_HOST, self.settings.SMTP_USERNAME, self.settings.SMTP_PASSWORD, self.settings.FROM_EMAIL]):
            return ToolResult(
                ok=False,
                error=ErrorInfo(
                    code=errors.EMAIL_CONFIG_MISSING,
                    message="Email settings are missing (SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD/FROM_EMAIL).",
                    hint="Set the values in .env or environment variables.",
                ),
            )

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.settings.FROM_EMAIL
        msg["To"] = to

        try:
            with smtplib.SMTP(self.settings.SMTP_HOST, int(self.settings.SMTP_PORT)) as server:
                server.starttls()
                server.login(self.settings.SMTP_USERNAME, self.settings.SMTP_PASSWORD)
                server.send_message(msg)

            return ToolResult(
                ok=True,
                data={
                    "to": to, 
                    "message": "Email sent successfully."
                    }
                )

        except Exception as e:
            return ToolResult(
                ok=False,
                error=ErrorInfo(
                    code=errors.EMAIL_SEND_FAILED,
                    message="Failed to send email.",
                    hint="Verify SMTP_HOST/SMTP_PORT and credentials. If using TLS, ensure the port supports STARTTLS (commonly 587).",
                    details={"exception": str(e)},
                ),
            )