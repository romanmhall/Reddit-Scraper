# Reddit-Scraper

Simple webscraper using reddit pages to find items that I would like to purchase second hand. 


Using Google App Passwords I can link my Gmail to the scraper and send alerts directly to myself when something of interest comes up on a subreddit.

![image](https://github.com/user-attachments/assets/a56b8831-fd03-4732-8fc0-54461067b9f0)

![image](https://github.com/user-attachments/assets/c10637a5-4697-4159-a9bd-675fec409715)

Installation instructions: 
Reddit Wishlist Scraper

Works on Windows, Linux, macOS

Setup Instructions:

1. Install Python 3 (if not already installed)

2. Open terminal or command prompt

   Windows:
   - Double-click launch.bat
   - Or open terminal and run:
     pip install -r requirements.txt
     python main.py

   Linux/macOS:
   - Open terminal and run:
     chmod +x launch.sh
     ./launch.sh

3. Edit scraper.py and replace:
   - your_email@gmail.com
   - your_app_password (App Password from Google)

Email alerts are sent only for unique matches within the last 24 hours.
