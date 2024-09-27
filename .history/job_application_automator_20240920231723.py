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
        driver.get('https://www.dice.com/dashboard/login')
        wait = WebDriverWait(driver, 20)  # Increased timeout for dynamic content

        # Wait for the email field to be present
        email_field = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
        email_field.clear()
        email_field.send_keys(EMAIL)
        logging.info('Entered email.')
        print('Entered email.')

        # Locate and click the "Continue" button
        continue_button = driver.find_element(By.XPATH, '//button[contains(@data-testid, "sign-in-button")]')
        continue_button.click()
        logging.info('Clicked "Continue" button.')
        print('Clicked "Continue" button.')

        # Wait for the password field to be present
        password_field = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        password_field.clear()
        password_field.send_keys(PASSWORD)
        logging.info('Entered password.')
        print('Entered password.')

        # Locate and click the "Sign In" button
        sign_in_button = driver.find_element(By.XPATH, '//button[contains(@data-testid, "submit-password")]')
        sign_in_button.click()
        logging.info('Clicked "Sign In" button.')
        print('Clicked "Sign In" button.')

        # Wait until dashboard loads by checking URL or a specific element
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

    """
    Logs into Dice.com using the provided email and password.
    """
    try:
        driver.get('https://www.dice.com/dashboard/login')
        wait = WebDriverWait(driver, 20)  # Increased timeout for dynamic content

        # Wait for the email field to be present
        email_field = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
        email_field.clear()
        email_field.send_keys(EMAIL)
        logging.info('Entered email.')
        print('Entered email.')

        # Locate and click the "Continue" button
        continue_button = driver.find_element(By.XPATH, '//button[contains(@data-testid, "sign-in-button")]')
        continue_button.click()
        logging.info('Clicked "Continue" button.')
        print('Clicked "Continue" button.')

        # Wait for the password field to be present
        password_field = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        password_field.clear()
        password_field.send_keys(PASSWORD)
        logging.info('Entered password.')
        print('Entered password.')

        # Locate and click the "Sign In" button
        sign_in_button = driver.find_element(By.XPATH, '//button[contains(@data-testid, "submit-password")]')
        sign_in_button.click()
        logging.info('Clicked "Sign In" button.')
        print('Clicked "Sign In" button.')

        # Wait until dashboard loads by checking URL or a specific element
        wait.until(EC.url_contains('/dashboard'))
        logging.info('Successfully logged into Dice.')
        print("Successfully logged into Dice.")
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error during login: {e}')
        print(f"Error during login: {e}")
        capture_screenshot('login_error')
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

