import os
import socket
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")  # your Gmail address
SMTP_PASS = os.environ.get("SMTP_PASS")  # Gmail App Password (not your normal password)
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER)


class MailerNotConfigured(Exception):
    pass


def _connect_smtp_ipv4(host, port, timeout=10):
    """Resolve host to an IPv4 address explicitly and connect.

    Render (and some other PaaS hosts) don't route outbound IPv6, but
    smtp.gmail.com resolves to both A and AAAA records. If Python picks
    the IPv6 address first, connect() fails with OSError(101, 'Network
    is unreachable'). Resolving with AF_INET up front avoids that.
    """
    infos = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    if not infos:
        raise OSError(f"Could not resolve {host} to an IPv4 address")
    ipv4_addr = infos[0][4][0]

    server = smtplib.SMTP(timeout=timeout)
    server.connect(ipv4_addr, port, source_address=None)
    # Gmail's cert is issued for the hostname, not the raw IP, so EHLO/TLS
    # still need the real hostname for SNI + certificate verification.
    server.ehlo()
    return server


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

    server = _connect_smtp_ipv4(SMTP_HOST, SMTP_PORT, timeout=10)
    try:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(MAIL_FROM, [to_email], msg.as_string())
    finally:
        server.quit()
