from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random

# Set up Selenium WebDriver with more browser-like behavior
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
# Add a realistic user agent
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
# Disable automation flags
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 60)  # Increased wait time to 60 seconds

def random_sleep(min_seconds=1, max_seconds=3):
    """Sleep for a random amount of time to mimic human behavior"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def check_and_handle_popups():
    """Check for and close any popups or overlays"""
    try:
        # Common popup/overlay selectors
        popup_selectors = [
            "div.popup", ".modal", ".overlay", ".cookie-banner", 
            "button.close", "button[aria-label='Close']", ".modal-close"
        ]
        
        for selector in popup_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed():
                    print(f"[INFO] Found popup/overlay with selector {selector}, attempting to close")
                    try:
                        element.click()
                        random_sleep()
                        print("[INFO] Clicked on popup/overlay element")
                    except:
                        print("[INFO] Failed to click popup element directly")
                        # Try to use JavaScript to close it
                        driver.execute_script("arguments[0].click();", element)
                        random_sleep()
    except Exception as e:
        print(f"[INFO] Error handling popups: {e}")

def search_keyword(keyword):
    try:
        print(f"[INFO] Opening website for keyword: {keyword}")
        driver.get("https://backlinko.com/tools/keyword-generator")
        random_sleep(5, 8)  # Longer initial wait

        # Debug page title and URL to verify we're on the right page
        print(f"[DEBUG] Page title: {driver.title}")
        print(f"[DEBUG] Current URL: {driver.current_url}")
        
        # Check for popups before interacting with the page
        check_and_handle_popups()
        
        # Take a screenshot of the initial page
        driver.save_screenshot(f"initial_page_{keyword.replace(' ', '_')}.png")

        try:
            # Try to find the search box
            print("[INFO] Looking for search box...")
            search_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Your keyword (e.g. paleo diet)']")))
            print("[INFO] Found search box by placeholder")
            
            # Interact with the search box more like a human
            search_box.click()
            random_sleep()
            search_box.clear()
            random_sleep()
            
            # Type the keyword with random delays between characters
            for char in keyword:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
                
            print(f"[INFO] Entered keyword: {keyword}")
            random_sleep()
            
            # Try clicking a search button instead of pressing Enter
            try:
                search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .search-button, button.submit")
                search_button.click()
                print("[INFO] Clicked search button")
            except:
                # Fall back to pressing Enter if no button found
                search_box.send_keys(Keys.RETURN)
                print("[INFO] Submitted search with Enter key")
            
            # Wait longer for results to load
            print("[INFO] Waiting for results to load...")
            random_sleep(10, 15)
            
            # Take a screenshot after search
            driver.save_screenshot(f"after_search_{keyword.replace(' ', '_')}.png")
            
            # Check for any iframes and switch to them if needed
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                print(f"[INFO] Found {len(iframes)} iframes on the page")
                for i, iframe in enumerate(iframes):
                    try:
                        print(f"[INFO] Switching to iframe {i}")
                        driver.switch_to.frame(iframe)
                        driver.save_screenshot(f"iframe_{i}_{keyword.replace(' ', '_')}.png")
                        # Look for results in the iframe
                        elements = driver.find_elements(By.CSS_SELECTOR, "table, .results, .keyword")
                        if elements:
                            print(f"[INFO] Found potential results in iframe {i}")
                        # Switch back to main content
                        driver.switch_to.default_content()
                    except Exception as e:
                        print(f"[ERROR] Error with iframe {i}: {e}")
                        driver.switch_to.default_content()
            
            # Check if we need to wait for AJAX content
            print("[INFO] Checking page for AJAX loaders...")
            loaders = driver.find_elements(By.CSS_SELECTOR, ".loading, .spinner, .loader")
            if loaders:
                for loader in loaders:
                    if loader.is_displayed():
                        print("[INFO] Found active loader, waiting for it to disappear")
                        try:
                            WebDriverWait(driver, 30).until_not(
                                EC.visibility_of(loader)
                            )
                            print("[INFO] Loader disappeared")
                        except:
                            print("[WARNING] Loader did not disappear within timeout")
            
            # Analyze the page structure to find results
            print("[INFO] Analyzing page structure for results...")
            
            # Look for tables
            tables = driver.find_elements(By.TAG_NAME, "table")
            if tables:
                print(f"[INFO] Found {len(tables)} tables on the page")
                for i, table in enumerate(tables):
                    print(f"[INFO] Table {i} classes: {table.get_attribute('class')}")
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    print(f"[INFO] Table {i} has {len(rows)} rows")
                    if len(rows) > 1:  # If there's more than just a header row
                        print(f"[SUCCESS] Found results in table {i}:")
                        for row in rows[1:]:  # Skip header row
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if cells and len(cells) > 0:
                                print(cells[0].text)  # Print first column
            else:
                print("[INFO] No tables found on the page")
                
                # Look for any elements that might contain keyword results
                print("[INFO] Looking for any elements that might contain keyword results...")
                potential_result_containers = driver.find_elements(
                    By.CSS_SELECTOR, 
                    "div.results, .keyword-list, .keyword-results, .suggestions, ul li, ol li, .result-item"
                )
                
                if potential_result_containers:
                    print(f"[INFO] Found {len(potential_result_containers)} potential result containers")
                    for container in potential_result_containers:
                        if container.is_displayed() and container.text.strip():
                            print(f"[INFO] Container text: {container.text.strip()[:100]}...")
                
                # Save the entire page source for analysis
                with open(f"page_source_{keyword.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"[INFO] Saved page source to page_source_{keyword.replace(' ', '_')}.html")
                
                # Execute JavaScript to get all visible text on the page
                print("[INFO] Extracting all visible text from the page...")
                visible_text = driver.execute_script("""
                    return Array.from(document.querySelectorAll('body *'))
                        .filter(el => el.offsetParent !== null && !['SCRIPT', 'STYLE'].includes(el.tagName))
                        .map(el => el.textContent.trim())
                        .filter(text => text.length > 0 && text.length < 100)
                        .join('\\n');
                """)
                
                print("[INFO] Sample of visible text:")
                lines = visible_text.split('\n')
                for line in lines[:20]:  # Print first 20 lines as a sample
                    if line.strip():
                        print(line.strip())

        except Exception as e:
            print(f"[ERROR] Error during search process: {e}")
            driver.save_screenshot(f"error_during_search_{keyword.replace(' ', '_')}.png")

    except Exception as e:
        print(f"[ERROR] Fatal error processing '{keyword}': {e}")

# List of keywords to search
keywords = [
    "Gratitude journal", "Productivity journal", "Self care journal",
    "Mindfulness journal", "Manifestation journal", "Reflection journal"
]

# Process each keyword
for keyword in keywords:
    print(f"\n{'='*50}\nSearching for: {keyword}\n{'='*50}")
    search_keyword(keyword)
    random_sleep(5, 10)  # Random delay between searches

# Clean up
print("[INFO] Finished all searches, closing browser")
driver.quit()

