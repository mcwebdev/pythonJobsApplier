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
    ElementClickInterceptedException,
    ElementNotInteractableException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

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
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

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
        logging.info('Navigating to Dice login page.')
        driver.get('https://www.dice.com/dashboard/login')
        wait = WebDriverWait(driver, 20)  # Increased timeout for dynamic content

        # Wait for the email field to be present
        logging.info('Waiting for email field.')
        email_field = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
        email_field.clear()
        email_field.send_keys(EMAIL)
        logging.info('Entered email.')
        print('Entered email.')

        # Locate and click the "Continue" button
        logging.info('Locating "Continue" button.')
        continue_button = driver.find_element(By.XPATH, '//button[contains(@data-testid, "sign-in-button")]')
        continue_button.click()
        logging.info('Clicked "Continue" button.')
        print('Clicked "Continue" button.')

        # Wait for the password field to be present
        logging.info('Waiting for password field.')
        password_field = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        password_field.clear()
        password_field.send_keys(PASSWORD)
        logging.info('Entered password.')
        print('Entered password.')

        # Locate and click the "Sign In" button
        logging.info('Locating "Sign In" button.')
        sign_in_button = driver.find_element(By.XPATH, '//button[contains(@data-testid, "submit-password")]')
        sign_in_button.click()
        logging.info('Clicked "Sign In" button.')
        print('Clicked "Sign In" button.')

        # Wait until dashboard loads by checking URL or a specific element
        logging.info('Waiting for dashboard to load.')
        wait.until(EC.url_contains('/dashboard'))
        logging.info('Successfully logged into Dice.')
        print("Successfully logged into Dice.")

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error during login: {e}')
        print(f"Error during login: {e}")
        capture_screenshot('login_error')
        driver.quit()
        exit(1)

    except WebDriverException as e:
        logging.error(f'Redirected to an unexpected URL or logged out: {e}')
        print(f"Unexpected redirection or logout: {e}")
        capture_screenshot('login_redirection_error')
        driver.quit()
        exit(1)

def capture_screenshot(name):
    """
    Captures a screenshot with the given name.
    """
    try:
        timestamp = int(time.time())
        screenshot_path = f'screenshot_{name}_{timestamp}.png'
        driver.save_screenshot(screenshot_path)
        logging.debug(f'Screenshot saved to {screenshot_path}')
        print(f'Screenshot saved to {screenshot_path}')
    except Exception as e:
        logging.error(f'Failed to capture screenshot "{name}": {e}')
        print(f'Failed to capture screenshot "{name}": {e}')

