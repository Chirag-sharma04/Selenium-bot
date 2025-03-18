# RyRob Keyword Scraper

This Python script automates the scraping of keyword data from RyRob's keyword tool. It uses Selenium with undetected-chromedriver to bypass basic anti-automation detection. The script is designed to input seed keywords, submit searches, and extract keyword suggestions along with their volume and difficulty.

## Prerequisites

* Python 3.x
* Chrome browser installed
* Selenium library (`pip install selenium`)
* undetected-chromedriver (`pip install undetected-chromedriver`)

## Setup

1.  **Install Dependencies:**

    ```bash
    pip install selenium undetected-chromedriver
    ```

## Usage

1.  **Run the Script:**

    ```bash
    python your_script_name.py
    ```

2.  **Keyword Categories:**
    * The script iterates through a predefined list of journal categories.
    * You can modify the `journal_categories` list in the script to include your desired seed keywords or categories.
3.  **CAPTCHA Handling:**
    * The script includes basic CAPTCHA detection. If a CAPTCHA is detected, the script will pause and prompt you to solve it manually.
4.  **Output:**
    * The script will create a CSV file for each seed keyword, containing the extracted keyword data.
    * The CSV files will be named `extracted_{seed_keyword}.csv`.
    * The script will print progress and status messages to the console.

## Code Explanation

* **`setup_driver()`:**
    * Initializes an undetected Chrome driver with specified options to avoid detection.
* **`random_sleep()`:**
    * Introduces random delays to simulate human behavior.
* **`solve_captcha()`:**
    * Checks for CAPTCHA elements and prompts the user to solve them manually.
* **`scrape_ryrob_keywords()`:**
    * Navigates to the RyRob keyword tool.
    * Inputs the seed keyword into the search box.
    * Submits the search and waits for the results to load.
    * Extracts keyword data (keyword, volume, difficulty) from the results.
    * Handles potential errors and timeouts.
    * Calls `save_keywords_to_csv()` to save the extracted data.
* **`save_keywords_to_csv()`:**
    * Saves the extracted keyword data to a CSV file.
    * Handles cases where no data is available.
* **Main Execution:**
    * Iterates through the `journal_categories` list.
    * Calls `scrape_ryrob_keywords()` for each category.
    * Closes the browser after completing all searches.

## Notes

* This script relies on the HTML structure of the RyRob keyword tool. If the website changes its HTML, the script may need to be updated.
* The script uses `undetected-chromedriver` to bypass basic anti-automation detection, but it may not be effective against advanced detection methods.
* The CAPTCHA handling is basic and requires manual intervention.
* Adjust the wait times and delays as needed to ensure reliable scraping.
* Because RyRob uses dynamic content, the css selectors used may need to be updated frequently.
* Error handling has been added to improve stability.
