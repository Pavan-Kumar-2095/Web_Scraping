# import threading
# import time
# import json
# from datetime import datetime
# from pathlib import Path
# from concurrent.futures import ThreadPoolExecutor, as_completed

# # Import scraping functions
# from WikSpinLiv_1 import scrape_data
# from WikSpinLiv_2 import scrape_wickspin_live
# from WikSpinLiv_2_Premium import scrape_premium_data


# # ========== Part 1: Periodic scraping of sports list ==========

# def periodic_sports_scrape(interval_minutes=5):
#     while True:
#         print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting scrape_data()...")
#         try:
#             scrape_data()
#         except Exception as e:
#             print(f"[{datetime.now().strftime('%H:%M:%S')}] Error in scrape_data: {e}")
#         print(f"[{datetime.now().strftime('%H:%M:%S')}] Finished scrape_data(), sleeping {interval_minutes} minutes...\n")
#         time.sleep(interval_minutes * 60)


# # ========== Part 2: Load matches from JSON ==========

# def load_matches_from_json(file_path):
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except Exception as e:
#         print(f"[{datetime.now().strftime('%H:%M:%S')}] Failed to load JSON: {e}")
#         return []


# # ========== Utility ==========

# def sanitize_filename(name):
#     return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).rstrip()


# # ========== Process a single match ==========

# def process_match(sport, match, base_output_dir):
#     match_name = sanitize_filename(match.get("match", "unknown_match"))
#     url = match.get("url")
#     fancy_bet = match.get("fancy_bet", False)
#     sportsbook = match.get("sportsbook", False)

#     sport_dir = Path(base_output_dir) / sanitize_filename(sport)
#     sport_dir.mkdir(parents=True, exist_ok=True)

#     premium_output = sport_dir / f"{match_name}_premium.json"
#     wickspin_output = sport_dir / f"{match_name}_wickspin.json"

#     print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Processing: {match_name} | Sport: {sport}")

#     try:
#         scrape_premium_data(
#             loop_interval=0.5,
#             main_url=url,
#             output_file=str(premium_output),
#             run_forever=False
#         )

#         scrape_wickspin_live(
#             main_url=url,
#             output_file=str(wickspin_output),
#             update_interval=0.2,
#             headless=True,
#             run_forever=False
#         )

#         print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Completed: {match_name}")
#     except Exception as e:
#         print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {match_name} | {e}")


# # ========== Run scrapers for all matches from JSON ==========

# def run_scrapers(json_file, base_output_dir="Scrapped", max_workers=5, loop_delay=2):
#     while True:
#         data = load_matches_from_json(json_file)
#         if not data:
#             print(f"[{datetime.now().strftime('%H:%M:%S')}] No data found, retrying soon...")
#             time.sleep(loop_delay)
#             continue

#         with ThreadPoolExecutor(max_workers=max_workers) as executor:
#             futures = []
#             for sport_entry in data:
#                 sport = sport_entry.get("sport", "Unknown")
#                 matches = sport_entry.get("matches", [])

#                 for match in matches:
#                     futures.append(executor.submit(process_match, sport, match, base_output_dir))

#             # Wait for all to complete
#             for future in as_completed(futures):
#                 try:
#                     future.result()
#                 except Exception as e:
#                     print(f"[{datetime.now().strftime('%H:%M:%S')}] Error in thread: {e}")

#         print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ Waiting before next run...\n")
#         time.sleep(loop_delay)


# # ========== Main: run both loops concurrently ==========

# if __name__ == "__main__":
#     json_file = "WikSpinLiv_1.json"

#     # Create threads
#     thread_scrape_list = threading.Thread(target=periodic_sports_scrape, args=(5,), daemon=True)
#     thread_process_matches = threading.Thread(target=run_scrapers, args=(json_file,), daemon=True)

#     # Start threads
#     thread_scrape_list.start()
#     thread_process_matches.start()

