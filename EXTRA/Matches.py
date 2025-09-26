import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


options = Options()
options.headless = True
options.add_argument("--headless")



driver = webdriver.Chrome(options=options)

url = 'https://www.cricketlineguru.com/cricket-schedule/upcoming/all'
driver.get(url)

wait = WebDriverWait(driver, 10)

try:
    toggle_container = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-sm-12.d-none.d-md-block"))
    )
    switch_button = toggle_container.find_element(By.CSS_SELECTOR, "button[role='switch']")
    driver.execute_script("arguments[0].scrollIntoView(true);", switch_button)
    time.sleep(1)

    try:
        switch_button.click()
        print("✅ Toggle switch clicked successfully with normal click.")
    except Exception as e_click:
        print(f"⚠️ Normal click failed, trying JS click: {e_click}")
        driver.execute_script("arguments[0].click();", switch_button)
        print("✅ Toggle switch clicked successfully with JS click.")

except Exception as e:
    print(f"⚠️ Could not click toggle switch: {e}")

time.sleep(5)  

soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

tbody = soup.find('tbody', class_='ng-star-inserted')
if not tbody:
    print("❌ Could not find matches tbody.")
    exit()

rows = tbody.find_all('tr', attrs={'match-key': True})
print(f"Total matches found: {len(rows)}\n")

matches = []

for tr in rows:
    tds = tr.find_all('td')

    td1 = tds[0] if len(tds) > 0 else None
    series_a = td1.find('a') if td1 else None
    series_name = series_a.get_text(strip=True) if series_a else 'N/A'
    match_date = td1.find('span', class_='d-block l-height').get_text(strip=True) if td1 and td1.find('span', class_='d-block l-height') else 'N/A'
    match_day = td1.find('span', class_='fixture-day').get_text(strip=True) if td1 and td1.find('span', class_='fixture-day') else 'N/A'

    td2 = tds[1] if len(tds) > 1 else None
    match_link = td2.find('a') if td2 else None
    match_title = match_link.get_text(strip=True) if match_link else 'N/A'

    venue_span = None
    if td2:
        for span in td2.find_all('span'):
            if not span.get('class'):
                venue_span = span
                break
    venue = venue_span.get_text(strip=True) if venue_span else 'N/A'

    status_span = td2.find('span', class_='inner_status m-upcoming ng-star-inserted') if td2 else None
    status = status_span.get_text(strip=True) if status_span else 'N/A'

    td3 = tds[2] if len(tds) > 2 else None
    time_text = td3.contents[0].strip() if td3 and td3.contents else 'N/A'
    gmt_div = td3.find('div', class_='initial_time ng-star-inserted') if td3 else None
    gmt_time = gmt_div.get_text(strip=True) if gmt_div else 'N/A'

    match_data = {
        'series': series_name,
        'date': match_date,
        'day': match_day,
        'match': match_title,
        'venue': venue,
        'time': time_text,
        'gmt_time': gmt_time,
        'status': status
    }

    matches.append(match_data)

    print(f"🏆 Series: {series_name}")
    print(f"📅 Date: {match_date} ({match_day})")
    print(f"🏏 Match: {match_title}")
    print(f"📍 Venue: {venue}")
    print(f"🕒 Time: {time_text} | GMT: {gmt_time}")
    print(f"📣 Status: {status}")
    print('-' * 50)


with open('cricket_matches.json', 'w', encoding='utf-8') as f:
    json.dump(matches, f, indent=4, ensure_ascii=False)

print(f"\n✅ Data saved to cricket_matches.json")
