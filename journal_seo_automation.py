from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import csv
import os
from bs4 import BeautifulSoup  # Added for HTML parsing

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

def save_keywords_to_csv(keyword, results):
    """Save the extracted keywords to a CSV file"""
    filename = f"keywords_{keyword.replace(' ', '_')}.csv"
    
    # Create a directory for results if it doesn't exist
    os.makedirs("keyword_results", exist_ok=True)
    filepath = os.path.join("keyword_results", filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Keyword'])  # Header
        for result in results:
            writer.writerow([result])
    
    print(f"[SUCCESS] Saved {len(results)} keywords to {filepath}")

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
            
            # Initialize all_keywords list
            all_keywords = []
            
            # Check for any iframes and switch to them if needed
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                print(f"[INFO] Found {len(iframes)} iframes on the page")
                for i, iframe in enumerate(iframes):
                    try:
                        print(f"[INFO] Switching to iframe {i}")
                        driver.switch_to.frame(iframe)
                        driver.save_screenshot(f"iframe_{i}_{keyword.replace(' ', '_')}.png")
                        
                        # Save iframe source for debugging
                        iframe_source = driver.page_source
                        with open(f"iframe_{i}_source_{keyword.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
                            f.write(iframe_source)
                        print(f"[DEBUG] Saved iframe {i} source")
                        
                        # Try to extract keywords using multiple methods
                        iframe_keywords = []
                        
                        # Method 1: Direct table extraction
                        iframe_tables = driver.find_elements(By.TAG_NAME, "table")
                        if iframe_tables:
                            print(f"[INFO] Found {len(iframe_tables)} tables in iframe {i}")
                            for j, table in enumerate(iframe_tables):
                                print(f"[INFO] Processing table {j} in iframe {i}")
                                # Debug table structure
                                print(f"[DEBUG] Table HTML: {table.get_attribute('outerHTML')[:200]}...")
                                
                                table_keywords = extract_keywords_from_table(table)
                                if table_keywords:
                                    iframe_keywords.extend(table_keywords)
                                    print(f"[SUCCESS] Extracted {len(table_keywords)} keywords from table {j} in iframe {i}")
                        
                        # Method 2: Parse with BeautifulSoup
                        soup = BeautifulSoup(iframe_source, 'html.parser')
                        bs_keywords = extract_keywords_with_bs4(soup)
                        if bs_keywords:
                            iframe_keywords.extend(bs_keywords)
                            print(f"[SUCCESS] Extracted {len(bs_keywords)} keywords with BeautifulSoup in iframe {i}")
                        
                        # Method 3: JavaScript extraction
                        js_keywords = extract_keywords_with_js()
                        if js_keywords:
                            iframe_keywords.extend(js_keywords)
                            print(f"[SUCCESS] Extracted {len(js_keywords)} keywords with JavaScript in iframe {i}")
                        
                        # Add iframe keywords to all keywords
                        if iframe_keywords:
                            all_keywords.extend(iframe_keywords)
                        
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
            
            # Save the entire page source for analysis
            page_source = driver.page_source
            with open(f"page_source_{keyword.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print(f"[INFO] Saved page source to page_source_{keyword.replace(' ', '_')}.html")
            
            # Method 1: Look for tables in the main page
            tables = driver.find_elements(By.TAG_NAME, "table")
            if tables:
                print(f"[INFO] Found {len(tables)} tables on the page")
                for i, table in enumerate(tables):
                    print(f"[INFO] Table {i} classes: {table.get_attribute('class')}")
                    # Debug table structure
                    print(f"[DEBUG] Table {i} HTML: {table.get_attribute('outerHTML')[:200]}...")
                    
                    # Debug table rows
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    print(f"[INFO] Table {i} has {len(rows)} rows")
                    
                    # Debug first row content
                    if rows:
                        try:
                            first_row = rows[0]
                            cells = first_row.find_elements(By.TAG_NAME, "td")
                            if cells:
                                print(f"[DEBUG] First row has {len(cells)} cells")
                                for j, cell in enumerate(cells):
                                    print(f"[DEBUG] Cell {j} text: '{cell.text}'")
                            else:
                                print("[DEBUG] No cells found in first row")
                        except Exception as e:
                            print(f"[ERROR] Error debugging first row: {e}")
                    
                    # Try to extract keywords
                    table_keywords = extract_keywords_from_table(table)
                    if table_keywords:
                        all_keywords.extend(table_keywords)
                        print(f"[SUCCESS] Extracted {len(table_keywords)} keywords from table {i}")
            else:
                print("[INFO] No tables found on the page")
            
            # Method 2: Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            bs_keywords = extract_keywords_with_bs4(soup)
            if bs_keywords:
                all_keywords.extend(bs_keywords)
                print(f"[SUCCESS] Extracted {len(bs_keywords)} keywords with BeautifulSoup")
            
            # Method 3: JavaScript extraction
            js_keywords = extract_keywords_with_js()
            if js_keywords:
                all_keywords.extend(js_keywords)
                print(f"[SUCCESS] Extracted {len(js_keywords)} keywords with JavaScript")
            
            # Method 4: Look for any elements that might contain keyword results
            print("[INFO] Looking for any elements that might contain keyword results...")
            element_keywords = extract_keywords_from_other_elements()
            if element_keywords:
                all_keywords.extend(element_keywords)
                print(f"[SUCCESS] Extracted {len(element_keywords)} keywords from other elements")
            
            # Remove duplicates and save results
            all_keywords = list(set(all_keywords))
            if all_keywords:
                print(f"[SUCCESS] Found a total of {len(all_keywords)} unique keywords")
                # Print first 10 keywords for verification
                print("[DEBUG] Sample of keywords found:")
                for i, kw in enumerate(all_keywords[:10]):
                    print(f"  {i+1}. {kw}")
                save_keywords_to_csv(keyword, all_keywords)
            else:
                print("[WARNING] No keywords were found for this search")
                
                # Try one last method: direct HTML parsing for specific patterns
                print("[INFO] Trying direct HTML parsing for keyword patterns...")
                pattern_keywords = extract_keywords_by_pattern(page_source)
                if pattern_keywords:
                    print(f"[SUCCESS] Found {len(pattern_keywords)} keywords by pattern matching")
                    save_keywords_to_csv(keyword, pattern_keywords)
                else:
                    print("[ERROR] All extraction methods failed to find keywords")

        except Exception as e:
            print(f"[ERROR] Error during search process: {e}")
            driver.save_screenshot(f"error_during_search_{keyword.replace(' ', '_')}.png")

    except Exception as e:
        print(f"[ERROR] Fatal error processing '{keyword}': {e}")

def extract_keywords_from_table(table):
    """Extract keywords from a table element with enhanced debugging"""
    keywords = []
    try:
        # Try multiple methods to extract table data
        
        # Method 1: Standard Selenium approach
        rows = table.find_elements(By.TAG_NAME, "tr")
        print(f"[DEBUG] Found {len(rows)} rows in table")
        
        for row_idx, row in enumerate(rows):
            try:
                # Try to get cells with both td and th tags
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    cells = row.find_elements(By.TAG_NAME, "th")
                
                if cells:
                    print(f"[DEBUG] Row {row_idx} has {len(cells)} cells")
                    for cell_idx, cell in enumerate(cells):
                        try:
                            # Try multiple ways to get text
                            cell_text = cell.text.strip()
                            if not cell_text:
                                cell_text = cell.get_attribute("textContent").strip()
                            
                            if cell_text:
                                print(f"[DEBUG] Cell {row_idx},{cell_idx} text: '{cell_text}'")
                                # Only add if it looks like a keyword (not just a number or single character)
                                if len(cell_text) > 2 and not cell_text.isdigit():
                                    keywords.append(cell_text)
                                    print(f"[INFO] Found keyword in table: {cell_text}")
                        except Exception as cell_e:
                            print(f"[ERROR] Error extracting text from cell {row_idx},{cell_idx}: {cell_e}")
            except Exception as row_e:
                print(f"[ERROR] Error processing row {row_idx}: {row_e}")
        
        # Method 2: JavaScript approach
        try:
            table_html = table.get_attribute("outerHTML")
            js_result = driver.execute_script("""
                var tableHTML = arguments[0];
                var tempDiv = document.createElement('div');
                tempDiv.innerHTML = tableHTML;
                var table = tempDiv.querySelector('table');
                var results = [];
                
                if (table) {
                    var rows = table.querySelectorAll('tr');
                    for (var i = 0; i < rows.length; i++) {
                        var cells = rows[i].querySelectorAll('td, th');
                        for (var j = 0; j < cells.length; j++) {
                            var text = cells[j].textContent.trim();
                            if (text && text.length > 2 && !/^\d+$/.test(text)) {
                                results.push(text);
                            }
                        }
                    }
                }
                
                return results;
            """, table_html)
            
            if js_result and isinstance(js_result, list):
                print(f"[DEBUG] JavaScript extracted {len(js_result)} items from table")
                for item in js_result:
                    if item not in keywords:
                        keywords.append(item)
                        print(f"[INFO] Found keyword via JavaScript: {item}")
        except Exception as js_e:
            print(f"[ERROR] JavaScript extraction failed: {js_e}")
    
    except Exception as e:
        print(f"[ERROR] Error extracting keywords from table: {e}")
    
    return keywords

def extract_keywords_with_bs4(soup):
    """Extract keywords using BeautifulSoup HTML parsing"""
    keywords = []
    try:
        # Look for tables
        tables = soup.find_all('table')
        print(f"[DEBUG] BeautifulSoup found {len(tables)} tables")
        
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"[DEBUG] Table {table_idx} has {len(rows)} rows")
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    text = cell.get_text().strip()
                    if text and len(text) > 2 and not text.isdigit():
                        keywords.append(text)
                        print(f"[INFO] BeautifulSoup found keyword: {text}")
        
        # Look for lists that might contain keywords
        lists = soup.find_all(['ul', 'ol'])
        for list_elem in lists:
            items = list_elem.find_all('li')
            for item in items:
                text = item.get_text().strip()
                if text and len(text) > 2 and not text.isdigit():
                    keywords.append(text)
                    print(f"[INFO] BeautifulSoup found keyword in list: {text}")
        
        # Look for divs with specific classes that might contain keywords
        keyword_divs = soup.find_all('div', class_=lambda c: c and any(x in c for x in ['keyword', 'result', 'suggestion']))
        for div in keyword_divs:
            text = div.get_text().strip()
            if text and len(text) > 2 and not text.isdigit():
                keywords.append(text)
                print(f"[INFO] BeautifulSoup found keyword in div: {text}")
    
    except Exception as e:
        print(f"[ERROR] BeautifulSoup extraction failed: {e}")
    
    return keywords

def extract_keywords_with_js():
    """Extract keywords using JavaScript execution"""
    keywords = []
    try:
        # Execute JavaScript to find text that looks like keywords
        js_result = driver.execute_script("""
            // Function to check if text looks like a keyword
            function isLikelyKeyword(text) {
                text = text.trim();
                return text.length > 2 && 
                       text.length < 100 && 
                       !(/^\\d+$/.test(text)) &&
                       text.indexOf(' ') > -1;  // Contains a space (likely a phrase)
            }
            
            var results = [];
            
            // Method 1: Get text from table cells
            var tableCells = document.querySelectorAll('td, th');
            for (var i = 0; i < tableCells.length; i++) {
                var text = tableCells[i].textContent.trim();
                if (isLikelyKeyword(text)) {
                    results.push(text);
                }
            }
            
            // Method 2: Get text from list items
            var listItems = document.querySelectorAll('li');
            for (var i = 0; i < listItems.length; i++) {
                var text = listItems[i].textContent.trim();
                if (isLikelyKeyword(text)) {
                    results.push(text);
                }
            }
            
            // Method 3: Get text from divs with keyword-related classes
            var keywordDivs = Array.from(document.querySelectorAll('div')).filter(function(div) {
                var className = div.className || '';
                return className.indexOf('keyword') > -1 || 
                       className.indexOf('result') > -1 || 
                       className.indexOf('suggestion') > -1;
            });
            
            for (var i = 0; i < keywordDivs.length; i++) {
                var text = keywordDivs[i].textContent.trim();
                if (isLikelyKeyword(text)) {
                    results.push(text);
                }
            }
            
            return results;
        """)
        
        if js_result and isinstance(js_result, list):
            print(f"[DEBUG] JavaScript extracted {len(js_result)} potential keywords")
            for item in js_result:
                keywords.append(item)
                print(f"[INFO] Found keyword via JavaScript: {item}")
    
    except Exception as e:
        print(f"[ERROR] JavaScript extraction failed: {e}")
    
    return keywords

def extract_keywords_from_other_elements():
    """Extract keywords from non-table elements that might contain results"""
    keywords = []
    try:
        # Common selectors for keyword results
        selectors = [
            "div.results li", ".keyword-list li", ".keyword-results li", 
            ".suggestions li", "ul.results li", "ol.results li", 
            ".result-item", "div.keyword", "span.keyword",
            ".keyword-ideas li", ".keyword-suggestions li"
        ]
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"[DEBUG] Found {len(elements)} elements with selector: {selector}")
            
            for element in elements:
                try:
                    if element.is_displayed():
                        # Try multiple ways to get text
                        text = element.text.strip()
                        if not text:
                            text = element.get_attribute("textContent").strip()
                        
                        if text and len(text) > 2 and not text.isdigit():
                            keywords.append(text)
                            print(f"[INFO] Found keyword in element: {text}")
                except Exception as elem_e:
                    print(f"[ERROR] Error processing element: {elem_e}")
    
    except Exception as e:
        print(f"[ERROR] Error extracting keywords from other elements: {e}")
    
    return keywords

def extract_keywords_by_pattern(html_source):
    """Extract keywords by pattern matching in the HTML source"""
    keywords = []
    try:
        # Use BeautifulSoup for parsing
        soup = BeautifulSoup(html_source, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text
        text = soup.get_text()
        
        # Split into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        
        # Filter lines that look like keywords
        for line in lines:
            # Skip empty lines or very short/long lines
            if not line or len(line) < 3 or len(line) > 100:
                continue
                
            # Skip lines that are just numbers
            if line.isdigit():
                continue
                
            # Skip lines without spaces (likely not keywords)
            if ' ' not in line:
                continue
                
            # Skip lines with too many spaces (likely paragraphs)
            if line.count(' ') > 10:
                continue
                
            # Skip lines with special characters that are unlikely in keywords
            if any(c in line for c in [':', ';', '=', '{', '}', '[', ']', '(', ')', '|', '\\']):
                continue
                
            # This line might be a keyword
            keywords.append(line)
            print(f"[INFO] Found potential keyword by pattern: {line}")
    
    except Exception as e:
        print(f"[ERROR] Pattern extraction failed: {e}")
    
    return keywords

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

# For testing purposes, print a message
print("Script execution completed successfully!")