#     print(f"[{datetime.now().strftime('%H:%M:%S')}] Both scraping threads started. Press Ctrl+C to stop.")

#     # Keep main thread alive
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("\nReceived exit signal. Exiting...")





import threading
import time
import json
from datetime import datetime
from pathlib import Path

# Import scraping functions
from WikSpinLiv_1 import scrape_data
from WikSpinLiv_2 import scrape_wickspin_live
from WikSpinLiv_2_Premium import scrape_premium_data


# ========== Part 1: Periodic scraping of sports list ==========
def periodic_sports_scrape(interval_minutes=5):
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting scrape_data()...")
        try:
            scrape_data()
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error in scrape_data: {e}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Finished scrape_data(), sleeping {interval_minutes} minutes...\n")
        time.sleep(interval_minutes * 60)


# ========== Part 2: Load matches from JSON ==========
def load_matches_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Failed to load JSON: {e}")
        return []


# ========== Utility ==========
def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).rstrip()


# ========== Process a single match persistently ==========
def process_match(sport, match, base_output_dir, stop_event):
    match_name = sanitize_filename(match.get("match", "unknown_match"))
    url = match.get("url")

    sport_dir = Path(base_output_dir) / sanitize_filename(sport)
    sport_dir.mkdir(parents=True, exist_ok=True)

    premium_output = sport_dir / f"{match_name}_premium.json"
    wickspin_output = sport_dir / f"{match_name}_wickspin.json"

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Starting persistent processing: {match_name} | Sport: {sport}")

    while not stop_event.is_set():
        try:
            scrape_premium_data(
                loop_interval=0.5,
                main_url=url,
                output_file=str(premium_output),
                run_forever=False
            )

            scrape_wickspin_live(
                main_url=url,
                output_file=str(wickspin_output),
                update_interval=0.2,
                headless=True,
                run_forever=False
            )

            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Cycle completed: {match_name}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {match_name} | {e}")

        # Wait some time before next cycle, but check stop_event periodically
        for _ in range(20):  # 20 * 0.5 = 10 seconds total wait
            if stop_event.is_set():
                break
            time.sleep(0.5)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Stopped processing: {match_name}")


# ========== Run scrapers for all matches persistently with reload ==========
def run_scrapers(json_file, base_output_dir="Scrapped", interval_minutes=5):
    match_threads = {}
    stop_events = {}

    while True:
        data = load_matches_from_json(json_file)
        if not data:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No data found, retrying soon...")
            time.sleep(10)
            continue

        # Stop all existing threads cleanly before starting new ones
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Stopping all existing match threads...")
        for event in stop_events.values():
            event.set()
        for thread in match_threads.values():
            thread.join()

        match_threads.clear()
        stop_events.clear()

        # Start new threads for current matches
        for sport_entry in data:
            sport = sport_entry.get("sport", "Unknown")
            matches = sport_entry.get("matches", [])

            for match in matches:
                match_name = sanitize_filename(match.get("match", "unknown_match"))
                stop_event = threading.Event()
                thread = threading.Thread(
                    target=process_match,
                    args=(sport, match, base_output_dir, stop_event),
                    daemon=True
                )
                thread.start()
                match_threads[match_name] = thread
                stop_events[match_name] = stop_event

        print(f"[{datetime.now().strftime('%H:%M:%S')}] All match threads started. Sleeping for {interval_minutes} minutes...\n")
        time.sleep(interval_minutes * 60)


# ========== Main: run both loops concurrently ==========
if __name__ == "__main__":
    json_file = "WikSpinLiv_1.json"

    # Create threads
    thread_scrape_list = threading.Thread(target=periodic_sports_scrape, args=(5,), daemon=True)
    thread_process_matches = threading.Thread(target=run_scrapers, args=(json_file,), daemon=True)

    # Start threads
    thread_scrape_list.start()
    thread_process_matches.start()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Both scraping threads started. Press Ctrl+C to stop.")

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nReceived exit signal. Exiting...")
