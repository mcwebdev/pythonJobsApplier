import configparser
import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.action_chains import ActionChains
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

# Configure logging
logging.basicConfig(
    filename='application_log.txt',
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

# Initialize the WebDriver
try:
    driver = webdriver.Chrome(options=chrome_options)
    print("Initialized Chrome WebDriver.")
except WebDriverException as e:
    logging.error(f'Error initializing Chrome WebDriver: {e}')
    print(f'Error initializing Chrome WebDriver: {e}')
    exit(1)

# Maximize browser window
driver.maximize_window()
print("Maximized browser window.")

# -----------------------------
# Utility Functions
# -----------------------------

def sanitize_title(title):
    """
    Sanitizes the job title to create a safe filename.
    """
    return "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip().replace(" ", "_")

def create_directory(path):
    """
    Creates a directory if it doesn't exist.
    """
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Created directory at path: {path}")
    except Exception as e:
        logging.error(f'Failed to create directory {path}: {e}')
        print(f'Failed to create directory {path}: {e}')

def capture_screenshot(name, subfolder='general'):
    """
    Captures a screenshot with the given name and saves it in the specified subfolder.
    """
    try:
        timestamp = int(time.time())
        screenshots_dir = os.path.join('screenshots', subfolder)
        create_directory(screenshots_dir)
        sanitized_name = sanitize_title(name)
        screenshot_path = os.path.join(screenshots_dir, f'screenshot_{sanitized_name}_{timestamp}.png')
        driver.save_screenshot(screenshot_path)
        logging.debug(f'Screenshot saved to {screenshot_path}')
        print(f'Screenshot saved to {screenshot_path}')
    except Exception as e:
        logging.error(f'Failed to capture screenshot "{name}": {e}')
        print(f'Failed to capture screenshot "{name}": {e}')

# -----------------------------
# Function Definitions
# -----------------------------

def wait_for_manual_login():
    """
    Waits for the user to manually log in before proceeding.
    """
    try:
        wait = WebDriverWait(driver, 300)  # Wait up to 5 minutes for manual login
        print("Please log in manually, waiting for you to complete login...")
        logging.info("Waiting for manual login.")

        # Assuming the presence of the job listings after login is complete
        wait.until(EC.presence_of_element_located((By.ID, 'searchResultsLocation')))
        print("Login completed, proceeding with the script.")
        logging.info("Login completed.")
    except TimeoutException:
        logging.error('Manual login not completed within timeout period.')
        print('Login not completed within timeout period.')
        driver.quit()
        exit(1)

def activate_easy_apply_filter():
    """
    Activates the "Easy Apply" filter to focus on jobs that offer this option.
    Ensures that the filter button is clickable and not obscured by overlays.
    """
    try:
        wait = WebDriverWait(driver, 20)  # Increased timeout for dynamic content

        # Wait for the filters widget to load
        filters_widget = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'dhi-filters-widget')))
        logging.info('Filters widget located.')

        # Locate the "Easy Apply" accordion within the filters widget using CSS Selector
        easy_apply_accordion = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'dhi-accordion[data-cy="accordion-easyApply"]'))
        )
        logging.info('"Easy Apply" accordion located.')

        # Scroll the "Easy Apply" accordion into view
        driver.execute_script("arguments[0].scrollIntoView(true);", easy_apply_accordion)
        time.sleep(1)  # Wait for scrolling animation

        # Locate the filter button within the "Easy Apply" accordion using a more precise selector
        easy_apply_filter_button = easy_apply_accordion.find_element(
            By.XPATH, './/js-single-select-filter[@data-cy="filter-easyApply"]//button[@aria-label="Filter Search Results by Easy Apply"]'
        )
        logging.info('"Easy Apply" filter button located.')

        # Wait until the "Easy Apply" filter button is clickable
        wait.until(EC.element_to_be_clickable(easy_apply_filter_button))

        # Check if the "Easy Apply" filter is already active
        aria_checked = easy_apply_filter_button.get_attribute('aria-checked')
        logging.debug(f'"Easy Apply" aria-checked: {aria_checked}')

        if aria_checked == 'true':
            logging.info('"Easy Apply" filter is already active.')
        else:
            # Click using ActionChains to ensure the element is in view
            ActionChains(driver).move_to_element(easy_apply_filter_button).click().perform()
            logging.info('"Easy Apply" filter activated.')
            time.sleep(3)  # Wait for the page to refresh after applying the filter

        # Verify that the URL contains the required parameters
        current_url = driver.current_url
        expected_params = 'filters.easyApply=true'
        if expected_params not in current_url:
            logging.warning(f'URL does not contain expected parameters: {expected_params}')
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
    except Exception as e:
        logging.error(f'Unexpected error activating "Easy Apply" filter: {e}')
        capture_screenshot('unexpected_error_easy_apply_filter', subfolder='filters')
        driver.quit()
        exit(1)