def activate_easy_apply_filter():
    """
    Activates the "Easy Apply" filter to focus on jobs that offer this option.
    Ensures that the filter button is clickable and not obscured by overlays.
    """
    try:
        wait = WebDriverWait(driver, 20)  # Increased timeout for dynamic content

        # Wait for the filters widget to load
        logging.info('Waiting for filters widget.')
        filters_widget = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'dhi-filters-widget')))
        logging.info('Filters widget located.')
        print('Filters widget located.')

        # For debugging: log the inner HTML of the filters_widget
        filters_html = filters_widget.get_attribute('innerHTML')
        logging.debug(f'Filters widget inner HTML: {filters_html}')
        print('Logged filters widget inner HTML for debugging.')

        # Locate the "Easy Apply" accordion within the filters widget using CSS Selector
        try:
            logging.info('Locating "Easy Apply" accordion.')
            easy_apply_accordion = WebDriverWait(filters_widget, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'dhi-accordion[data-cy="accordion-easyApply"]'))
            )
            logging.info('"Easy Apply" accordion located.')
            print('"Easy Apply" accordion located.')
        except TimeoutException:
            logging.error('"Easy Apply" accordion not found within filters widget.')
            print('"Easy Apply" accordion not found within filters widget.')
            capture_screenshot('missing_easy_apply_accordion')
            driver.quit()
            exit(1)

        # Scroll the "Easy Apply" accordion into view
        driver.execute_script("arguments[0].scrollIntoView(true);", easy_apply_accordion)
        time.sleep(1)  # Wait for scrolling animation

        # Locate the filter button within the "Easy Apply" accordion using a more precise selector
        try:
            logging.info('Locating "Easy Apply" filter button.')
            easy_apply_filter_button = easy_apply_accordion.find_element(
                By.XPATH, './/js-single-select-filter[@data-cy="filter-easyApply"]//button[@aria-label="Filter Search Results by Easy Apply"]'
            )
            logging.info('"Easy Apply" filter button located.')
            print('"Easy Apply" filter button located.')
        except NoSuchElementException:
            logging.error('"Easy Apply" filter button not found within accordion.')
            print('"Easy Apply" filter button not found within accordion.')
            capture_screenshot('missing_easy_apply_filter_button')
            driver.quit()
            exit(1)

        # Wait until the "Easy Apply" filter button is clickable
        try:
            logging.info('Waiting for "Easy Apply" filter button to be clickable.')
            easy_apply_filter_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, './/js-single-select-filter[@data-cy="filter-easyApply"]//button[@aria-label="Filter Search Results by Easy Apply"]'))
            )
        except TimeoutException:
            logging.error('"Easy Apply" filter button is not clickable.')
            print('"Easy Apply" filter button is not clickable.')
            capture_screenshot('easy_apply_not_clickable')
            driver.quit()
            exit(1)

        # Check if the "Easy Apply" filter is already active
        aria_checked = easy_apply_filter_button.get_attribute('aria-checked')
        logging.debug(f'"Easy Apply" aria-checked: {aria_checked}')
        print(f'"Easy Apply" aria-checked: {aria_checked}')

        if aria_checked == 'true':
            logging.info('"Easy Apply" filter is already active.')
            print('"Easy Apply" filter is already active.')
        else:
            # Click using ActionChains to ensure the element is in view
            try:
                logging.info('Attempting to click "Easy Apply" filter button.')
                ActionChains(driver).move_to_element(easy_apply_filter_button).click().perform()
            except (ElementClickInterceptedException, ElementNotInteractableException) as e:
                logging.warning(f'"Easy Apply" filter button not interactable: {e}. Attempting JavaScript click.')
                driver.execute_script("arguments[0].click();", easy_apply_filter_button)

            logging.info('"Easy Apply" filter activated.')
            print('"Easy Apply" filter activated.')
            # Wait for the page to refresh after applying the filter
            time.sleep(3)  # Adjust as needed based on network speed

        # Verify that the URL contains the required parameters
        current_url = driver.current_url
        expected_params = 'filters.easyApply=true'
        if expected_params not in current_url:
            logging.warning(f'URL does not contain expected parameters: {expected_params}')
            print(f'URL does not contain expected parameters: {expected_params}')
            # Optionally, navigate to the correct URL directly
            driver.get(f'https://www.dice.com/jobs?q={SEARCH_TERMS}&filters.easyApply=true')
            # Wait for job listings to load
            wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
            ))
            logging.info('Navigated to filtered URL.')
            print('Navigated to filtered URL.')
        else:
            logging.info('URL contains the expected filter parameters.')
            print('URL contains the expected filter parameters.')

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error activating "Easy Apply" filter: {e}')
        print(f'Error activating "Easy Apply" filter: {e}')
        capture_screenshot('error_activating_easy_apply_filter')
        driver.quit()
        exit(1)
    except Exception as e:
        logging.error(f'Unexpected error activating "Easy Apply" filter: {e}')
        print(f"Unexpected error activating 'Easy Apply' filter: {e}")
        capture_screenshot('unexpected_error_easy_apply_filter')
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
    try:
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
    except Exception as e:
        logging.error(f'Error logging available buttons for "{job_title}": {e}')
        print(f'Error logging available buttons for "{job_title}": {e}')

