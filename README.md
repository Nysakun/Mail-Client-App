# Python Mail Client

A simple desktop mail client built in pure Python. Log in with your Gmail address and App Password, send emails via SMTP, and read your inbox via IMAP, all from a Tkinter GUI.

## Features
- Login screen with credential verification
- Compose and send emails (SMTP)
- Fetch and read inbox messages (IMAP)
- Background threading so the UI never freezes

## Files
- `app.py` - the Tkinter user interface (run this file)
- `email_service.py` - all mail logic (send, login check, fetch inbox)

## How to run
1. Install Python 3 (Tkinter comes built in, no pip install needed)
2. Put both files in the same folder
3. Run: `python app.py`

## Gmail App Password (required)
Gmail blocks normal passwords for SMTP/IMAP. Create an App Password:
1. Google Account -> Security
2. Turn on 2-Step Verification
3. Search for "App Passwords" and generate one
4. Use your Gmail address and this 16-character password to log in

## Testing
Send a mail to yourself or a second account, then open the Inbox tab and click Refresh Inbox.

## Tech stack
Python, Tkinter, smtplib, imaplib, threading 