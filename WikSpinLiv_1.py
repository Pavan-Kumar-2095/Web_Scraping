import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

chrome_options = Options()

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.wickspin24.live/#/sports')

wait = WebDriverWait(driver, 15)

wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.sport-type-filter-ul')))


all_button = wait.until(
    EC.element_to_be_clickable((
        By.XPATH,
        "//ul[contains(@class,'sport-type-filter-ul')]//li[.//span[text()='All']]"
    ))
)
all_button.click()
print("✅ Clicked 'All' filter button")


dropdown = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".shadow-all-button"))
)
dropdown.click()


option = wait.until(
    EC.element_to_be_clickable((
        By.XPATH,
        "//span[contains(@class, 'item-text') and normalize-space(text())='by Matched']"
    ))
)
option.click()
print("✅ Selected 'by Matched' from dropdown")


time.sleep(2)


sections = wait.until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "mb-4"))
)

for index, section in enumerate(sections, 1):
    try:
     
        sport_name = section.find_element(By.CSS_SELECTOR, ".text-event-tab-icon").text.strip()

     
        matches = section.find_elements(By.CLASS_NAME, "truncate")

        print(f"\n{index}. Sport: {sport_name}")
        for match_index, match in enumerate(matches, 1):
            match_name = match.text.strip()
            if not match_name:
                continue  
            print(f"   {match_index}. Match: {match_name}")


    except Exception as e:
        print(f"{index}. ⚠️ Error extracting sport or matches: {e}")


all_sports = []

for index, section in enumerate(sections, 1):
    try:
        sport_name = section.find_element(By.CSS_SELECTOR, ".text-event-tab-icon").text.strip()
        matches = section.find_elements(By.CLASS_NAME, "truncate")

        sport_dict = {
            "sport": sport_name,
            "matches": []
        }

        for match in matches:
            match_name = match.text.strip()
            if not match_name:
                continue
            sport_dict["matches"].append(match_name)

        all_sports.append(sport_dict)

    except Exception as e:
        print(f"{index}. ⚠️ Error extracting sport or matches: {e}")


with open("sports_matches.json", "w", encoding="utf-8") as f:
    json.dump(all_sports, f, indent=4, ensure_ascii=False)

print("✅ Data saved to sports_matches.json")