import configparser
import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -----------------------------
# Configuration and Setup
# -----------------------------

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

SEARCH_TERMS = config['DEFAULT']['SearchTerms']
RESUME_PATH = config['DEFAULT']['ResumePath']
PAUSE_DURATION = int(config['DEFAULT']['PauseDuration'])

# Validate Resume Path
if not os.path.isfile(RESUME_PATH):
    print(f'Resume file not found at path: {RESUME_PATH}')
    logging.error(f'Resume file not found at path: {RESUME_PATH}')
    exit(1)

# Configure logging to both file and console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler('application_log.txt'),
        logging.StreamHandler()
    ]
)

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

# Initialize the WebDriver
try:
    driver = webdriver.Chrome(options=chrome_options)
    logging.info("Initialized Chrome WebDriver.")
except WebDriverException as e:
    logging.error(f'Error initializing Chrome WebDriver: {e}')
    exit(1)

# Maximize browser window
driver.maximize_window()
logging.info("Maximized browser window.")

# -----------------------------
# Utility Functions
# -----------------------------

def sanitize_title(title):
    return "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip().replace(" ", "_")

def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        logging.info(f"Created directory at path: {path}")
    except Exception as e:
        logging.error(f'Failed to create directory {path}: {e}')

def capture_screenshot(name, subfolder='general'):
    try:
        timestamp = int(time.time())
        screenshots_dir = os.path.join('screenshots', subfolder)
        create_directory(screenshots_dir)
        sanitized_name = sanitize_title(name)
        screenshot_path = os.path.join(screenshots_dir, f'screenshot_{sanitized_name}_{timestamp}.png')
        driver.save_screenshot(screenshot_path)
        logging.info(f'Screenshot saved to {screenshot_path}')
    except Exception as e:
        logging.error(f'Failed to capture screenshot "{name}": {e}')

# -----------------------------
# Function Definitions
# -----------------------------

def activate_easy_apply_filter():
    try:
        wait = WebDriverWait(driver, 20)
        filters_widget = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'dhi-filters-widget')))
        logging.info('Filters widget located.')
        easy_apply_accordion = WebDriverWait(filters_widget, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'dhi-accordion[data-cy="accordion-easyApply"]'))
        )
        logging.info('"Easy Apply" accordion located.')
        driver.execute_script("arguments[0].scrollIntoView(true);", easy_apply_accordion)
        time.sleep(1)

        easy_apply_filter_button = easy_apply_accordion.find_element(
            By.XPATH, './/js-single-select-filter[@data-cy="filter-easyApply"]//button[@aria-label="Filter Search Results by Easy Apply"]'
        )
        logging.info('"Easy Apply" filter button located.')
        aria_checked = easy_apply_filter_button.get_attribute('aria-checked')
        logging.info(f'"Easy Apply" aria-checked: {aria_checked}')

        if aria_checked != 'true':
            try:
                ActionChains(driver).move_to_element(easy_apply_filter_button).click().perform()
                logging.info('"Easy Apply" filter activated.')
                time.sleep(3)
            except (ElementClickInterceptedException, ElementNotInteractableException) as e:
                logging.warning(f'"Easy Apply" filter button not interactable: {e}. Attempting JavaScript click.')
                driver.execute_script("arguments[0].click();", easy_apply_filter_button)
                logging.info('"Easy Apply" filter activated using JavaScript.')

        if 'filters.easyApply=true' not in driver.current_url:
            driver.get(f'https://www.dice.com/jobs?q={SEARCH_TERMS}&filters.easyApply=true')
            wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
            ))
            logging.info('Navigated to filtered URL.')
        else:
            logging.info('URL contains the expected filter parameters.')

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error activating "Easy Apply" filter: {e}')
        capture_screenshot('error_activating_easy_apply_filter', subfolder='filters')
        driver.quit()
        exit(1)

