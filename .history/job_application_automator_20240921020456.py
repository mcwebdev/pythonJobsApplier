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
        capture_screenshot('login_error', subfolder='login')
        driver.quit()
        exit(1)

    except WebDriverException as e:
        logging.error(f'Redirected to an unexpected URL or logged out: {e}')
        print(f"Unexpected redirection or logout: {e}")
        capture_screenshot('login_redirection_error', subfolder='login')
        driver.quit()
        exit(1)

def handle_login_modal():
    """
    Handles the login modal that appears after clicking "Apply now".
    """
    try:
        wait = WebDriverWait(driver, 20)
        logging.info("Checking if login modal is present.")
        print("Checking if login modal is present.")  # Debugging print

        # Wait for the modal dialog itself to appear
        modal_dialog = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'dialog')))
        logging.info("Modal dialog detected.")
        print("Modal dialog detected.")  # Debugging print

        # Since the email field is already focused, we can directly send keys to it
        logging.info("Login modal detected. Entering credentials.")
        print("Login modal detected.")  # Debugging print

        # Send the email address (assuming it is focused already)
        actions = ActionChains(driver)
        actions.send_keys(EMAIL)
        actions.perform()
        logging.info("Entered email in modal.")
        print("Entered email in modal.")  # Debugging print

        # Wait for the password field to be visible
        password_field = wait.until(EC.visibility_of_element_located((By.ID, 'password')))
        password_field.clear()
        password_field.send_keys(PASSWORD)
        logging.info("Entered password in modal.")
        print("Entered password in modal.")  # Debugging print

        # Wait for the "Log in" button to be clickable
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'login-dhi-button button')))
        login_button.click()
        logging.info("Clicked 'Log in' button in modal.")
        print("Clicked 'Log in' button in modal.")  # Debugging print

        # Wait for the modal to disappear (indicating a successful login)
        wait.until(EC.invisibility_of_element_located((By.TAG_NAME, 'dialog')))
        logging.info("Successfully logged in via modal.")
        print("Successfully logged in via modal.")  # Debugging print

    except TimeoutException:
        logging.error("Login modal did not appear as expected.")
        print("Login modal did not appear as expected.")  # Debugging print
        capture_screenshot('login_modal_missing', subfolder='login')
    except NoSuchElementException as e:
        logging.error(f"Error finding login modal elements: {e}")
        capture_screenshot('login_modal_element_not_found', subfolder='login')
    except Exception as e:
        logging.error(f"An unexpected error occurred while handling the login modal: {e}")
        capture_screenshot('login_modal_unexpected_error', subfolder='login')
        print(f"An unexpected error occurred while handling the login modal: {e}")  # Debugging print

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
            capture_screenshot('missing_easy_apply_accordion', subfolder='filters')
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
            capture_screenshot('missing_easy_apply_filter_button', subfolder='filters')
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
            capture_screenshot('easy_apply_not_clickable', subfolder='filters')
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
        capture_screenshot('error_activating_easy_apply_filter', subfolder='filters')
        driver.quit()
        exit(1)
    except Exception as e:
        logging.error(f'Unexpected error activating "Easy Apply" filter: {e}')
        print(f"Unexpected error activating 'Easy Apply' filter: {e}")
        capture_screenshot('unexpected_error_easy_apply_filter', subfolder='filters')
        driver.quit()
        exit(1)