def apply_to_job(job_card, job_title, applied_jobs):
    """
    Attempts to apply to a job using the "Easy Apply" option.
    """
    try:
        if job_title in applied_jobs:
            logging.info(f'Skipping already applied job: {job_title}')
            return  # Skip if we've already applied to this job

        wait = WebDriverWait(driver, 30)  # Increased timeout to handle new tab loading

        # Scroll the job card into view
        logging.info(f'Scrolling into view for job: {job_title}')
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
        time.sleep(1)  # Wait for scrolling animation

        # Click on the job title to open job details
        logging.info(f'Locating job title link for: {job_title}')
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
        wait.until(EC.element_to_be_clickable(title_element))
        title_element.click()
        logging.info(f'Clicked on job title: {job_title}')

        # Handle the new window or tab
        original_window = driver.current_window_handle
        windows_after_click = driver.window_handles
        if len(windows_after_click) > 1:
            new_window = [window for window in windows_after_click if window != original_window][0]
            driver.switch_to.window(new_window)
            logging.info(f'Switched to new window for job: {job_title}')

        # Wait for the job details page to load
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        time.sleep(2)  # Additional wait to ensure all elements are loaded

        # Call `has_apply_now` to check for the "Easy Apply" button within the Shadow DOM
        if not has_apply_now(driver):
            logging.info(f'"Easy Apply" button not found for job: {job_title}. Skipping application.')
            capture_screenshot(f'easy_apply_not_found_{sanitize_title(job_title)}', subfolder='easy_apply_missing')
            return  # Exit if the button is not found

        # Click the "Apply Now" button
        logging.info(f'Clicking "Apply Now" button for job: {job_title}')
        apply_now_button = driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')
        apply_now_button.click()

        # Wait for the URL to change to the application form URL
        logging.info(f'Waiting for URL change to application form for job: {job_title}')
        wait.until(EC.url_contains("dice.com/apply"))

        # Now, wait for the "Next" button to appear and click it
        logging.info(f'Waiting for "Next" button to be clickable on the application form page.')
        click_next_button()

        logging.info(f'Successfully applied to {job_title}')
        applied_jobs.add(job_title)

        # Close the new window or navigate back
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
            logging.info(f'Closed new window and switched back to original window after processing {job_title}')

def click_next_button():
    """
    Waits for the 'Next' button to appear after the apply modal is displayed and clicks it.
    """
    try:
        wait = WebDriverWait(driver, 30)  # Increased timeout for dynamic content

        logging.info('Waiting for "Next" button to be clickable.')
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Next")]')))
        
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(1)  # Give time for scrolling animation

        try:
            next_button.click()  # Attempt to click the button normally
            logging.info('"Next" button clicked.')
        except Exception as e:
            logging.warning(f'Normal click failed: {e}, trying JavaScript click.')
            driver.execute_script("arguments[0].click();", next_button)
            logging.info('"Next" button clicked using JavaScript.')

    except TimeoutException:
        logging.error('Timeout: "Next" button did not become clickable.')
        capture_screenshot('next_button_not_clickable', subfolder='application_errors')
    except Exception as e:
        logging.error(f'An unexpected error occurred when clicking "Next" button: {e}')
        capture_screenshot('unexpected_error_clicking_next_button', subfolder='application_errors')

# Main Function
def main():
    applied_jobs = set()  # Track jobs that have been applied to

    try:
        logging.info('Navigating to Dice homepage.')
        driver.get('https://www.dice.com/')
        wait_for_manual_login()  # Wait for the user to log in manually

        # Activate the "Easy Apply" filter
        activate_easy_apply_filter()

        # Wait for job listings to load
        time.sleep(3)  # Add a small delay to ensure the page is loaded after applying the filter

        # Get the list of job postings
        logging.info('Locating job cards.')
        job_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
        logging.info(f'Found {len(job_cards)} job postings.')

        for index, job_card in enumerate(job_cards, start=1):
            try:
                # Extract the job title using data-cy attribute
                logging.info(f'Processing job {index}.')
                title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
                job_title = title_element.text.strip()
                logging.info(f'Job {index}: Found title: {job_title}')

            except NoSuchElementException:
                logging.warning(f'Job {index}: Title element not found.')
                job_card_html = job_card.get_attribute('outerHTML')
                logging.debug(f'Job {index} HTML: {job_card_html}')
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