def apply_to_job(job_card, job_title, applied_jobs):
    """
    Attempts to apply to a job using the "Easy Apply" option.
    """
    try:
        if job_title in applied_jobs:
            logging.info(f'Skipping already applied job: {job_title}')
            return  # Skip if we've already applied to this job

        wait = WebDriverWait(driver, 20)  # Increased timeout

        # Scroll the job card into view
        logging.info(f'Scrolling into view for job: {job_title}')
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
        time.sleep(1)  # Wait for scrolling animation

        # Click on the job title to open job details
        logging.info(f'Locating job title link for: {job_title}')
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')

        # Wait until the title_element is clickable
        logging.info(f'Waiting for job title to be clickable for: {job_title}')
        wait.until(EC.element_to_be_clickable((By.XPATH, './/a[@data-cy="card-title-link"]')))

        try:
            logging.info(f'Attempting to click on job title: {job_title}')
            title_element.click()
            logging.info(f'Clicked on job title: {job_title}')
            print(f'Clicked on job title: {job_title}')
        except (ElementClickInterceptedException, ElementNotInteractableException) as e:
            logging.warning(f'Click intercepted or element not interactable for job title: {job_title}. Trying JavaScript click.')
            driver.execute_script("arguments[0].click();", title_element)

        # Check if a new window has been opened
        original_window = driver.current_window_handle
        windows_after_click = driver.window_handles
        if len(windows_after_click) > 1:
            new_window = [window for window in windows_after_click if window != original_window][0]
            driver.switch_to.window(new_window)
            logging.info(f'Switched to new window for job: {job_title}')
            print(f'Switched to new window for job: {job_title}')
        else:
            # Job details opened in the same window
            logging.info(f'Job details opened in the same window for job: {job_title}')
            print(f'Job details opened in the same window for job: {job_title}')

        # Wait for the job details panel to load
        logging.info(f'Waiting for job details to load for: {job_title}')
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        time.sleep(2)  # Additional wait to ensure all elements are loaded
        logging.debug(f'Job details loaded for: {job_title}')
        print(f'Job details loaded for: {job_title}')

        # Attempt to locate the 'Easy Apply' button
        try:
            logging.info(f'Locating "Easy Apply" button for job: {job_title}')
            # Update the selector based on the actual button
            easy_apply_button = driver.find_element(By.XPATH, '//button[contains(text(), "Easy Apply")]')
            if easy_apply_button.is_displayed():
                # Scroll the button into view
                driver.execute_script("arguments[0].scrollIntoView(true);", easy_apply_button)
                time.sleep(0.5)
                try:
                    easy_apply_button.click()
                    logging.info(f'Clicked "Easy Apply" for job: {job_title}')
                    print(f'Clicked "Easy Apply" for job: {job_title}')
                except (ElementClickInterceptedException, ElementNotInteractableException) as e:
                    logging.warning(f'Click intercepted on "Easy Apply" button for job: {job_title}. Trying JavaScript click.')
                    driver.execute_script("arguments[0].click();", easy_apply_button)
            else:
                logging.info(f'"Easy Apply" button is not visible for job: {job_title}')
                print(f'"Easy Apply" button is not visible for job: {job_title}')
                return  # Exit if the button is not visible
        except NoSuchElementException:
            logging.info(f'"Easy Apply" button not found for job: {job_title}. Skipping application.')
            print(f'"Easy Apply" button not found for job: {job_title}. Skipping application.')
            return  # Exit if the button is not found

        # Wait for the apply modal to appear
        logging.info(f'Waiting for apply modal for job: {job_title}')
        modal = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "apply-modal")]')))
        logging.debug(f'Apply modal appeared for job: {job_title}')
        print(f'Apply modal appeared for job: {job_title}')

        # Wait for the resume upload field to be present within the modal
        logging.info(f'Locating resume upload field for job: {job_title}')
        upload_field = wait.until(EC.presence_of_element_located((By.XPATH, './/input[@type="file"]')))
        upload_field.send_keys(RESUME_PATH)
        logging.info(f'Uploaded resume for job: {job_title}')
        print(f'Uploaded resume for job: {job_title}')

        # Wait for the 'Submit' button to be clickable and click it
        logging.info(f'Locating "Submit" button for job: {job_title}')
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, './/button[contains(text(), "Submit")]')))
        submit_button.click()
        logging.info(f'Successfully applied to {job_title}')
        print(f"Successfully applied to {job_title}")

        # Add the job to the set of applied jobs
        applied_jobs.add(job_title)

        # Close the new window or navigate back
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)
            logging.info(f'Closed new window and switched back to original window after processing {job_title}')
            print(f'Closed new window and switched back to original window after processing {job_title}')
        else:
            # Navigate back to the job listings page
            driver.back()
            logging.info(f'Navigated back to job listings after processing {job_title}')
            print(f'Navigated back to job listings after processing {job_title}')

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error applying to "{job_title}": {e}')
        print(f'Error applying to "{job_title}": {e}')

        # Log available buttons and capture a screenshot
        log_available_buttons(job_card, job_title)

    except Exception as e:
        logging.error(f'Failed to apply to "{job_title}": {e}')
        print(f'Failed to apply to "{job_title}": {e}')
        capture_screenshot(f'error_applying_{job_title}')

    finally:
        # Ensure that any new window is closed and focus is back to the original window
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)
            logging.info(f'Closed new window and switched back to original window after processing {job_title}')
            print(f'Closed new window and switched back to original window after processing {job_title}')