def has_apply_now(driver):
    logging.info("Entering `has_apply_now` function")
    try:
        shadow_host = driver.find_element(By.CSS_SELECTOR, 'apply-button-wc')
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', shadow_host)
        apply_now_button = shadow_root.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')
        logging.info("Found the 'Easy Apply' button.")
        driver.execute_script("arguments[0].scrollIntoView(true);", apply_now_button)
        time.sleep(1)
        apply_now_button.click()
        logging.info("Clicked 'Easy Apply' button using click method.")
        return True
    except NoSuchElementException as e:
        logging.error(f"NoSuchElementException: {str(e)} - Element not found.")
        capture_screenshot('easy_apply_missing', subfolder='easy_apply_missing')
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        capture_screenshot('unexpected_error', subfolder='easy_apply_missing')
        return False

def apply_to_job(job_card, job_title, applied_jobs):
    if job_title in applied_jobs:
        logging.info(f'Skipping already applied job: {job_title}')
        return

    try:
        wait = WebDriverWait(driver, 30)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
        time.sleep(1)
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
        wait.until(EC.element_to_be_clickable((By.XPATH, './/a[@data-cy="card-title-link"]')))
        title_element.click()
        logging.info(f'Clicked on job title: {job_title}')

        original_window = driver.current_window_handle
        windows_after_click = driver.window_handles
        if len(windows_after_click) > 1:
            new_window = [window for window in windows_after_click if window != original_window][0]
            driver.switch_to.window(new_window)
            logging.info(f'Switched to new window for job: {job_title}')

        wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        time.sleep(2)

        if not has_apply_now(driver):
            logging.info(f'"Easy Apply" button not found for job: {job_title}. Skipping application.')
            capture_screenshot(f'easy_apply_not_found_{sanitize_title(job_title)}', subfolder='easy_apply_missing')
            return

        logging.info(f'Waiting for user login before proceeding with application for job: {job_title}')
        wait.until(EC.url_contains("dice.com/apply"))

        logging.info(f'Successfully applied to {job_title}')
        applied_jobs.add(job_title)

        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)
            logging.info(f'Closed new window and switched back to original window after processing {job_title}')
        else:
            driver.back()
            logging.info(f'Navigated back to job listings after processing {job_title}')

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error applying to "{job_title}": {e}')
        capture_screenshot(f'error_applying_{sanitize_title(job_title)}', subfolder='easy_apply_errors')
    except Exception as e:
        logging.error(f'Failed to apply to "{job_title}": {e}')
        capture_screenshot(f'error_applying_{sanitize_title(job_title)}', subfolder='easy_apply_errors')
    finally:
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)

def main():
    applied_jobs = set()

    try:
        logging.info('Navigating to Dice homepage.')
        driver.get('https://www.dice.com/')
        wait = WebDriverWait(driver, 20)
        search_field = wait.until(EC.presence_of_element_located((By.ID, 'typeaheadInput')))
        search_field.clear()
        search_field.send_keys(SEARCH_TERMS)
        logging.info(f'Entered search terms: {SEARCH_TERMS}')

        search_button = driver.find_element(By.ID, 'submitSearch-button')
        search_button.click()
        logging.info('Clicked search button.')

        activate_easy_apply_filter()
        time.sleep(3)

        job_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
        logging.info(f'Found {len(job_cards)} job postings.')

        for index, job_card in enumerate(job_cards, start=1):
            try:
                logging.info(f'Processing job {index}.')
                title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
                job_title = title_element.text.strip()
                logging.info(f'Job {index}: Found title: {job_title}')
            except NoSuchElementException:
                logging.warning(f'Job {index}: Title element not found.')
                capture_screenshot(f'job_{index}_no_title', subfolder='job_card_errors')
                continue

            if 'angular' in job_title.lower() and ('lead' in job_title.lower() or 'senior' in job_title.lower() or 'frontend' in job_title.lower()):
                logging.info(f'Job {index}: Applying to job: {job_title}')
                apply_to_job(job_card, job_title, applied_jobs)
                time.sleep(PAUSE_DURATION)
            else:
                logging.info(f'Job {index}: Skipping job: {job_title}')

        logging.info("Job application process completed.")
    except Exception as e:
        logging.error(f'An error occurred in main(): {e}')
        capture_screenshot('main_exception', subfolder='main_errors')
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
