# main.py

from scraper import scrape_once, scrape_and_alert

def main():
    print("=== Reddit Wishlist Scraper ===")
    print("1. Run once and save matches to wishlist_matches.txt")
    print("2. Run continuously and send email alerts on new matches")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        matches = scrape_once()
        if matches:
            with open("wishlist_matches.txt", "w", encoding="utf-8") as f:
                for match in matches:
                    f.write(f"{match['title']}\n{match['url']}\n{'-'*50}\n")
            print("Matches saved to wishlist_matches.txt")
        else:
            print("No wishlist matches found.")

    elif choice == "2":
        print("Running continuous scraper with email alerts...")
        scrape_and_alert(interval=60)  # Check every 60 seconds

    else:
        print("Invalid option. Please run again and choose 1 or 2.")

if __name__ == "__main__":
    main()
