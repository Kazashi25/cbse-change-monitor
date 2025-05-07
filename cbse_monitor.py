
import hashlib
import smtplib
import os
import requests
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

# === Configuration ===
URLS = {
    "CBSE Main Page": "https://www.cbse.gov.in/cbsenew/cbse.html",
    "CBSE Results Page": "https://cbseresults.nic.in/2025/CBSE12th/CBSE12thLogin?resultType=cbse12"
}
HASH_DIR = "hashes"
EMAIL_ADDRESS = "youremail@gmail.com"          # Your Gmail address
EMAIL_PASSWORD = "your_app_password"           # App password (use Gmail App Password)
TO_EMAIL = "youremail@gmail.com"               # Where to receive alerts

# === Ensure hash directory exists ===
os.makedirs(HASH_DIR, exist_ok=True)

# === Utility Functions ===
def get_site_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except Exception as e:
        return f"ERROR: {e}"

def hash_content(content):
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# === Send live notification once ===
if not os.path.exists("notified_live.txt"):
    send_email("[CBSE Monitor] Site is Live", "Your CBSE Monitor app has started successfully.")
    with open("notified_live.txt", "w") as f:
        f.write("notified")

# === Main Monitoring Logic ===
for name, url in URLS.items():
    print(f"Checking {name}...")
    content = get_site_text(url)
    current_hash = hash_content(content)
    hash_file = os.path.join(HASH_DIR, f"{name.replace(' ', '_')}.txt")

    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            last_hash = f.read()
    else:
        last_hash = ""

    if current_hash != last_hash:
        send_email(
            subject=f"[CBSE Monitor] Change detected on: {name}",
            body=f"The content at {url} has changed."
        )
        with open(hash_file, "w") as f:
            f.write(current_hash)
