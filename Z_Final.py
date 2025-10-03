import threading
import time
import json
from datetime import datetime
from pathlib import Path
import orjson

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from WikSpinLiv_2 import scrape_wickspin_live
from WikSpinLiv_2_Premium import scrape_premium_data
from WikSpinLiv_1 import scrape_data  # Update this to your actual module if needed


# Helper for timestamps
def now():
    return datetime.now().strftime('%H:%M:%S')


# Load match data from JSON file using orjson
def load_matches_from_json(file_path):
    try:
        with open(file_path, 'rb') as f:  # orjson requires binary mode
            return orjson.loads(f.read())
    except Exception as e:
        print(f"[{now()}] ❌ Failed to load JSON: {e}")
        return []


# Clean filenames
def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).rstrip()


# Setup Selenium Chrome driver
def create_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-webgl')
    options.add_argument('--enable-unsafe-swiftshader')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--log-level=3')
    return webdriver.Chrome(options=options)


# Thread function for scraping a match continuously
def process_match_forever(sport, match):
    match_name = sanitize_filename(match.get("match", "unknown_match"))
    url = match.get("url")
    fancy_bet = match.get("fancy_bet", False)
    sport_dir = Path("Scrapped") / sanitize_filename(sport)
    sport_dir.mkdir(parents=True, exist_ok=True)

    premium_output = sport_dir / f"{match_name}_premium.json"
    wickspin_output = sport_dir / f"{match_name}_wickspin.json"

    print(f"[{now()}] 🔄 Starting continuous scrape for: {match_name} | Sport: {sport} | Fancy Bet: {fancy_bet}")

    driver = create_driver()

    try:
        while True:
            try:
                if fancy_bet:
                    scrape_wickspin_live(
                        main_url=url,
                        output_file=str(wickspin_output),
                        update_interval=0.0,
                        headless=True,
                        run_forever=False,
                        driver=driver
                    )
                    print(f"[{now()}] ✅ Wickspin scrape cycle complete: {match_name}")
                # else:
                #     scrape_premium_data(
                #         loop_interval=0.5,
                #         main_url=url,
                #         output_file=str(premium_output),
                #         run_forever=False,
                #         driver=driver
                #     )
                #     print(f"[{now()}] ✅ Premium scrape cycle complete: {match_name}")
            except Exception as e:
                print(f"[{now()}] ❌ Error scraping {match_name}: {e}")
                # Restart driver if error
                try:
                    driver.quit()
                except Exception:
                    pass
                driver = create_driver()
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        print(f"[{now()}] 🛑 Driver quit for match: {match_name}")


# Watcher thread to monitor the JSON file for new matches
def watch_for_new_matches(json_file, existing_matches_set, check_interval=30):
    print(f"[{now()}] 👀 Watcher started — monitoring for new matches every {check_interval}s.")
    while True:
        try:
            data = load_matches_from_json(json_file)
            if data:
                for sport_entry in data:
                    sport = sport_entry.get("sport", "Unknown")
                    matches = sport_entry.get("matches", [])
                    for match in matches:
                        if match.get("fancy_bet", False):
                            match_id = f"{sport}|{match.get('match', '')}|{match.get('url', '')}"
                            if match_id not in existing_matches_set:
                                print(f"[{now()}] ➕ New match detected: {match.get('match')} in {sport}. Starting scraper thread.")
                                thread = threading.Thread(
                                    target=process_match_forever,
                                    args=(sport, match),
                                    daemon=True
                                )
                                thread.start()
                                threads.append(thread)
                                existing_matches_set.add(match_id)
            else:
                print(f"[{now()}] ⚠️ Watcher found no matches in JSON.")
        except Exception as e:
            print(f"[{now()}] ❌ Watcher error: {e}")

        time.sleep(check_interval)


