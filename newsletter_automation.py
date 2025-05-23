import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import imaplib, email
from email.header import decode_header
import openai

# Configuration – fill in your details
EMAIL = "morettindavid@gmail.com"  # Your email address
PASSWORD = "your_email_password"   # Replace with your email password or an app-specific password
OPENAI_API_KEY = "your_openai_api_key"

# List of GTA low-rise builder newsletter signup URLs
BUILDER_URLS = [
    "https://mattamyhomes.com/ontario/gta",
    "https://www.fieldgatehomes.com/",
    "https://www.minto.com/ottawa/new-homes-condos/projects/Sign-Up~1135.html",
    "https://danielshomes.ca/",
    # Add more builder signup pages or community-specific pages here
]

# IMAP settings (e.g., for Gmail)
IMAP_SERVER = "imap.gmail.com"
IMAP_FOLDER = "INBOX"


def signup(driver, url):
    """Navigate to the signup page and submit the email address."""
    driver.get(url)
    time.sleep(2)
    try:
        email_input = driver.find_element(By.XPATH, "//input[@type='email']")
        email_input.send_keys(EMAIL)
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Submit')]")
        submit_btn.click()
        time.sleep(2)
    except Exception as e:
        print(f"Failed to sign up at {url}: {e}")


def fetch_unseen_emails():
    """Connect to the IMAP server, fetch unseen newsletters, and return raw content."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select(IMAP_FOLDER)
    status, messages = mail.search(None, 'UNSEEN')
    email_ids = messages[0].split()
    fetched = {}

    for eid in email_ids:
        res, msg_data = mail.fetch(eid, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_header(msg['Subject'])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                from_ = msg.get('From')

                # Extract text/plain body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                key = f"{from_} | {subject}"
                fetched[key] = body

    return fetched


def summarize(text: str) -> str:
    """Use OpenAI to summarize newsletter content and extract key insights."""
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "co
