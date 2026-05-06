import asyncio
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import partial

from fastapi import HTTPException

from app.core.config import settings


class BaseEmailService(ABC):
    @abstractmethod
    def send_otp_email(self, email: str, code: str) -> None: ...

    @abstractmethod
    def send_welcome_email(self, email: str) -> None: ...


class GmailEmailService(BaseEmailService):
    """
    Sends transactional emails via Gmail SMTP using an App Password.

    Setup:
        1. Enable 2-Step Verification on your Google Account.
        2. Go to https://myaccount.google.com/apppasswords
        3. Create an app password for "Mail" → copy the 16-char code.
        4. Set SMTP_USERNAME and SMTP_APP_PASSWORD in your .env file.
    """

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_APP_PASSWORD
        self.from_name = settings.EMAIL_FROM_NAME

    # ─── Public API

    async def send_otp_email(self, email: str, code: str) -> None:
        """Send a 6-digit OTP verification email asynchronously."""
        subject = "Verify your email address"
        html = self._otp_template(email, code)
        await self._send_async(to=email, subject=subject, html=html)

    async def send_welcome_email(self, email: str) -> None:
        """Send a welcome email after successful OTP verification."""
        subject = f"Welcome to {self.from_name}!"
        html = self._welcome_template(email)
        await self._send_async(to=email, subject=subject, html=html)

    #  Internal

    async def _send_async(self, to: str, subject: str, html: str) -> None:
        """
        Run the blocking smtplib call in a thread pool so it doesn't block
        the FastAPI event loop.
        """
        loop = asyncio.get_event_loop()
        send_fn = partial(self._send_sync, to=to, subject=subject, html=html)
        try:
            await loop.run_in_executor(None, send_fn)
        except Exception as e:
            # Log and raise a 500 — caller decides whether to surface this
            raise HTTPException(
                status_code=500,
                detail=f"Email delivery failed: {e}",
            ) from e

    def _send_sync(self, to: str, subject: str, html: str) -> None:
        """Build and send a MIME email via Gmail SMTP with STARTTLS."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.username}>"
        msg["To"] = to
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(self.host, self.port) as server:
            server.ehlo()
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, to, msg.as_string())

    #  HTML Templates

    def _otp_template(self, email: str, code: str) -> str:
        expire = settings.OTP_EXPIRE_MINUTES
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }}
            .wrapper {{ max-width: 520px; margin: 40px auto; background: #ffffff;
                        border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,.08); }}
            .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                       padding: 32px; text-align: center; }}
            .header h1 {{ color: #e94560; margin: 0; font-size: 22px; letter-spacing: 1px; }}
            .body {{ padding: 36px 40px; }}
            .body p {{ color: #444; line-height: 1.6; font-size: 15px; }}
            .otp-box {{ background: #f0f4ff; border: 2px dashed #4a90e2;
                        border-radius: 10px; padding: 20px; text-align: center; margin: 24px 0; }}
            .otp-code {{ font-size: 40px; font-weight: bold; letter-spacing: 10px;
                         color: #1a1a2e; font-family: monospace; }}
            .footer {{ background: #f9f9f9; padding: 20px 40px; text-align: center;
                       color: #999; font-size: 12px; border-top: 1px solid #eee; }}
          </style>
        </head>
        <body>
          <div class="wrapper">
            <div class="header">
              <h1>🌍 {self.from_name}</h1>
            </div>
            <div class="body">
              <p>Hello,</p>
              <p>Use the code below to verify your email address. It expires in <strong>{expire} minutes</strong>.</p>
              <div class="otp-box">
                <div class="otp-code">{code}</div>
              </div>
              <p>If you didn't create an account, you can safely ignore this email.</p>
            </div>
            <div class="footer">
              <p>This email was sent to {email} · © 2025 {self.from_name}</p>
            </div>
          </div>
        </body>
        </html>
        """

    def _welcome_template(self, email: str) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }}
            .wrapper {{ max-width: 520px; margin: 40px auto; background: #ffffff;
                        border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,.08); }}
            .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                       padding: 32px; text-align: center; }}
            .header h1 {{ color: #e94560; margin: 0; font-size: 22px; letter-spacing: 1px; }}
            .body {{ padding: 36px 40px; }}
            .body p {{ color: #444; line-height: 1.6; font-size: 15px; }}
            .cta {{ display: inline-block; margin-top: 20px; padding: 14px 32px;
                    background: #e94560; color: #fff; text-decoration: none;
                    border-radius: 8px; font-weight: bold; font-size: 15px; }}
            .footer {{ background: #f9f9f9; padding: 20px 40px; text-align: center;
                       color: #999; font-size: 12px; border-top: 1px solid #eee; }}
          </style>
        </head>
        <body>
          <div class="wrapper">
            <div class="header">
              <h1>🌍 {self.from_name}</h1>
            </div>
            <div class="body">
              <p>Welcome aboard! 🎉</p>
              <p>Your email has been verified and your account is now active. You can start contributing
                 to African indigenous language datasets.</p>
              <p>Thank you for helping preserve Africa's linguistic heritage.</p>
            </div>
            <div class="footer">
              <p>This email was sent to {email} · © 2025 {self.from_name}</p>
            </div>
          </div>
        </body>
        </html>
        """


# Singleton — import and use this instance throughout the app
email_service = GmailEmailService()