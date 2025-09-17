import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- CONFIGURATION ---
main_url = "https://www.wickspin24.live/#/full-market/4-34733839?marketId=1.247788458"
output_file = "WikSpinLiv_2.json"

# --- SETUP CHROME DRIVER ---
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless")  # Faster scraping
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 2)  # Reduced wait time for faster scraping

# --- HELPER FUNCTION ---
def get_text_when_nonempty(parent, tag_name, timeout=1):
    try:
        return WebDriverWait(parent, timeout).until(
            lambda e: e.find_element(By.TAG_NAME, tag_name).text.strip() != ""
        ) and parent.find_element(By.TAG_NAME, tag_name).text.strip()
    except TimeoutException:
        return ""

# --- SCRAPE FUNCTION ---
def scrape_market_data():
    data = {}

    # --- Market Depth ---
    try:
        bet_limit_div = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="betLimit"]')
        spans = bet_limit_div.find_elements(By.TAG_NAME, "span")
        if len(spans) >= 2:
            label = spans[0].text.strip()
            value = spans[1].text.strip()
            data["market_depth"] = {label: value}
        else:
            data["market_depth"] = {}
    except NoSuchElementException:
        data["market_depth"] = {}

    # --- Exchange Odds ---
    data["exchange_odds"] = []
    try:
        match_lines = driver.find_elements(By.CLASS_NAME, "exchange_panel_line")
        for line in match_lines:
            try:
                h2_elem = line.find_element(By.TAG_NAME, "h2")
                name = h2_elem.text.strip().split("\n")[0]

                back_elem = line.find_element(By.CSS_SELECTOR, "div[title='BACK']")
                back_odds = back_elem.find_element(By.TAG_NAME, "h3").text.strip()
                back_volume = back_elem.find_element(By.TAG_NAME, "p").text.strip()

                lay_elem = line.find_element(By.CSS_SELECTOR, "div[title='LAY']")
                lay_odds = lay_elem.find_element(By.TAG_NAME, "h3").text.strip()
                lay_volume = lay_elem.find_element(By.TAG_NAME, "p").text.strip()

                data["exchange_odds"].append({
                    "team": name,
                    "back": {"odds": back_odds, "volume": back_volume},
                    "lay": {"odds": lay_odds, "volume": lay_volume}
                })
            except Exception:
                continue
    except Exception:
        data["exchange_odds"] = []

    # --- Fancy Bet Markets ---
    data["fancy_markets"] = []
    try:
        containers = driver.find_elements(By.CSS_SELECTOR, 'div.mb-1px.px-1.relative')
        for container in containers:  # Limit to first 10 for speed
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", container)
                title = container.find_element(By.TAG_NAME, "h2").text.strip()

                status_el = container.find_elements(By.CSS_SELECTOR, 'div[data-testid="fancybet-market-status"]')
                status = status_el[0].text.strip() if status_el else "Active"

                market = {"title": title, "status": status}

                if status.lower() == "suspend":
                    market["no"] = {"odds": None, "value": None}
                    market["yes"] = {"odds": None, "value": None}
                else:
                    try:
                        no_option = container.find_element(By.CSS_SELECTOR, 'div[title="NO"]')
                        no_odds = get_text_when_nonempty(no_option, "h3")
                        no_value = get_text_when_nonempty(no_option, "p")
                        market["no"] = {"odds": no_odds or "N/A", "value": no_value or "N/A"}
                    except:
                        market["no"] = {"odds": "N/A", "value": "N/A"}

                    try:
                        yes_option = container.find_element(By.CSS_SELECTOR, 'div[title="YES"]')
                        yes_odds = get_text_when_nonempty(yes_option, "h3")
                        yes_value = get_text_when_nonempty(yes_option, "p")
                        market["yes"] = {"odds": yes_odds or "N/A", "value": yes_value or "N/A"}
                    except:
                        market["yes"] = {"odds": "N/A", "value": "N/A"}

                data["fancy_markets"].append(market)
            except:
                continue
    except:
        data["fancy_markets"] = []

    # --- Nested iframe URL ---
    data["nested_iframe_url"] = None
    try:
        outer_iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(outer_iframe)
        nested_iframe = driver.find_element(By.TAG_NAME, "iframe")
        data["nested_iframe_url"] = nested_iframe.get_attribute("src")
        driver.switch_to.default_content()
    except Exception:
        driver.switch_to.default_content()
        data["nested_iframe_url"] = None

    # --- Teams & Scores inside iframe ---
    data["teams"] = []
    if data["nested_iframe_url"]:
        try:
            driver.switch_to.frame(outer_iframe)
            driver.switch_to.frame(nested_iframe)
            teams = driver.find_elements(By.CSS_SELECTOR, "div.team")

            for team in teams:
                try:
                    try:
                        team_name_el = team.find_element(By.CSS_SELECTOR, "div.team-name")
                        team_name = team_name_el.text.strip()
                    except:
                        team_name = team.find_element(By.CSS_SELECTOR, "div.team-short-name").text.strip()

                    try:
                        score_el = team.find_element(By.CSS_SELECTOR, "div.team-score-and-overs")
                        score = score_el.text.strip()
                    except:
                        score = "[Score Not Loaded Yet]"

                    data["teams"].append({"team_name": team_name, "score": score})
                except:
                    continue
        except:
            data["teams"] = []
        finally:
            driver.switch_to.default_content()

    return data

