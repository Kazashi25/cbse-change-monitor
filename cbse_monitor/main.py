import os
import time
import smtplib
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

URLS = [
    "https://www.cbse.gov.in/cbsenew/cbse.html",
    "https://cbseresults.nic.in/2025/CBSE12th/CBSE12thLogin?resultType=cbse12"
]

CACHE_FILE = "last_content.txt"

def fetch_page_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser").get_text()
    except Exception as e:
        return f"ERROR: {e}"

def load_last_content():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, "r") as f:
        lines = f.read().split("\n\n")
        return {URLS[i]: lines[i] for i in range(len(lines))}

def save_current_content(content_dict):
    with open(CACHE_FILE, "w") as f:
        f.write("\n\n".join(content_dict[url] for url in URLS))

def send_email(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["GMAIL_USER"]
    msg["To"] = os.environ["RECEIVER_EMAIL"]
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["GMAIL_USER"], os.environ["GMAIL_PASS"])
        smtp.send_message(msg)

def check_for_changes():
    old_content = load_last_content()
    new_content = {}
    changes = []

    for url in URLS:
        content = fetch_page_content(url)
        new_content[url] = content
        if old_content.get(url) != content:
            changes.append(url)

    if changes:
        body = "\n\n".join([f"{url} has changed." for url in changes])
        send_email("Website Update Alert", body)
        save_current_content(new_content)

# Run immediately on app start
send_email("CBSE Monitor Started", "The CBSE monitor app has started successfully.")
check_for_changes()
