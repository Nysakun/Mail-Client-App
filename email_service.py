"""
Core mail logic — sending (SMTP) and receiving (IMAP).
Works out of the box with Gmail. For other providers, just change
SMTP_SERVER / IMAP_SERVER below.
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.header import decode_header

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
IMAP_SERVER = "imap.gmail.com"


def send_email(sender_email, app_password, to_email, subject, body):
    """Send a plain-text email. Returns (success: bool, message: str)."""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Failed to send email: {e}"


def verify_login(email_addr, app_password):
    """Check credentials by attempting an IMAP login. Used for the login screen."""
    try:
        imap = imaplib.IMAP4_SSL(IMAP_SERVER)
        imap.login(email_addr, app_password)
        imap.logout()
        return True, "Login successful!"
    except Exception as e:
        return False, f"Login failed: {e}"


def _decode(value):
    if not value:
        return ""
    decoded, encoding = decode_header(value)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded


def fetch_inbox(email_addr, app_password, limit=10):
    """Fetch the most recent emails from the inbox. Returns (success, list_or_error)."""
    try:
        imap = imaplib.IMAP4_SSL(IMAP_SERVER)
        imap.login(email_addr, app_password)
        imap.select("inbox")

        _, message_nums = imap.search(None, "ALL")
        mail_ids = message_nums[0].split()
        mail_ids = mail_ids[-limit:] if len(mail_ids) > limit else mail_ids
        mail_ids.reverse()  # newest first

        emails = []
        for mid in mail_ids:
            _, msg_data = imap.fetch(mid, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = _decode(msg["Subject"])
            from_ = _decode(msg["From"])
            date_ = msg["Date"] or ""

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode(errors="ignore")
                        break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode(errors="ignore")

            emails.append({
                "from": from_,
                "subject": subject,
                "date": date_,
                "body": body.strip()
            })

        imap.logout()
        return True, emails
    except Exception as e:
        return False, f"Failed to fetch inbox: {e}" 