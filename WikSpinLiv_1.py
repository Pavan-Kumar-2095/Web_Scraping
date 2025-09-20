import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

def safe_click(driver, element, retries=3):
    for _ in range(retries):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            element.click()
            return
        except ElementClickInterceptedException:
            time.sleep(1)
    raise ElementClickInterceptedException("Element could not be clicked after multiple attempts.")

def scrape_data():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")  # uncomment to run headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.wickspin24.live/#/sports")
        wait = WebDriverWait(driver, 20)

        # Click 'All' filter
        all_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//ul[contains(@class,'sport-type-filter-ul')]//li[.//span[text()='All']]")
        ))
        safe_click(driver, all_button)
        print("Clicked 'All' filter")

        # Open sorting dropdown
        dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".shadow-all-button")))
        safe_click(driver, dropdown)

        # Select 'by Matched'
        option = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class, 'item-text') and normalize-space(text())='by Matched']")
        ))
        safe_click(driver, option)
        print("Selected 'by Matched'")

        time.sleep(3)

        all_sports = []

        # Get all sport sections
        sections = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "mb-4")))

        for sport_index in range(len(sections)):
            sections = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "mb-4")))
            section = sections[sport_index]

            try:
                sport_name = section.find_element(By.CSS_SELECTOR, ".text-event-tab-icon").text.strip()
                print(f"Processing sport: {sport_name}")

                sport_data = {
                    "sport": sport_name,
                    "matches": []
                }

                matches = section.find_elements(By.CSS_SELECTOR, ".event-block-item-row")

                for match_index in range(len(matches)):
                    # Refresh sections and matches to avoid stale elements
                    sections = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "mb-4")))
                    section = sections[sport_index]
                    matches = section.find_elements(By.CSS_SELECTOR, ".event-block-item-row")

                    match = matches[match_index]
                    match_name = match.find_element(By.CSS_SELECTOR, ".truncate").text.strip()
                    print(f"  Match: {match_name}")

                    fancy_bet = bool(match.find_elements(By.CSS_SELECTOR, ".icon-fancybet"))
                    sportsbook = bool(match.find_elements(By.CSS_SELECTOR, ".icon-sportsbook"))

                    # Try to click inner clickable element for better success
                    try:
                        clickable = match.find_element(By.CSS_SELECTOR, ".truncate")
                        if clickable.is_displayed() and clickable.is_enabled():
                            safe_click(driver, clickable)
                        else:
                            driver.execute_script("arguments[0].click();", clickable)
                    except Exception as e:
                        print(f"  Warning: couldn't click inner element, trying outer element: {e}")
                        safe_click(driver, match)

                    wait.until(lambda d: "full-market" in d.current_url)
                    current_url = driver.current_url
                    print(f"    URL: {current_url}")

                    sport_data["matches"].append({
                        "match": match_name,
                        "url": current_url,
                        "fancy_bet": fancy_bet,
                        "sportsbook": sportsbook
                    })

                    driver.back()
                    wait.until(lambda d: d.current_url.startswith("https://www.wickspin24.live/#/sports"))
                    time.sleep(2)

                all_sports.append(sport_data)

            except Exception as e:
                print(f"Error processing sport section '{sport_name}': {e}")

        # Save data to JSON file
        with open("WikSpinLiv_1.json", "w", encoding="utf-8") as f:
            json.dump(all_sports, f, indent=4, ensure_ascii=False)

        print("✅ Data saved successfully")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_data()
