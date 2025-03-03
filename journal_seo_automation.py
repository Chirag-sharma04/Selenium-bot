from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)  # Increased wait time

# Function to search for a keyword
def search_keyword(keyword):
    try:
        driver.get("https://backlinko.com/tools/keyword-generator")
        time.sleep(5)

        try:
            search_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Your keyword (e.g. paleo diet)']")))
            search_box.click()
        except Exception as e:
            print(f"[ERROR] Search box not found: {e}")
            return

        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        try:
            # Wait for the table to be present
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.results-table")))

        except Exception as e:
            print(f"[WARNING] Results table not found: {e}")
            return

        time.sleep(3)

        results = driver.find_elements(By.CSS_SELECTOR, "table.results-table tbody tr td:nth-child(1)")
        if results:
            for result in results:
                print(result.text)
        else:
            print("[WARNING] No results found. Page structure may have changed.")

    except Exception as e:
        print(f"[ERROR] Error processing '{keyword}': {e}")

keywords = [
    "Gratitude journal", "Productivity journal", "Self care journal",
    "Mindfulness journal", "Manifestation journal", "Reflection journal"
]

for keyword in keywords:
    print(f"Searching for: {keyword}")
    search_keyword(keyword)

driver.quit()