import time
import random
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Setup undetected Chrome driver
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 30)

def random_sleep(min_seconds=1, max_seconds=3):
    time.sleep(random.uniform(min_seconds, max_seconds))

def solve_captcha():
    print("[INFO] Checking for CAPTCHA...")
    try:
        captcha_element = driver.find_element(By.XPATH, "//*[contains(text(), 'verify that you are human')]")
        print("[ALERT] CAPTCHA detected! Please solve it manually.")
        input("[PROMPT] Press Enter after solving the CAPTCHA...")
    except NoSuchElementException:
        print("[INFO] No CAPTCHA detected. Continuing...")

def scrape_ryrob_keywords(seed_keyword, max_keywords=15):
    """Scrape keywords from RyRob's keyword tool"""
    keywords = []
    try:
        print(f"Scraping keywords from RyRob for: {seed_keyword} (max: {max_keywords})")
        driver.get("https://www.ryrob.com/keyword-tool/")
        random_sleep(5, 8)
        
        solve_captcha()  # Check for CAPTCHA before proceeding

        search_box = wait.until(EC.element_to_be_clickable((By.ID, "keyword-tool-phrase")))
        search_box.clear()
        for char in seed_keyword:
            search_box.send_keys(char)
            random_sleep(0.2, 0.5)
        search_box.send_keys(Keys.RETURN)
        
        print("[INFO] Submitted search")
        random_sleep(10, 15)

        try:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "keyword-item")))
            keyword_items = driver.find_elements(By.CLASS_NAME, "keyword-item")
            
            if not keyword_items:
                print("[ERROR] No keyword rows found! Taking a screenshot...")
                driver.save_screenshot("debug_no_results.png")
            
            keyword_count = 0
            for item in keyword_items:
                if keyword_count >= max_keywords:
                    break
                try:
                    keyword_text = item.find_element(By.CSS_SELECTOR, ".info-block span[x-text='details.keyword']").text.strip()
                    volume_text = item.find_element(By.CSS_SELECTOR, ".info-block span[x-text='kFormatter(details.volume)']").text.strip()
                    difficulty_text = item.find_element(By.CSS_SELECTOR, ".info-block span[x-text='details.competition']").text.strip()

                    if keyword_text:
                        keywords.append({
                            "keyword": keyword_text,
                            "volume": volume_text if volume_text else "0",
                            "difficulty": difficulty_text if difficulty_text else "0"
                        })
                        keyword_count += 1
                        print(f"✅ Extracted ({keyword_count}/{max_keywords}): {keyword_text} | Volume: {volume_text} | Difficulty: {difficulty_text}")
                except NoSuchElementException:
                    continue

        except TimeoutException:
            print("[ERROR] Keywords not found within timeout.")

        print(f"✅ Found {len(keywords)} keywords from RyRob for '{seed_keyword}' (limited to {max_keywords})")
        save_keywords_to_csv(keywords, f"extracted_{seed_keyword}.csv")

    except WebDriverException as e:
        print(f"[ERROR] WebDriver exception: {e}")

def save_keywords_to_csv(data, filename):
    if not data:
        print(f"[WARNING] No data to save for {filename}")
        return

    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["keyword", "volume", "difficulty"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"📁 Saved keyword data to {filename} with {len(data)} keywords")
    except Exception as e:
        print(f"[ERROR] Failed to save CSV: {e}")

journal_categories = [
    "Gratitude & Positivity Journals",
    "Daily,Weekly & Yearly Journals",
    # "Productivity & Goal-Setting Journals",
    # "Mental Health & Self-Care Journals",
    # "Self-Improvement & Growth Journals",
    # "Manifestation & Law of Attraction Journals",
    # "Reflection & Thought Journals",
    # "Specialized Journals (Shadow Work, ADHD, etc.)",
    # "Spiritual & Mindfulness Journals",
    # "Relationship & Emotional Journals",
    # "Journaling Techniques & Guides",
    # "Themed & Brand-Specific Journals",
    # "Online & Digital Journaling",
    # "Bullet Journals & Creative Journaling",
    # "Miscellaneous & Notable Journals"
]

for category in journal_categories:
    print(f"\n{'='*50}\n🔍 Searching for: {category}\n{'='*50}")
    scrape_ryrob_keywords(category, max_keywords=15)
    random_sleep(5, 10)

print("\n✅ All searches completed. Closing browser.")
driver.quit()
