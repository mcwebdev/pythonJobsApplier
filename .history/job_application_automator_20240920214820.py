import configparser
import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
    TimeoutException,
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
EMAIL = config['DEFAULT']['Email']
PASSWORD = config['DEFAULT']['Password']

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
# Uncomment the following line to run the browser in headless mode
# chrome_options.add_argument('--headless')

# Optional: Ignore SSL certificate errors (Use with caution)
# chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--ignore-ssl-errors')

# Initialize the WebDriver
try:
    driver = webdriver.Chrome(options=chrome_options)
except WebDriverException as e:
    logging.error(f'Error initializing Chrome WebDriver: {e}')
    print(f'Error initializing Chrome WebDriver: {e}')
    exit(1)

# Maximize browser window
driver.maximize_window()

# -----------------------------
# Function Definitions
# -----------------------------

def login_to_dice():
    """
    Logs into Dice.com using the provided email and password.
    """
    try:
        driver.get('https://www.dice.com/dashboard/login')
        wait = WebDriverWait(driver, 15)  # Increased timeout

        # Wait for the email field to be present
        email_field = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
        email_field.clear()
        email_field.send_keys(EMAIL)

        # Locate and click the "Continue" button
        continue_button = driver.find_element(By.XPATH, '//button[contains(@data-testid, "sign-in-button")]')
        continue_button.click()

        # Wait for the password field to be present
        password_field = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        password_field.clear()
        password_field.send_keys(PASSWORD)

        # Locate and click the "Sign In" button
        sign_in_button = driver.find_element(By.XPATH, '//button[contains(@data-testid, "submit-password")]')
        sign_in_button.click()

        # Wait until dashboard loads by checking URL or a specific element
        wait.until(EC.url_contains('/dashboard'))

        logging.info('Successfully logged into Dice.')
        print("Successfully logged into Dice.")
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error during login: {e}')
        print(f"Error during login: {e}")
        driver.quit()
        exit(1)

def activate_easy_apply_filter():
    """
    Activates the "Easy Apply" filter to focus on jobs that offer this option.
    """
    try:
        wait = WebDriverWait(driver, 15)  # Increased timeout

        # Wait for the filters widget to load
        filters_widget = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'dhi-filters-widget')))

        # Locate the "Easy Apply" accordion within the filters widget
        easy_apply_accordion = filters_widget.find_element(By.XPATH, './/dhi-accordion[@data-cy="accordion-easyApply"]')

        # Within the "Easy Apply" accordion, locate the filter button
        easy_apply_filter_button = easy_apply_accordion.find_element(
            By.XPATH, './/button[@aria-label="Filter Search Results by Easy Apply"]'
        )

        # Check if the "Easy Apply" filter is already active
        aria_checked = easy_apply_filter_button.get_attribute('aria-checked')
        if aria_checked and aria_checked.lower() != 'true':
            easy_apply_filter_button.click()
            logging.info('"Easy Apply" filter activated.')
            print('"Easy Apply" filter activated.')
            # Wait for the page to refresh after applying the filter
            time.sleep(3)  # Adjust as needed based on network speed
        else:
            logging.info('"Easy Apply" filter is already active.')
            print('"Easy Apply" filter is already active.')

    except NoSuchElementException as e:
        logging.error(f'Error locating "Easy Apply" filter: {e}')
        print(f'Error locating "Easy Apply" filter: {e}')
        driver.quit()
        exit(1)
    except TimeoutException as e:
        logging.error(f'Timeout while activating "Easy Apply" filter: {e}')
        print(f'Timeout while activating "Easy Apply" filter: {e}')
        driver.quit()
        exit(1)

def has_apply_now(job_card):
    """
    Checks if a job card contains an "Apply now" button.
    Returns True if present, False otherwise.
    """
    try:
        apply_now_button = job_card.find_element(By.XPATH, './/button[contains(text(), "Apply now")]')
        return True
    except NoSuchElementException:
        return False

def log_available_buttons(job_card, job_title):
    """
    Logs all available buttons within a job card for debugging purposes.
    """
    buttons = job_card.find_elements(By.TAG_NAME, 'button')
    button_texts = [button.text for button in buttons]
    logging.debug(f'Available buttons for job "{job_title}": {button_texts}')
    print(f'Available buttons for job "{job_title}": {button_texts}')

    # Capture a screenshot for visual debugging
    sanitized_title = "".join([c for c in job_title if c.isalnum() or c in (' ', '_')]).rstrip()
    screenshot_path = f'screenshot_job_{sanitized_title.replace(" ", "_")}.png'
    driver.save_screenshot(screenshot_path)
    logging.debug(f'Screenshot saved to {screenshot_path}')
    print(f'Screenshot saved to {screenshot_path}')

