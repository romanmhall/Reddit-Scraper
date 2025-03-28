# scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime, timedelta

# Wishlist keywords (must be in lowercase)
wishlist = [
]

# Email settings
EMAIL = "@gmail.com"           # Replace with your email
EMAIL_PASSWORD = "xxx xxx xxx xxx"     # Replace with your app password (not your Gmail password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# History file to avoid duplicates
HISTORY_FILE = "match_history.txt"


def _setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    return webdriver.Chrome(options=chrome_options)


def _load_history():
    """Load match history from file, returns a dict {title: timestamp}"""
    history = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    timestamp_str, title = line.strip().split("|", 1)
                    history[title] = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except:
                    continue
    return history


def _save_to_history(matches):
    """Append new matches to history file"""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for match in matches:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{match['title']}\n")


def _send_email(matches):
    """Send email only for matches not seen in the past 24h"""
    recent_history = _load_history()
    cutoff_time = datetime.now() - timedelta(hours=24)

    new_matches = []
    for match in matches:
        title = match['title']
        if title in recent_history and recent_history[title] > cutoff_time:
            print(f"Skipping duplicate (seen in last 24h): {title}")
            continue
        new_matches.append(match)

    if not new_matches:
        print("No new unique matches to send.")
        return

    # Compose and send the email
    subject = "Wishlist Match(es) from Reddit Scraper"
    body = "\n".join([f"{m['title']}\n{m['url']}\n{'-'*50}" for m in new_matches])

    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent with new matches!")
        _save_to_history(new_matches)
    except Exception as e:
        print(f"Failed to send email: {e}")


def scrape_once():
    """Scrapes once and returns a list of matched items"""
    matches = []
    seen_posts = set()

    driver = _setup_driver()
    driver.get("https://www.reddit.com/r/GunAccessoriesForSale/new/")
    time.sleep(5)

    posts = driver.find_elements(By.TAG_NAME, "shreddit-post")
    for post in posts:
        try:
            post_id = post.get_attribute("id") or post.get_attribute("content-href")
            if post_id in seen_posts:
                continue
            seen_posts.add(post_id)

            article = post.find_element(By.XPATH, "./ancestor::article")
            title = article.get_attribute("aria-label")
            url = post.get_attribute("content-href")

            if any(item in title.lower() for item in wishlist):
                matches.append({"title": title, "url": url})
        except Exception as e:
            print(f"Error: {e}")

    driver.quit()
    return matches


def scrape_and_alert(interval=60):
    """Continuously scrapes and sends email alerts for new matches"""
    seen_posts = set()

    while True:
        driver = _setup_driver()
        driver.get("https://www.reddit.com/r/GunAccessoriesForSale/new/")
        time.sleep(5)
        posts = driver.find_elements(By.TAG_NAME, "shreddit-post")
        new_matches = []

        for post in posts:
            try:
                post_id = post.get_attribute("id") or post.get_attribute("content-href")
                if post_id in seen_posts:
                    continue
                seen_posts.add(post_id)

                article = post.find_element(By.XPATH, "./ancestor::article")
                title = article.get_attribute("aria-label")
                url = post.get_attribute("content-href")

                if any(item in title.lower() for item in wishlist):
                    new_matches.append({"title": title, "url": url})
                    print(f"Match: {title}")
                    print(f"{url}\n{'-'*50}")
            except Exception as e:
                print(f"Error: {e}")

        driver.quit()

        if new_matches:
            _send_email(new_matches)

        print(f"Waiting {interval} seconds before next check...\n")
        time.sleep(interval)