# --- SAVE TO JSON ---
def save_data_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- MAIN LOOP ---
try:
    driver.get(main_url)  # Load the page once at the start

    while True:
        scraped_data = scrape_market_data()
        save_data_to_json(scraped_data, output_file)
        print(f"[✓] Data updated and saved to '{output_file}'")
        time.sleep(0.2)  # Small delay for rapid updates
except KeyboardInterrupt:
    print("\n[!] Keyboard interrupt received. Exiting...")
finally:
    driver.quit()








# import json
# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

# # Setup Chrome driver
# options = Options()
# options.add_argument("--start-maximized")
# # options.add_argument("--headless")  # Uncomment for headless mode

# driver = webdriver.Chrome(options=options)
# wait = WebDriverWait(driver, 30)

# main_url = "https://www.wickspin24.live/#/full-market/4-34719324?marketId=1.247724277"
# output_file = "WikSpinLiv_2.json"

# def get_text_when_nonempty(parent, tag_name, timeout=5):
#     try:
#         el = WebDriverWait(parent, timeout).until(
#             lambda e: e.find_element(By.TAG_NAME, tag_name).text.strip() != ""
#         )
#         return parent.find_element(By.TAG_NAME, tag_name).text.strip()
#     except TimeoutException:
#         return ""

# def scrape_market_data():
#     data = {}

#     driver.get(main_url)

#     ### STEP 1: Extract Market Depth ###
#     try:
#         wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="betLimit"]')))
#         bet_limit_div = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="betLimit"]')
#         spans = bet_limit_div.find_elements(By.TAG_NAME, "span")

#         if len(spans) >= 2:
#             label = spans[0].text.strip()
#             value = spans[1].text.strip()
#             data["market_depth"] = {label: value}
#         else:
#             data["market_depth"] = {}
#     except Exception:
#         data["market_depth"] = {}

#     ### STEP 2: Extract Exchange Odds ###
#     data["exchange_odds"] = []
#     try:
#         wait.until(EC.presence_of_element_located((By.CLASS_NAME, "exchange_panel_line")))
#         match_lines = driver.find_elements(By.CLASS_NAME, "exchange_panel_line")

#         for line in match_lines:
#             try:
#                 name = line.find_element(By.TAG_NAME, "h2").text.split("\n")[0]

#                 back_elem = line.find_element(By.CSS_SELECTOR, "div[title='BACK']")
#                 back_odds = back_elem.find_element(By.TAG_NAME, "h3").text.strip()
#                 back_volume = back_elem.find_element(By.TAG_NAME, "p").text.strip()

#                 lay_elem = line.find_element(By.CSS_SELECTOR, "div[title='LAY']")
#                 lay_odds = lay_elem.find_element(By.TAG_NAME, "h3").text.strip()
#                 lay_volume = lay_elem.find_element(By.TAG_NAME, "p").text.strip()

#                 data["exchange_odds"].append({
#                     "team": name,
#                     "back": {"odds": back_odds, "volume": back_volume},
#                     "lay": {"odds": lay_odds, "volume": lay_volume}
#                 })
#             except Exception:
#                 continue
#     except Exception:
#         data["exchange_odds"] = []

