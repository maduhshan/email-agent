import os
import email
import imaplib

from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def read_gmail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)

    mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)

    mail.select("INBOX", readonly=True)

    status, messages = mail.search(None, "ALL")

    if status != "OK":
        raise RuntimeError("Unable to search inbox")

    email_ids = messages[0].split()[-5:]

    for email_id in reversed(email_ids):
        status, data = mail.fetch(email_id, "(RFC822)")

        if status != "OK":
            continue

        msg = email.message_from_bytes(data[0][1])

        subject = decode_header(msg["Subject"] or "")[0][0]

        if isinstance(subject, bytes):
            subject = subject.decode(errors="replace")

        print("----------------------")
        print("From:", msg["From"])
        print("Subject:", subject)

    mail.logout()


if __name__ == "__main__":
    read_gmail()