"""Send Email Tool

Sends an email with an optional file attachment via SMTP.
"""

import json
import os
import smtplib
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def main(to: str, subject: str, body: str, attachment_path: str = None) -> dict:
    """Send an email via SMTP with an optional attachment.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Plain-text email body.
        attachment_path: Optional path to a file to attach.

    Returns:
        dict with 'sent' boolean.
    """
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    email_from = os.environ.get("EMAIL_FROM")

    if not all([smtp_host, smtp_user, smtp_password, email_from]):
        return {
            "ok": False,
            "error": {
                "code": "SEND_EMAIL/VALIDATION",
                "message": "SMTP credentials not fully configured in environment variables.",
                "detail": {"required": ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "EMAIL_FROM"]},
                "retryable": False,
            },
        }

    if attachment_path and not os.path.isfile(attachment_path):
        return {
            "ok": False,
            "error": {
                "code": "SEND_EMAIL/VALIDATION",
                "message": f"Attachment file not found: {attachment_path}",
                "detail": {},
                "retryable": False,
            },
        }

    # Build the email message
    msg = MIMEMultipart()
    msg["From"] = email_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach file if provided
    if attachment_path:
        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=filename)
        part["Content-Disposition"] = f'attachment; filename="{filename}"'
        msg.attach(part)

    # Send via SMTP with STARTTLS
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(email_from, [to], msg.as_string())
    except smtplib.SMTPAuthenticationError as e:
        return {
            "ok": False,
            "error": {
                "code": "SEND_EMAIL/PERMANENT",
                "message": f"SMTP authentication failed: {e}",
                "detail": {},
                "retryable": False,
            },
        }
    except (smtplib.SMTPException, OSError) as e:
        return {
            "ok": False,
            "error": {
                "code": "SEND_EMAIL/TRANSIENT",
                "message": f"Failed to send email: {e}",
                "detail": {},
                "retryable": True,
            },
        }

    return {
        "ok": True,
        "result": {
            "sent": True,
        },
    }


if __name__ == "__main__":
    data = json.loads(sys.stdin.read())
    result = main(
        to=data["to"],
        subject=data["subject"],
        body=data["body"],
        attachment_path=data.get("attachment_path"),
    )
    print(json.dumps(result, indent=2))