# Main entry point
if __name__ == "__main__":
    threads = []
    existing_matches_set = set()
    json_file = "WikSpinLiv_1.json"

    # 2. Start periodic scraper thread that loops every 15 minutes
    def periodic_scraper_loop():
        while True:
            print(f"\n[{now()}] ⏳ Starting periodic scrape...")
            try:
                scrape_data()
            except Exception as e:
                print(f"[{now()}] ❌ Error in periodic scrape: {e}")
            print(f"[{now()}] ⏱ periodic_scraper waiting 15 minutes...\n")
            time.sleep(900)  # 15 minutes

    periodic_thread = threading.Thread(target=periodic_scraper_loop, daemon=True)
    periodic_thread.start()
    threads.append(periodic_thread)

    # 4. Start watcher thread to monitor for new matches
    watcher_thread = threading.Thread(
        target=watch_for_new_matches,
        args=(json_file, existing_matches_set),
        daemon=True
    )
    watcher_thread.start()
    threads.append(watcher_thread)

    print(f"[{now()}] ✅ All threads started. Waiting for matches...")

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Exiting... All threads will stop automatically.")

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Exiting... All threads will stop automatically.")







# import threading
# import time
# import json
# from datetime import datetime
# from pathlib import Path

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

# from WikSpinLiv_2 import scrape_wickspin_live
# from WikSpinLiv_2_Premium import scrape_premium_data

# def load_matches_from_json(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except Exception as e:
#         print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Failed to load JSON: {e}")
#         return []

# def sanitize_filename(name):
#     return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).rstrip()

# def create_driver():
#     options = Options()
#     options.add_argument('--headless=new')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-software-rasterizer')
#     options.add_argument('--disable-webgl')
#     options.add_argument('--enable-unsafe-swiftshader')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--log-level=3')
#     return webdriver.Chrome(options=options)

# def process_match_forever(sport, match):
#     match_name = sanitize_filename(match.get("match", "unknown_match"))
#     url = match.get("url")
#     fancy_bet = match.get("fancy_bet", False)
#     sport_dir = Path("Scrapped") / sanitize_filename(sport)
#     sport_dir.mkdir(parents=True, exist_ok=True)

#     premium_output = sport_dir / f"{match_name}_premium.json"
#     wickspin_output = sport_dir / f"{match_name}_wickspin.json"

#     print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Starting continuous scrape for: {match_name} | Sport: {sport} | Fancy Bet: {fancy_bet}")

#     driver = create_driver()

#     try:
#         while True:
#             try:
#                 if fancy_bet:
#                     scrape_wickspin_live(
#                         main_url=url,
#                         output_file=str(wickspin_output),
#                         update_interval=0.2,
#                         headless=True,
#                         run_forever=False,
#                         driver=driver
#                     )
#                     print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Wickspin scrape cycle complete: {match_name}")
#                 else:
#                     scrape_premium_data(
#                         loop_interval=0.5,
#                         main_url=url,
#                         output_file=str(premium_output),
#                         run_forever=False,
#                         driver=driver
#                     )
#                     print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Premium scrape cycle complete: {match_name}")
#             except Exception as e:
#                 print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error scraping {match_name}: {e}")

#             time.sleep(2)
#     finally:
#         driver.quit()
#         print(f"[{datetime.now().strftime('%H:%M:%S')}] 🛑 Driver quit for match: {match_name}")

# if __name__ == "__main__":
#     json_file = "WikSpinLiv_1.json"
#     data = load_matches_from_json(json_file)

#     if not data:
#         print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ No data found in {json_file}")
#         exit()

#     threads = []

#     for sport_entry in data:
#         sport = sport_entry.get("sport", "Unknown")
#         matches = sport_entry.get("matches", [])
#         for match in matches:
#             thread = threading.Thread(
#                 target=process_match_forever,
#                 args=(sport, match),
#                 daemon=True
#             )
#             thread.start()
#             threads.append(thread)

#     print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ All match threads started. Scraping continuously...")

#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("\n🛑 Exiting... All threads will stop automatically.")

