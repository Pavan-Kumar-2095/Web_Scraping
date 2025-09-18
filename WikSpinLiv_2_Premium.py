import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIG ---
main_url = "https://www.wickspin24.live/#/full-market/11205870--49624?marketId=-49979"
output_file = "WikSpinLiv_2_Premium.json"
loop_interval = 0.5  # seconds between each scrape

options = Options()
# options.add_argument("--headless")  # uncomment to run headless
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    driver.get(main_url)
    print("🌍 Opened main URL")
    time.sleep(1)  # reduced initial wait

    while True:
        combined_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "scoreboard": [],
            "markets": []
        }

        try:
            print(f"\n🔄 Refreshing data at {datetime.now().strftime('%H:%M:%S')}")

            # === SCRAPE MARKETS ===
            time.sleep(1)  # reduced wait for JS rendering

            markets = driver.find_elements(By.CSS_SELECTOR, "div.mb-1")
            print(f"📦 Found {len(markets)} market blocks.")

            for market in markets:
                try:
                    title_elem = market.find_element(By.CSS_SELECTOR, "div.relative.py-2.pl-0 > span.text-13.font-bold")
                    market_title = title_elem.text.strip()

                    options_data = []

                    bet_boxes = market.find_elements(By.CSS_SELECTOR, "div.grid.grid-cols-2 > div[title='back']")

                    try:
                        overlay_div = market.find_element(By.CSS_SELECTOR, "div.absolute.w-full.h-full")
                        style = overlay_div.get_attribute("style")
                        status = "suspended" if "display: none" not in style else "active"
                    except:
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

            # === SCRAPE SCOREBOARD (IFRAME) ===
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            found = False
            for iframe in iframes:
                src = iframe.get_attribute("src")
                if src and "betgenius.com/multisportscoreboard" in src:
                    driver.switch_to.frame(iframe)
                    found = True
                    break

            if found:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="scoreboard-head-to-head-container"]')))
                competitors = driver.find_elements(By.CSS_SELECTOR, '[data-testid="scoreboard-competitor-container"]')

                for comp in competitors:
                    try:
                        score_elem = comp.find_element(By.CSS_SELECTOR, '[data-testid="scoreWrapper"]')
                        team_elem = comp.find_element(By.CSS_SELECTOR, '[data-testid="dynamic-text-container"] p')

                        combined_data["scoreboard"].append({
                            "team": team_elem.text.strip(),
                            "score": score_elem.text.strip()
                        })

                    except Exception as e:
                        print(f"⚠️ Scoreboard entry error: {e}")

                driver.switch_to.default_content()
            else:
                print("❌ Scoreboard iframe not found.")

            # === SAVE DATA ===
            with open(output_file, "w") as f:
                json.dump(combined_data, f, indent=2)

            print(f"✅ Updated data saved to {output_file}")
            print(f"🔁 Waiting {loop_interval} seconds before next refresh...\n")
            time.sleep(loop_interval)

        except Exception as e:
            print(f"❌ Scrape error in loop: {e}")
            time.sleep(loop_interval)

except KeyboardInterrupt:
    print("\n🛑 Stopped by user (Ctrl+C)")
finally:
    driver.quit()
