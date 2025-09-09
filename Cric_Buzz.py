import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
from datetime import datetime  


def load_existing_comments(filename="commentary.json"):
    try:
        data = json.load(open(filename, "r", encoding="utf-8"))
        if isinstance(data, dict):
            return data
        else:
            print("Warning: Loaded data is a list, expected dict. Starting fresh.")
            return {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_comments(comments, filename="commentary.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)

def fetch_match_info_and_commentary(driver, url):
    driver.get(url)
    time.sleep(5)  

    soup = BeautifulSoup(driver.page_source, 'html.parser')

   
    match_title_tag = soup.find('h3')
    match_title = match_title_tag.get_text(strip=True) if match_title_tag else "Match title not found"

    match_datetime_tag = soup.find('h4', class_='mb-7')
    match_datetime = match_datetime_tag.get_text(strip=True).replace('●', '|') if match_datetime_tag else "Date/Time not found"

    comment_items = soup.find_all('div', class_='comment_listing')
    
    commentary_dict = {}
    for item in comment_items:
        text = item.get_text(strip=True)
    
        match = re.match(r'^(\d+\.\d)(.*)', text)

        if match:
            ball_number = match.group(1)
            comment = match.group(2).strip()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp
            commentary_dict[ball_number] = {
                "comment": comment,
                "timestamp": timestamp
            }

    return match_title, match_datetime, commentary_dict

def main():
    url = "https://cricketlineguru.com/match-detail/asia_cup_2025_g1/commentary/afghanistan-vs-hong-kong-1st-match-group-b"

    options = Options()
    options.headless = True
    options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)

    stored_comments = load_existing_comments()

    try:
        while True:
            match_title, match_datetime, commentary = fetch_match_info_and_commentary(driver, url)

            print(f"\nMatch: {match_title}")
            print(f"{match_datetime}")

            
            new_balls = {ball: comment for ball, comment in commentary.items() if stored_comments.get(ball) != comment}

            if new_balls:
                print(f"Found {len(new_balls)} new or updated commentary entries. Saving...")
                stored_comments.update(new_balls)
                save_comments(stored_comments)
            else:
                print("No new commentary found.")

            time.sleep(30)  

    except KeyboardInterrupt:
        print("Stopping scraping by user.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
