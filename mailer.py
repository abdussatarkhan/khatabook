import os
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")  # your Gmail address
SMTP_PASS = os.environ.get("SMTP_PASS")  # Gmail App Password (not your normal password)
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER)


class MailerNotConfigured(Exception):
    pass


def send_otp_email(to_email, code, purpose, business_name=None):
    """Send a one-time verification code to the user's email.

    purpose: 'register' | 'login'
    Raises MailerNotConfigured if SMTP env vars aren't set (caller should
    handle this gracefully, e.g. by showing the code on-screen in dev mode).
    """
    if not SMTP_USER or not SMTP_PASS:
        raise MailerNotConfigured(
            "SMTP_USER / SMTP_PASS environment variables are not set."
        )

    if purpose == "register":
        subject = "Verify your Khatabook account"
        intro = "Thanks for signing up for Khatabook! Use this code to verify your email and finish setting up your account:"
    else:
        subject = "Your Khatabook login code"
        intro = "Use this code to complete your login to Khatabook:"

    body = f"""{intro}

    Verification code: {code}

This code expires in 10 minutes. If you didn't request this, you can safely ignore this email.

— Khatabook{f" ({business_name})" if business_name else ""}
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(MAIL_FROM, [to_email], msg.as_string())