def apply_to_job(job_card, job_title):
    """
    Attempts to apply to a job using the "Easy Apply" option.
    Skips if "Apply now" is present or "Easy Apply" is unavailable.
    """
    try:
        wait = WebDriverWait(driver, 15)  # Increased timeout

        # Click on the job title to open job details
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
        title_element.click()
        logging.info(f'Clicked on job title: {job_title}')
        print(f'Clicked on job title: {job_title}')

        # Wait for the job details panel to load
        job_details = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        logging.debug(f'Job details loaded for: {job_title}')
        print(f'Job details loaded for: {job_title}')

        # Check if 'Apply now' button is present; if so, skip
        if has_apply_now(job_card):
            logging.info(f'"Apply now" button present for job: {job_title}. Skipping application.')
            print(f'"Apply now" button present for job: {job_title}. Skipping application.')
            return

        # Attempt to locate the 'Easy Apply' button using the revised selector
        try:
            easy_apply_div = job_details.find_element(By.XPATH, './/div[@data-cy="card-easy-apply"]')
            # Assuming clicking the div initiates the application
            easy_apply_div.click()
            logging.info(f'Clicked "Easy Apply" for job: {job_title}')
            print(f'Clicked "Easy Apply" for job: {job_title}')

            # Wait for the modal to appear (adjust the XPath based on actual modal structure)
            modal = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "apply-modal")]')))
            logging.debug(f'Modal appeared for job: {job_title}')
            print(f'Modal appeared for job: {job_title}')

            # Wait for the resume upload field to be present within the modal
            upload_field = wait.until(EC.presence_of_element_located((By.XPATH, './/input[@type="file"]')))
            upload_field.send_keys(RESUME_PATH)
            logging.info(f'Uploaded resume for job: {job_title}')
            print(f'Uploaded resume for job: {job_title}')

            # Wait for the 'Submit' button to be clickable and click it
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, './/button[contains(text(), "Submit")]')))
            submit_button.click()
            logging.info(f'Successfully applied to {job_title}')
            print(f"Successfully applied to {job_title}")

            # Optional: Wait for a confirmation message or element
            # confirmation = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Application submitted")]')))
            # logging.info(f'Application confirmed for job: {job_title}')

        except NoSuchElementException:
            # 'Easy Apply' button not found; likely already applied or not available
            logging.info(f'"Easy Apply" not available for job: {job_title}. It may have already been applied to.')
            print(f'"Easy Apply" not available for job: {job_title}. Skipping application.')

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error applying to "{job_title}": {e}')
        print(f'Error applying to "{job_title}": {e}')

        # Log available buttons and capture a screenshot
        log_available_buttons(job_card, job_title)

    except Exception as e:
        logging.error(f'Failed to apply to "{job_title}": {e}')
        print(f'Failed to apply to "{job_title}": {e}')

        # Capture a screenshot for visual debugging
        sanitized_title = "".join([c for c in job_title if c.isalnum() or c in (' ', '_')]).rstrip()
        screenshot_path = f'screenshot_job_{sanitized_title.replace(" ", "_")}_error.png'
        driver.save_screenshot(screenshot_path)
        logging.debug(f'Screenshot saved to {screenshot_path}')
        print(f'Screenshot saved to {screenshot_path}')

# -----------------------------
# Main Execution Function
# -----------------------------

def main():
    login_to_dice()

    try:
        # Enter search criteria
        driver.get('https://www.dice.com/')
        wait = WebDriverWait(driver, 15)  # Increased timeout
        search_field = wait.until(EC.presence_of_element_located((By.ID, 'typeaheadInput')))
        search_field.clear()
        search_field.send_keys(SEARCH_TERMS)
        search_button = driver.find_element(By.ID, 'submitSearch-button')
        search_button.click()

        # Activate the "Easy Apply" filter
        activate_easy_apply_filter()

        # Wait until job listings are loaded
        wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
        ))

        # Get the list of job postings
        job_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
        logging.info(f'Found {len(job_cards)} job postings.')
        print(f'Found {len(job_cards)} job postings.')

        for index, job_card in enumerate(job_cards, start=1):
            try:
                # Extract the job title using data-cy attribute
                title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
                job_title = title_element.text.strip()
            except NoSuchElementException:
                logging.warning(f'Job {index}: Title element not found.')
                print(f'Job {index}: Title element not found.')

                # Debugging: Print the outer HTML of the job card
                job_card_html = job_card.get_attribute('outerHTML')
                logging.debug(f'Job {index} HTML: {job_card_html}')
                print(f'Job {index} HTML: {job_card_html}')
                continue

            # Debugging: Log job titles
            logging.debug(f'Job {index}: Title="{job_title}"')
            print(f'Job {index}: Title="{job_title}"')

            # Define the criteria for applying
            criteria = ['Angular', 'Senior Frontend Developer']
            if all(keyword in job_title for keyword in criteria):
                print(f"Applying to job: {job_title}")
                logging.info(f"Applying to job: {job_title}")
                apply_to_job(job_card, job_title)

                # Pause for specified duration before the next application
                print(f"Waiting for {PAUSE_DURATION} seconds before the next application...")
                time.sleep(PAUSE_DURATION)
            else:
                print(f"Skipping job: {job_title}")
                logging.info(f"Skipping job: {job_title}")

        print("Job application process completed.")
        logging.info("Job application process completed.")
    except Exception as e:
        logging.error(f'An error occurred in main(): {e}')
        print(f"An error occurred in main(): {e}")
    finally:
        driver.quit()

# -----------------------------
# Entry Point
# -----------------------------

if __name__ == '__main__':
    main()