def has_apply_now(driver):
    print("Entering `has_apply_now` function")  # Debugging print
    logging.info("Attempting to locate the shadow host element.")
    try:
        # Locate the shadow host element
        shadow_host = driver.find_element(By.CSS_SELECTOR, 'apply-button-wc')
        logging.info("Shadow host element found: %s", shadow_host)
        print("Shadow host element found")  # Debugging print

        logging.info("Accessing the shadow root.")
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', shadow_host)
        logging.info("Shadow root accessed: %s", shadow_root)
        print("Shadow root accessed")  # Debugging print

        logging.info("Attempting to locate the 'Easy Apply' button within the shadow root.")
        apply_now_button = shadow_root.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')
        logging.info("Found the 'Easy Apply' button: %s", apply_now_button)
        print("Easy Apply button found")  # Debugging print

        # Scroll the button into view before clicking
        driver.execute_script("arguments[0].scrollIntoView(true);", apply_now_button)
        time.sleep(1)  # Give time for scrolling animation

        # Try clicking the button using JavaScript
        try:
            apply_now_button.click()  # Attempt to click the button
            logging.info("Clicked 'Easy Apply' button using click method.")
            print("Clicked 'Easy Apply' button using click method.")  # Debugging print
        except Exception as e:
            logging.warning(f"Regular click failed: {e}, trying JavaScript click.")
            driver.execute_script("arguments[0].click();", apply_now_button)
            logging.info("Clicked 'Easy Apply' button using JavaScript.")
            print("Clicked 'Easy Apply' button using JavaScript.")  # Debugging print

        return True
    except NoSuchElementException as e:
        logging.error(f"NoSuchElementException: {str(e)} - Element not found.")
        driver.save_screenshot(f'screenshots/easy_apply_missing/screenshot_easy_apply_not_found.png')
        print("NoSuchElementException caught")  # Debugging print
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        driver.save_screenshot(f'screenshots/easy_apply_missing/unexpected_error.png')
        print("Unexpected exception caught")  # Debugging print
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
        sanitized_title = sanitize_title(job_title)
        screenshot_path = os.path.join('screenshots', 'missing_easy_apply', f'screenshot_job_{sanitized_title}.png')
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

        # **NEW CODE**: Call `has_apply_now` to check for the "Easy Apply" button within the Shadow DOM
        if not has_apply_now(driver):
            logging.info(f'"Easy Apply" button not found for job: {job_title}. Skipping application.')
            print(f'"Easy Apply" button not found for job: {job_title}. Skipping application.')
            capture_screenshot(f'easy_apply_not_found_{sanitize_title(job_title)}', subfolder='easy_apply_missing')
            return  # Exit if the button is not found

        # Call handle_login_modal right after the apply button is clicked
        handle_login_modal()

        # Continue with the application process...
        # Wait for the apply modal to appear
        logging.info(f'Waiting for apply modal for job: {job_title}')
        try:
            modal = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "apply-modal")]')))
            logging.debug(f'Apply modal appeared for job: {job_title}')
            print(f'Apply modal appeared for job: {job_title}')
        except TimeoutException:
            logging.error(f'Apply modal did not appear for job: {job_title}')
            print(f'Apply modal did not appear for job: {job_title}')
            capture_screenshot(f'apply_modal_missing_{sanitize_title(job_title)}', subfolder='easy_apply_missing')
            return

        # Wait for the resume upload field to be present within the modal
        logging.info(f'Locating resume upload field for job: {job_title}')
        try:
            upload_field = wait.until(EC.presence_of_element_located((By.XPATH, './/input[@type="file"]')))
            upload_field.send_keys(RESUME_PATH)
            logging.info(f'Uploaded resume for job: {job_title}')
            print(f'Uploaded resume for job: {job_title}')
        except TimeoutException:
            logging.error(f'Resume upload field not found for job: {job_title}')
            print(f'Resume upload field not found for job: {job_title}')
            capture_screenshot(f'resume_upload_missing_{sanitize_title(job_title)}', subfolder='easy_apply_missing')
            return

        # Wait for the 'Submit' button to be clickable and click it
        logging.info(f'Locating "Submit" button for job: {job_title}')
        try:
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, './/button[contains(text(), "Submit")]')))
            submit_button.click()
            logging.info(f'Successfully applied to {job_title}')
            print(f"Successfully applied to {job_title}")
        except TimeoutException:
            logging.error(f'"Submit" button not found or not clickable for job: {job_title}')
            print(f'"Submit" button not found or not clickable for job: {job_title}')
            capture_screenshot(f'submit_button_missing_{sanitize_title(job_title)}', subfolder='easy_apply_missing')
            return

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
        capture_screenshot(f'error_applying_{sanitize_title(job_title)}', subfolder='easy_apply_errors')

    except Exception as e:
        logging.error(f'Failed to apply to "{job_title}": {e}')
        print(f'Failed to apply to "{job_title}": {e}')
        capture_screenshot(f'error_applying_{sanitize_title(job_title)}', subfolder='easy_apply_errors')

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
                capture_screenshot(f'job_{index}_no_title', subfolder='job_card_errors')
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
        capture_screenshot('main_exception', subfolder='main_errors')
    finally:
        driver.quit()

# -----------------------------
# Entry Point
# -----------------------------

if __name__ == '__main__':
    main()
