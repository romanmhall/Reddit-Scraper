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

# Wishlist (all lowercase)
wishlist = [
    "11.5", "mk18", "qrf-10", "42", "h3", "ssa", "ssae", "ssaex", "sd3g", "sde", "sdc", "ssf",
    "prong", "prong flash hider", "surefire socom", "exps3-1", "g43", "g45", "surefire m640dft",
    "m640dft", "ds-sr07", "dssr07", "neomagsentry", "neomagsentry strap", "lightbar scout mount",
    "lightbar", "scout mount", "magpul bad", "magpul battery assist device", "bad", "sba4", "sba5",
    "radian raptor sd", "sd", "esk selector", "esk", "magpul esk", "folding stock adapter",
    "law tactical", "law tactical folding", "folding stock", "vikings tactics", "pmm ar15 magwell",
    "pmm magwell", "g33"
]

# Email settings
EMAIL = "romanhallfb@gmail.com"           # Replace with your email
EMAIL_PASSWORD = "iblo iytc tlyv ioqb"     # Use Gmail App Password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# History tracking
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
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for match in matches:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{match['title']}\n")


def _send_email(matches):
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


def scrape_and_alert(interval=900):  # 15 minutes = 900 seconds
    seen_posts = set()

    while True:
        driver = _setup_driver()
        driver.get("https://www.reddit.com/r/GunAccessoriesForSale/new/")
        time.sleep(5)

        posts = driver.find_elements(By.TAG_NAME, "shreddit-post")
        matches = []

        for post in posts:
            try:
                post_id = post.get_attribute("id") or post.get_attribute("content-href")
                if post_id in seen_posts:
                    continue
                seen_posts.add(post_id)

                post_url = post.get_attribute("content-href")

                # Visit full post page
                driver.execute_script(f"window.open('{post_url}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(3)

                try:
                    full_title = driver.find_element(By.TAG_NAME, "h1").text.lower()
                except:
                    full_title = ""

                try:
                    body_elem = driver.find_element(By.XPATH, "//div[contains(@data-testid, 'post-container')]")
                    body_text = body_elem.text.lower()
                except:
                    body_text = ""

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                combined_text = f"{full_title} {body_text}"

                if any(word in combined_text for word in wishlist):
                    matches.append({"title": full_title.strip(), "url": post_url})
                    print(f"Match: {full_title.strip()}")
                    print(f"{post_url}\n{'-'*50}")

            except Exception as e:
                print(f"Error: {e}")

        driver.quit()

        if matches:
            _send_email(matches)
        else:
            print("No matches found this run.")

        print(f"Sleeping for {interval // 60} minutes...\n")
        time.sleep(interval)