def main():
    applied_jobs = set()  # Track jobs that have been applied to

    login_to_dice()

    try:
        logging.info('Navigating to Dice homepage.')
        # Enter search criteria
        driver.get('https://www.dice.com/')
        wait = WebDriverWait(driver, 20)  # Increased timeout
        logging.info('Waiting for search field.')
        search_field = wait.until(EC.presence_of_element_located((By.ID, 'typeaheadInput')))
        search_field.clear()
        search_field.send_keys(SEARCH_TERMS)
        logging.info(f'Entered search terms: {SEARCH_TERMS}')
        print(f'Entered search terms: {SEARCH_TERMS}')

        logging.info('Locating search button.')
        search_button = driver.find_element(By.ID, 'submitSearch-button')
        search_button.click()
        logging.info('Clicked search button.')
        print('Clicked search button.')

        # Activate the "Easy Apply" filter
        activate_easy_apply_filter()

        # Wait for job listings to load
        time.sleep(3)  # Add a small delay to ensure the page is loaded after applying the filter

        # Get the list of job postings
        logging.info('Locating job cards.')
        job_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
        logging.info(f'Found {len(job_cards)} job postings.')
        print(f'Found {len(job_cards)} job postings.')

        for index, job_card in enumerate(job_cards, start=1):
            try:
                # Extract the job title using data-cy attribute
                logging.info(f'Processing job {index}.')
                title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
                job_title = title_element.text.strip()
                logging.info(f'Job {index}: Found title: {job_title}')
                print(f'Job {index}: Found title: {job_title}')

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

            # Simplified criteria for applying
            if 'angular' in job_title.lower() and ('lead' in job_title.lower() or 'senior' in job_title.lower() or 'frontend' in job_title.lower()):
                logging.info(f'Job {index}: Applying to job: {job_title}')
                print(f'Applying to job: {job_title}')
                apply_to_job(job_card, job_title, applied_jobs)

                # Pause for specified duration before the next application
                print(f"Waiting for {PAUSE_DURATION} seconds before the next application...")
                time.sleep(PAUSE_DURATION)
            else:
                logging.info(f'Job {index}: Skipping job: {job_title}')
                print(f"Skipping job: {job_title}")

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
