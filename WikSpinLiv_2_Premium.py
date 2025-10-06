
import json
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def scrape_premium_data(loop_interval=0.5, main_url=None, output_file=None, run_forever=True, driver=None ,  headless=True):
    if driver is None:
        raise ValueError("A Selenium WebDriver instance must be provided via the 'driver' argument.")

    main_url = main_url 
    output_file = output_file or "WikSpinLiv_2_Premium.json"

    driver.get(main_url)
    time.sleep(1)  # initial wait

    # Open all closed dropdowns once
    print("🔓 Opening all closed dropdowns...\n")
    market_blocks = driver.find_elements(By.CSS_SELECTOR, "div.mb-1")
    for idx, market in enumerate(market_blocks):
        try:
            header = market.find_element(By.CSS_SELECTOR, "div.relative.py-2.pl-0")
            market_title = header.find_element(By.CSS_SELECTOR, "span.text-13.font-bold").text.strip()

            try:
                arrow_icon = header.find_element(By.CSS_SELECTOR, "i.icon-arrow-down-sencodary")
                class_list = arrow_icon.get_attribute("class")
                closed = "rotate-180" not in class_list  # rotate-180 = open
            except NoSuchElementException:
                closed = False

            if closed:
                print(f"  ➡️ Opening: {market_title}")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", header)
                header.click()
                time.sleep(0.5)  # give some time after click
            else:
                print(f"  ✅ Already open: {market_title}")
        except Exception as e:
            print(f"  ⚠️ Failed to process dropdown {idx}: {e}")

    print("\n✅ All dropdowns opened.\n")

    while True:
        combined_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "markets": []
        }

        try:
            print(f"\n🔄 Refreshing data at {datetime.now().strftime('%H:%M:%S')}")
            time.sleep(1)  # wait for page to update

            markets = driver.find_elements(By.CSS_SELECTOR, "div.mb-1")
            print(f"📦 Found {len(markets)} market blocks.")

            for index, market in enumerate(markets):
                if index >= 5:  # ✅ Limit to first 5 markets
                    break

                try:
                    title_elem = market.find_element(By.CSS_SELECTOR, "div.relative.py-2.pl-0 > span.text-13.font-bold")
                    market_title = title_elem.text.strip()

                    options_data = []

                    bet_boxes = market.find_elements(By.CSS_SELECTOR, "div.grid.grid-cols-2 > div[title='back']")

                    # If no bets found, try clicking the arrow-down to expand
                    if len(bet_boxes) == 0:
                        try:
                            arrow_icon = market.find_element(By.CSS_SELECTOR, "i.icon-arrow-down-sencodary.text-12.mr-3.justify-self-end.text-black.transition-transform.origin-center.duration-300.transform.rotate-180")
                            print(f"  ⚡ Bets empty for '{market_title}', clicking arrow to expand...")
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", arrow_icon)
                            time.sleep(0.5)
                            arrow_icon.click()
                            time.sleep(1)  # wait for bets to load
                            bet_boxes = market.find_elements(By.CSS_SELECTOR, "div.grid.grid-cols-2 > div[title='back']")
                        except NoSuchElementException:
                            print(f"  ⚠️ No arrow icon found to expand bets for market '{market_title}'")

                    # Detect if market is suspended
                    try:
                        overlay_div = market.find_element(By.CSS_SELECTOR, "div.absolute.w-full.h-full")
                        style = overlay_div.get_attribute("style")
                        status = "suspended" if "display: none" not in style else "active"
                    except NoSuchElementException:
                        status = "active"

                    for box in bet_boxes:
                        try:
                            bet_label = box.find_element(By.CSS_SELECTOR, "p.text-9").text.strip()
                            odds_value = box.find_element(By.CSS_SELECTOR, "p.text-15").text.strip()

                            options_data.append({
                                "bet": bet_label,
                                "odds": odds_value,
                                "status": status
                            })
                        except Exception as e:
                            print(f"⚠️ Bet option parse error: {e}")

                    combined_data["markets"].append({
                        "market": market_title,
                        "bets": options_data
                    })

                except Exception as e:
                    print(f"⚠️ Market parse error: {e}")

            # Save data
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=2)

            print(f"✅ Updated data saved to {output_file}")
            print(f"🔁 Waiting {loop_interval} seconds before next refresh...\n")

            if not run_forever:
                break

            time.sleep(loop_interval)

        except Exception as e:
            print(f"❌ Scrape error in loop: {e}")
            time.sleep(loop_interval)


# import json
# import time
# from datetime import datetime
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException

# def scrape_premium_data(loop_interval=0.5, main_url=None, output_file=None, run_forever=True, driver=None):
#     if driver is None:
#         raise ValueError("A Selenium WebDriver instance must be provided via the 'driver' argument.")