def close_popup():
    """
    Closes any pop-up or overlay that might be blocking elements.
    """
    try:
        # Example XPath for a generic close button (update based on actual pop-up)
        popup_close_button = driver.find_element(By.XPATH, '//button[contains(@class, "close-button-class")]')
        popup_close_button.click()
        logging.info('Closed pop-up successfully.')
        print('Closed pop-up successfully.')
        time.sleep(2)  # Wait for the pop-up to close
    except NoSuchElementException:
        logging.info('No pop-up to close.')
        print('No pop-up to close.')
    except Exception as e:
        logging.error(f'Error closing pop-up: {e}')
        print(f'Error closing pop-up: {e}')

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
        print('Filters widget located.')

        # For debugging: log the inner HTML of the filters_widget
        filters_html = filters_widget.get_attribute('innerHTML')
        logging.debug(f'Filters widget inner HTML: {filters_html}')
        print('Logged filters widget inner HTML for debugging.')

        # Locate the "Easy Apply" accordion within the filters widget using CSS Selector
        try:
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

        # Handle cases where 'aria-checked' might be missing or None
        if aria_checked is None:
            # Determine if the filter is active based on other attributes or states
            # For example, check if the icon has a 'selected' class
            try:
                icon = easy_apply_filter_button.find_element(By.TAG_NAME, 'i')
                class_attribute = icon.get_attribute('class')
                if 'selected' not in class_attribute:
                    # Attempt to close any pop-up before clicking
                    close_popup()

                    # Click using ActionChains to ensure the element is in view
                    ActionChains(driver).move_to_element(easy_apply_filter_button).click().perform()
                    logging.info('"Easy Apply" filter activated (based on icon class).')
                    print('"Easy Apply" filter activated (based on icon class).')
                    time.sleep(3)  # Wait for the page to refresh after applying the filter
                else:
                    logging.info('"Easy Apply" filter is already active (based on icon class).')
                    print('"Easy Apply" filter is already active (based on icon class).')
            except NoSuchElementException:
                logging.warning('"Easy Apply" icon not found. Assuming filter is active.')
                print('"Easy Apply" icon not found. Assuming filter is active.')
        else:
            if aria_checked.lower() != 'true':
                # Attempt to close any pop-up before clicking
                close_popup()

                # Click using ActionChains to ensure the element is in view
                try:
                    ActionChains(driver).move_to_element(easy_apply_filter_button).click().perform()
                except ElementClickInterceptedException:
                    logging.warning('"Easy Apply" filter button click intercepted. Attempting JavaScript click.')
                    driver.execute_script("arguments[0].click();", easy_apply_filter_button)
                except ElementNotInteractableException:
                    logging.warning('"Easy Apply" filter button not interactable. Attempting JavaScript click.')
                    driver.execute_script("arguments[0].click();", easy_apply_filter_button)

                logging.info('"Easy Apply" filter activated.')
                print('"Easy Apply" filter activated.')
                # Wait for the page to refresh after applying the filter
                time.sleep(3)  # Adjust as needed based on network speed
            else:
                logging.info('"Easy Apply" filter is already active.')
                print('"Easy Apply" filter is already active.')

        # Verify that the URL contains the required parameters
        current_url = driver.current_url
        expected_params = 'pageSize=100&filters.easyApply=true'
        if expected_params not in current_url:
            logging.warning(f'URL does not contain expected parameters: {expected_params}')
            print(f'URL does not contain expected parameters: {expected_params}')
            # Optionally, navigate to the correct URL directly
            driver.get(f'https://www.dice.com/jobs?q={SEARCH_TERMS}&pageSize=100&filters.easyApply=true')
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

