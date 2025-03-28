#!/bin/bash

echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Running Reddit Scraper..."
python3 main.py