#     main_url = main_url or "https://www.wickspin24.live/#/full-market/2-34748486?marketId=1.247941123"
#     output_file = output_file or "WikSpinLiv_2_Premium.json"

#     driver.get(main_url)
#     time.sleep(1)  # initial wait

#     # Open all closed dropdowns once
#     print("🔓 Opening all closed dropdowns...\n")
#     market_blocks = driver.find_elements(By.CSS_SELECTOR, "div.mb-1")
#     for idx, market in enumerate(market_blocks):
#         try:
#             header = market.find_element(By.CSS_SELECTOR, "div.relative.py-2.pl-0")
#             market_title = header.find_element(By.CSS_SELECTOR, "span.text-13.font-bold").text.strip()

#             try:
#                 arrow_icon = header.find_element(By.CSS_SELECTOR, "i.icon-arrow-down-sencodary")
#                 class_list = arrow_icon.get_attribute("class")
#                 closed = "rotate-180" not in class_list  # rotate-180 = open
#             except NoSuchElementException:
#                 closed = False

#             if closed:
#                 print(f"  ➡️ Opening: {market_title}")
#                 driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", header)
#                 header.click()
#                 time.sleep(0.5)  # give some time after click
#             else:
#                 print(f"  ✅ Already open: {market_title}")
#         except Exception as e:
#             print(f"  ⚠️ Failed to process dropdown {idx}: {e}")

#     print("\n✅ All dropdowns opened.\n")

#     while True:
#         combined_data = {
#             "timestamp": datetime.utcnow().isoformat() + "Z",
#             "scoreboard": [],
#             "markets": []
#         }

#         try:
#             print(f"\n🔄 Refreshing data at {datetime.now().strftime('%H:%M:%S')}")
#             time.sleep(1)  # wait for page to update

#             markets = driver.find_elements(By.CSS_SELECTOR, "div.mb-1")
#             print(f"📦 Found {len(markets)} market blocks.")

#             for market in markets:
#                 try:
#                     title_elem = market.find_element(By.CSS_SELECTOR, "div.relative.py-2.pl-0 > span.text-13.font-bold")
#                     market_title = title_elem.text.strip()

#                     options_data = []

#                     bet_boxes = market.find_elements(By.CSS_SELECTOR, "div.grid.grid-cols-2 > div[title='back']")

#                     # If no bets found, try clicking the arrow-down to expand
#                     if len(bet_boxes) == 0:
#                         try:
#                             arrow_icon = market.find_element(By.CSS_SELECTOR, "i.icon-arrow-down-sencodary.text-12.mr-3.justify-self-end.text-black.transition-transform.origin-center.duration-300.transform.rotate-180")
#                             print(f"  ⚡ Bets empty for '{market_title}', clicking arrow to expand...")
#                             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", arrow_icon)
#                             time.sleep(0.5)
#                             arrow_icon.click()
#                             time.sleep(1)  # wait for bets to load
#                             bet_boxes = market.find_elements(By.CSS_SELECTOR, "div.grid.grid-cols-2 > div[title='back']")
#                         except NoSuchElementException:
#                             print(f"  ⚠️ No arrow icon found to expand bets for market '{market_title}'")

#                     # Detect if market is suspended
#                     try:
#                         overlay_div = market.find_element(By.CSS_SELECTOR, "div.absolute.w-full.h-full")
#                         style = overlay_div.get_attribute("style")
#                         status = "suspended" if "display: none" not in style else "active"
#                     except NoSuchElementException:
#                         status = "active"

#                     for box in bet_boxes:
#                         try:
#                             bet_label = box.find_element(By.CSS_SELECTOR, "p.text-9").text.strip()
#                             odds_value = box.find_element(By.CSS_SELECTOR, "p.text-15").text.strip()

#                             options_data.append({
#                                 "bet": bet_label,
#                                 "odds": odds_value,
#                                 "status": status
#                             })
#                         except Exception as e:
#                             print(f"⚠️ Bet option parse error: {e}")

#                     combined_data["markets"].append({
#                         "market": market_title,
#                         "bets": options_data
#                     })

#                 except Exception as e:
#                     print(f"⚠️ Market parse error: {e}")

#             # Save data
#             with open(output_file, "w", encoding="utf-8") as f:
#                 json.dump(combined_data, f, ensure_ascii=False, indent=2)

#             print(f"✅ Updated data saved to {output_file}")
#             print(f"🔁 Waiting {loop_interval} seconds before next refresh...\n")

#             if not run_forever:
#                 break

#             time.sleep(loop_interval)

#         except Exception as e:
#             print(f"❌ Scrape error in loop: {e}")
#             time.sleep(loop_interval)