def apply_to_job(job_card, job_title):
    """
    Attempts to apply to a job using the "Apply now" button inside the <apply-button-wc> element.
    """
    try:
        wait = WebDriverWait(driver, 20)  # Increased timeout

        # Click on the job title to open job details
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
        title_element.click()
        logging.info(f'Clicked on job title: {job_title}')
        print(f'Clicked on job title: {job_title}')

        # Wait for the job details panel to load
        job_details = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        logging.debug(f'Job details loaded for: {job_title}')
        print(f'Job details loaded for: {job_title}')

        # Wait explicitly for the "Apply now" button to appear
        apply_button_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'apply-button-wc'))
        )
        logging.info(f'"Apply now" button found for job: {job_title}')
        print(f'"Apply now" button found for job: {job_title}')

        # Attempt to click the button within the <apply-button-wc> custom element
        driver.execute_script("arguments[0].shadowRoot.querySelector('button').click();", apply_button_element)
        logging.info(f'Clicked "Apply now" for job: {job_title}')
        print(f'Clicked "Apply now" for job: {job_title}')

    except TimeoutException:
        logging.error(f'Error: "Apply now" button not found for "{job_title}" after waiting.')
        print(f'Error: "Apply now" button not found for "{job_title}" after waiting.')
        capture_screenshot(f'apply_now_button_missing_{job_title}')
    except (NoSuchElementException, WebDriverException) as e:
        logging.error(f'Error applying to "{job_title}": {e}')
        print(f'Error applying to "{job_title}": {e}')
        capture_screenshot(f'apply_error_{job_title}')
    except Exception as e:
        logging.error(f'Unexpected error applying to "{job_title}": {e}')
        print(f'Unexpected error applying to "{job_title}": {e}')
        capture_screenshot(f'unexpected_apply_error_{job_title}')

    """
    Attempts to apply to a job using the "Apply now" button inside the <apply-button-wc> element.
    """
    try:
        wait = WebDriverWait(driver, 20)  # Increased timeout

        # Click on the job title to open job details
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
        title_element.click()
        logging.info(f'Clicked on job title: {job_title}')
        print(f'Clicked on job title: {job_title}')

        # Wait for the job details panel to load
        job_details = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        logging.debug(f'Job details loaded for: {job_title}')
        print(f'Job details loaded for: {job_title}')

        # Wait explicitly for the "Apply now" button to appear
        apply_now_button = wait.until(
            EC.presence_of_element_located((By.XPATH, './/apply-button-wc | .//button[contains(text(), "Apply now")]'))
        )
        logging.info(f'"Apply now" button found for job: {job_title}')
        print(f'"Apply now" button found for job: {job_title}')

        # Click the "Apply now" button
        apply_now_button.click()
        logging.info(f'Clicked "Apply now" for job: {job_title}')
        print(f'Clicked "Apply now" for job: {job_title}')

        # Optional: Additional steps to complete the application process

    except TimeoutException:
        logging.error(f'Error: "Apply now" button not found for "{job_title}" after waiting.')
        print(f'Error: "Apply now" button not found for "{job_title}" after waiting.')
        capture_screenshot(f'apply_now_button_missing_{job_title}')
    except (NoSuchElementException, WebDriverException) as e:
        logging.error(f'Error applying to "{job_title}": {e}')
        print(f'Error applying to "{job_title}": {e}')
        capture_screenshot(f'apply_error_{job_title}')
    except Exception as e:
        logging.error(f'Unexpected error applying to "{job_title}": {e}')
        print(f'Unexpected error applying to "{job_title}": {e}')
        capture_screenshot(f'unexpected_apply_error_{job_title}')
    """
    Attempts to apply to a job using the "Apply" button inside the <apply-button-wc> element.
    """
    try:
        wait = WebDriverWait(driver, 20)  # Increased timeout

        # Click on the job title to open job details
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
        title_element.click()
        logging.info(f'Clicked on job title: {job_title}')
        print(f'Clicked on job title: {job_title}')

        # Wait for the job details panel to load
        job_details = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        logging.debug(f'Job details loaded for: {job_title}')
        print(f'Job details loaded for: {job_title}')

        # Wait an additional 10 seconds to allow the "Apply" button to load
        time.sleep(10)

        # Attempt to locate and click the <apply-button-wc> element
        try:
            # Directly target the custom element
            apply_button_element = job_details.find_element(By.XPATH, './/apply-button-wc')
            apply_button_element.click()
            logging.info(f'Clicked "Apply" for job: {job_title}')
            print(f'Clicked "Apply" for job: {job_title}')

            # Optional: Additional steps to complete the application process
            return

        except NoSuchElementException:
            logging.info(f'<apply-button-wc> element not found for job: {job_title}. Skipping application.')
            print(f'<apply-button-wc> element not found for job: {job_title}. Skipping application.')
            return

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error applying to "{job_title}": {e}')
        print(f'Error applying to "{job_title}": {e}')

        # Log available buttons and capture a screenshot
        log_available_buttons(job_card, job_title)

    except ElementClickInterceptedException as e:
        logging.error(f'Click intercepted while applying to "{job_title}": {e}')
        print(f'Click intercepted while applying to "{job_title}": {e}')
        capture_screenshot('click_intercepted')

    except ElementNotInteractableException as e:
        logging.error(f'Element not interactable while applying to "{job_title}": {e}')
        print(f'Element not interactable while applying to "{job_title}": {e}')
        capture_screenshot('element_not_interactable')

    except Exception as e:
        logging.error(f'Failed to apply to "{job_title}": {e}')
        print(f'Failed to apply to "{job_title}": {e}')

        # Capture a screenshot for visual debugging
        sanitized_title = "".join([c for c in job_title if c.isalnum() or c in (' ', '_')]).rstrip()
        screenshot_path = f'screenshot_job_{sanitized_title.replace(" ", "_")}_error.png'
        driver.save_screenshot(screenshot_path)
        logging.debug(f'Screenshot saved to {screenshot_path}')
        print(f'Screenshot saved to {screenshot_path}')

    """
    Attempts to apply to a job using the "Apply" button inside the <apply-button-wc> element.
    """
    try:
        wait = WebDriverWait(driver, 20)  # Increased timeout

        # Click on the job title to open job details
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
        title_element.click()
        logging.info(f'Clicked on job title: {job_title}')
        print(f'Clicked on job title: {job_title}')

        # Wait for the job details panel to load
        job_details = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        logging.debug(f'Job details loaded for: {job_title}')
        print(f'Job details loaded for: {job_title}')

        # Wait an additional 10 seconds to allow the "Apply" button to load
        time.sleep(10)

        # Attempt to locate the <apply-button-wc> element
        try:
            apply_button_element = job_details.find_element(By.XPATH, './/apply-button-wc')
            apply_button_element.click()
            logging.info(f'Clicked "Apply" for job: {job_title}')
            print(f'Clicked "Apply" for job: {job_title}')
            
            # Optional: Additional steps to complete the application process
            return
        
        except NoSuchElementException:
            logging.info(f'<apply-button-wc> element not found for job: {job_title}. Skipping application.')
            print(f'<apply-button-wc> element not found for job: {job_title}. Skipping application.')
            return

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error applying to "{job_title}": {e}')
        print(f'Error applying to "{job_title}": {e}')

        # Log available buttons and capture a screenshot
        log_available_buttons(job_card, job_title)

    except ElementClickInterceptedException as e:
        logging.error(f'Click intercepted while applying to "{job_title}": {e}')
        print(f'Click intercepted while applying to "{job_title}": {e}')
        capture_screenshot('click_intercepted')

    except ElementNotInteractableException as e:
        logging.error(f'Element not interactable while applying to "{job_title}": {e}')
        print(f'Element not interactable while applying to "{job_title}": {e}')
        capture_screenshot('element_not_interactable')

    except Exception as e:
        logging.error(f'Failed to apply to "{job_title}": {e}')
        print(f'Failed to apply to "{job_title}": {e}')

        # Capture a screenshot for visual debugging
        sanitized_title = "".join([c for c in job_title if c.isalnum() or c in (' ', '_')]).rstrip()
        screenshot_path = f'screenshot_job_{sanitized_title.replace(" ", "_")}_error.png'
        driver.save_screenshot(screenshot_path)
        logging.debug(f'Screenshot saved to {screenshot_path}')
        print(f'Screenshot saved to {screenshot_path}')

    """
    Attempts to apply to a job using the "Easy Apply" or "Apply now" option.
    """
    try:
        wait = WebDriverWait(driver, 20)  # Increased timeout

        # Click on the job title to open job details
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
        title_element.click()
        logging.info(f'Clicked on job title: {job_title}')
        print(f'Clicked on job title: {job_title}')

        # Wait for the job details panel to load
        job_details = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        logging.debug(f'Job details loaded for: {job_title}')
        print(f'Job details loaded for: {job_title}')

        # Wait an additional 10 seconds to allow the "Easy Apply" or "Apply now" button to load
        time.sleep(10)

        # Attempt to locate either the "Easy Apply" or "Apply now" button
        try:
            easy_apply_button = job_details.find_element(By.XPATH, './/button[contains(@aria-label, "Easy Apply") or contains(@aria-label, "Apply now")]')
            easy_apply_button.click()
            logging.info(f'Clicked "{easy_apply_button.get_attribute("aria-label")}" for job: {job_title}')
            print(f'Clicked "{easy_apply_button.get_attribute("aria-label")}" for job: {job_title}')
            
            # Optional: Additional steps to complete the application process
            return
        
        except NoSuchElementException:
            logging.info(f'Neither "Easy Apply" nor "Apply now" button found for job: {job_title}. Skipping application.')
            print(f'Neither "Easy Apply" nor "Apply now" button found for job: {job_title}. Skipping application.')
            return

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error applying to "{job_title}": {e}')
        print(f'Error applying to "{job_title}": {e}')

        # Log available buttons and capture a screenshot
        log_available_buttons(job_card, job_title)

    except ElementClickInterceptedException as e:
        logging.error(f'Click intercepted while applying to "{job_title}": {e}')
        print(f'Click intercepted while applying to "{job_title}": {e}')
        capture_screenshot('click_intercepted')

    except ElementNotInteractableException as e:
        logging.error(f'Element not interactable while applying to "{job_title}": {e}')
        print(f'Element not interactable while applying to "{job_title}": {e}')
        capture_screenshot('element_not_interactable')

    except Exception as e:
        logging.error(f'Failed to apply to "{job_title}": {e}')
        print(f'Failed to apply to "{job_title}": {e}')

        # Capture a screenshot for visual debugging
        sanitized_title = "".join([c for c in job_title if c.isalnum() or c in (' ', '_')]).rstrip()
        screenshot_path = f'screenshot_job_{sanitized_title.replace(" ", "_")}_error.png'
        driver.save_screenshot(screenshot_path)
        logging.debug(f'Screenshot saved to {screenshot_path}')
        print(f'Screenshot saved to {screenshot_path}')

    """
    Attempts to apply to a job using the "Easy Apply","Apply now"
    """
    try:
        wait = WebDriverWait(driver, 20)  # Increased timeout

        # Click on the job title to open job details
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
        title_element.click()
        logging.info(f'Clicked on job title: {job_title}')
        print(f'Clicked on job title: {job_title}')

        # Wait for the job details panel to load
        job_details = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        logging.debug(f'Job details loaded for: {job_title}')
        print(f'Job details loaded for: {job_title}')

        # Wait an additional 10 seconds to allow the "Apply now" button to load
        time.sleep(10)

        # Check if 'Apply now' button is present; if so, click it
        if has_apply_now(job_details):
            apply_now_button = job_details.find_element(By.XPATH, './/button[contains(text(), "Apply now")]')
            apply_now_button.click()
            logging.info(f'Clicked "Apply now" for job: {job_title}')
            print(f'Clicked "Apply now" for job: {job_title}')

            # Optional: Additional steps to complete the application process

            return
        else:
            logging.info(f'"Apply now" button not found for job: {job_title}. Skipping application.')
            print(f'"Apply now" button not found for job: {job_title}. Skipping application.')
            return

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error applying to "{job_title}": {e}')
        print(f'Error applying to "{job_title}": {e}')

        # Log available buttons and capture a screenshot
        log_available_buttons(job_card, job_title)

    except ElementClickInterceptedException as e:
        logging.error(f'Click intercepted while applying to "{job_title}": {e}')
        print(f'Click intercepted while applying to "{job_title}": {e}')
        capture_screenshot('click_intercepted')

    except ElementNotInteractableException as e:
        logging.error(f'Element not interactable while applying to "{job_title}": {e}')
        print(f'Element not interactable while applying to "{job_title}": {e}')
        capture_screenshot('element_not_interactable')

    except Exception as e:
        logging.error(f'Failed to apply to "{job_title}": {e}')
        print(f'Failed to apply to "{job_title}": {e}')

        # Capture a screenshot for visual debugging
        sanitized_title = "".join([c for c in job_title if c.isalnum() or c in (' ', '_')]).rstrip()
        screenshot_path = f'screenshot_job_{sanitized_title.replace(" ", "_")}_error.png'
        driver.save_screenshot(screenshot_path)
        logging.debug(f'Screenshot saved to {screenshot_path}')
        print(f'Screenshot saved to {screenshot_path}')

    """
    Attempts to apply to a job using the "Easy Apply" or "Apply now" option.
    
    """
    try:
        wait = WebDriverWait(driver, 20)  # Increased timeout

        # Click on the job title to open job details
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
        title_element.click()
        logging.info(f'Clicked on job title: {job_title}')
        print(f'Clicked on job title: {job_title}')

        # Wait for the job details panel to load
        job_details = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        logging.debug(f'Job details loaded for: {job_title}')
        print(f'Job details loaded for: {job_title}')

        # Attempt to locate the 'Easy Apply' button within job details using a precise selector
        try:
            easy_apply_button = job_details.find_element(By.XPATH, './/button[contains(@aria-label, "Easy Apply")]')
            easy_apply_button.click()
            logging.info(f'Clicked "Easy Apply" for job: {job_title}')
            print(f'Clicked "Easy Apply" for job: {job_title}')

            # Wait for the apply modal to appear
            modal = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "apply-modal")]')))
            logging.debug(f'Apply modal appeared for job: {job_title}')
            print(f'Apply modal appeared for job: {job_title}')

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
            # 'Easy Apply' button not found within job details
            logging.info(f'"Easy Apply" button not found for job: {job_title}. Skipping application.')
            print(f'"Easy Apply" button not found for job: {job_title}. Skipping application.')

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error applying to "{job_title}": {e}')
        print(f'Error applying to "{job_title}": {e}')

        # Log available buttons and capture a screenshot
        log_available_buttons(job_card, job_title)

    except ElementClickInterceptedException as e:
        logging.error(f'Click intercepted while applying to "{job_title}": {e}')
        print(f'Click intercepted while applying to "{job_title}": {e}')
        capture_screenshot('click_intercepted')

    except ElementNotInteractableException as e:
        logging.error(f'Element not interactable while applying to "{job_title}": {e}')
        print(f'Element not interactable while applying to "{job_title}": {e}')
        capture_screenshot('element_not_interactable')

    except Exception as e:
        logging.error(f'Failed to apply to "{job_title}": {e}')
        print(f'Failed to apply to "{job_title}": {e}')

        # Capture a screenshot for visual debugging
        sanitized_title = "".join([c for c in job_title if c.isalnum() or c in (' ', '_')]).rstrip()
        screenshot_path = f'screenshot_job_{sanitized_title.replace(" ", "_")}_error.png'
        driver.save_screenshot(screenshot_path)
        logging.debug(f'Screenshot saved to {screenshot_path}')
        print(f'Screenshot saved to {screenshot_path}')

