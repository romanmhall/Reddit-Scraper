@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Running Reddit Scraper...
python main.py

pause