#     ### STEP 3: Fancy Bet Markets ###
#     data["fancy_markets"] = []
#     try:
#         containers = driver.find_elements(By.CSS_SELECTOR, 'div.mb-1px.px-1.relative')

#         for container in containers:
#             market = {}
#             try:
#                 driver.execute_script("arguments[0].scrollIntoView(true);", container)
#                 time.sleep(0.5)

#                 title = container.find_element(By.TAG_NAME, "h2").text.strip()
#                 market["title"] = title

#                 try:
#                     status = container.find_element(By.CSS_SELECTOR, 'div[data-testid="fancybet-market-status"]').text.strip()
#                 except:
#                     status = "Active"
#                 market["status"] = status

#                 if status.lower() == "suspend":
#                     market["no"] = {"odds": None, "value": None}
#                     market["yes"] = {"odds": None, "value": None}
#                 else:
#                     try:
#                         no_option = container.find_element(By.CSS_SELECTOR, 'div[title="NO"]')
#                         no_odds = get_text_when_nonempty(no_option, "h3") or "N/A"
#                         no_value = get_text_when_nonempty(no_option, "p") or "N/A"
#                         market["no"] = {"odds": no_odds, "value": no_value}
#                     except Exception:
#                         market["no"] = {"odds": "N/A", "value": "N/A"}

#                     try:
#                         yes_option = container.find_element(By.CSS_SELECTOR, 'div[title="YES"]')
#                         yes_odds = get_text_when_nonempty(yes_option, "h3") or "N/A"
#                         yes_value = get_text_when_nonempty(yes_option, "p") or "N/A"
#                         market["yes"] = {"odds": yes_odds, "value": yes_value}
#                     except Exception:
#                         market["yes"] = {"odds": "N/A", "value": "N/A"}
#                 data["fancy_markets"].append(market)
#             except Exception:
#                 continue
#     except Exception:
#         data["fancy_markets"] = []

#     ### STEP 4: Get Nested iFrame URL ###
#     nested_iframe_url = None
#     try:
#         outer_iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
#         driver.switch_to.frame(outer_iframe)

#         nested_iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
#         nested_iframe_url = nested_iframe.get_attribute("src")

#         driver.switch_to.default_content()
#     except Exception:
#         nested_iframe_url = None

#     data["nested_iframe_url"] = nested_iframe_url

#     ### STEP 5: Navigate to Nested iFrame URL and Extract Scores ###
#     data["teams"] = []
#     if nested_iframe_url:
#         try:
#             driver.get(nested_iframe_url)
#             wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.team")))
#             teams = driver.find_elements(By.CSS_SELECTOR, "div.team")

#             for team in teams:
#                 try:
#                     try:
#                         team_name_el = team.find_element(By.CSS_SELECTOR, "div.team-name")
#                         WebDriverWait(team, 5).until(lambda t: team_name_el.text.strip() != "")
#                         team_name = team_name_el.text.strip()
#                     except:
#                         try:
#                             team_name = team.find_element(By.CSS_SELECTOR, "div.team-short-name").text.strip()
#                         except:
#                             team_name = team.get_attribute("innerText").split("\n")[0].strip() or "[Unknown Team]"

#                     try:
#                         score_el = team.find_element(By.CSS_SELECTOR, "div.team-score-and-overs")
#                         WebDriverWait(team, 5).until(lambda t: score_el.text.strip() != "")
#                         score = score_el.text.strip()
#                     except TimeoutException:
#                         score = "[Score Not Loaded Yet]"
#                     except:
#                         score = "[Score Missing]"

#                     data["teams"].append({"team_name": team_name, "score": score})
#                 except Exception:
#                     continue
#         except Exception:
#             data["teams"] = []
    
#     return data

# def save_data_to_json(data, filename):
#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)

# try:
#     while True:
#         scraped_data = scrape_market_data()
#         save_data_to_json(scraped_data, output_file)
#         print(f"[✓] Data updated and saved to {output_file}")
#         time.sleep(0.5)
# except KeyboardInterrupt:
#     print("\n[!] Exiting and closing driver...")
# finally:
#     driver.quit()

    
# driver.quit()