def main():
    login_to_dice()

    try:
        # Enter search criteria
        driver.get('https://www.dice.com/')
        wait = WebDriverWait(driver, 20)  # Increased timeout
        search_field = wait.until(EC.presence_of_element_located((By.ID, 'typeaheadInput')))
        search_field.clear()
        search_field.send_keys(SEARCH_TERMS)
        logging.info(f'Entered search terms: {SEARCH_TERMS}')
        print(f'Entered search terms: {SEARCH_TERMS}')

        search_button = driver.find_element(By.ID, 'submitSearch-button')
        search_button.click()
        logging.info('Clicked search button.')
        print('Clicked search button.')

        # Activate the "Easy Apply" filter
        activate_easy_apply_filter()

        # Wait for job listings to load
        time.sleep(3)  # Add a small delay to ensure the page is loaded after applying the filter

        # Get the list of job postings
        job_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
        logging.info(f'Found {len(job_cards)} job postings.')
        print(f'Found {len(job_cards)} job postings.')

        for index, job_card in enumerate(job_cards, start=1):
            try:
                # Extract the job title using data-cy attribute
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
                apply_to_job(job_card, job_title)

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
    login_to_dice()

    try:
        # Enter search criteria
        driver.get('https://www.dice.com/')
        wait = WebDriverWait(driver, 20)  # Increased timeout
        search_field = wait.until(EC.presence_of_element_located((By.ID, 'typeaheadInput')))
        search_field.clear()
        search_field.send_keys(SEARCH_TERMS)
        logging.info(f'Entered search terms: {SEARCH_TERMS}')
        print(f'Entered search terms: {SEARCH_TERMS}')

        search_button = driver.find_element(By.ID, 'submitSearch-button')
        search_button.click()
        logging.info('Clicked search button.')
        print('Clicked search button.')

        # Activate the "Easy Apply" filter
        activate_easy_apply_filter()

        # Ensure the page is fully loaded before attempting to click the search button again
        time.sleep(3)  # Add a small delay to ensure the page is loaded after applying the filter

        # -----------------------------
        # **New Step: Click Search Button Again**
        # -----------------------------
        try:
            # Wait until the search button is present and clickable
            search_button = wait.until(EC.element_to_be_clickable((By.ID, 'submitSearch-button')))
            
            # Attempt to click the search button using ActionChains
            ActionChains(driver).move_to_element(search_button).click().perform()
            logging.info('Clicked search button again after applying "Easy Apply" filter.')
            print('Clicked search button again after applying "Easy Apply" filter.')

            # Wait until job listings are loaded again
            wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
            ))
            logging.info('Job listings reloaded after applying filter.')
            print('Job listings reloaded after applying filter.')

            # Get the updated list of job postings
            job_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
            logging.info(f'Found {len(job_cards)} job postings after applying filter.')
            print(f'Found {len(job_cards)} job postings after applying filter.')

        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f'Error clicking search button again: {e}')
            print(f'Error clicking search button again: {e}')
            capture_screenshot('error_clicking_search_again')
            driver.quit()
            exit(1)

        # Wait until job listings are loaded
        wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
        ))
        logging.info('Job listings loaded.')
        print('Job listings loaded.')

        # Get the list of job postings
        job_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
        logging.info(f'Found {len(job_cards)} job postings.')
        print(f'Found {len(job_cards)} job postings.')

        for index, job_card in enumerate(job_cards, start=1):
            try:
                # Extract the job title using data-cy attribute
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
                apply_to_job(job_card, job_title)

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
