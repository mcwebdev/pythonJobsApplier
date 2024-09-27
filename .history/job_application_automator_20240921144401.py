import configparser
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
    exit(1)

# Set up Chrome options
chrome_options = Options()
# Uncomment the following line to run the browser in headless mode
# chrome_options.add_argument('--headless')

# Optional: Ignore SSL certificate errors (Use with caution)
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
 Chrome/91.0.4472.124 Safari/537.36')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

# Add options to use your existing Chrome profile
chrome_options.add_argument("user-data-dir=C:\\Users\\d33psp33d\\AppData\\Local\\Google\\Chrome\\User Data")
chrome_options.add_argument("profile-directory=Default")  # Or the name of your profile directory

# Initialize the WebDriver
try:
    driver = webdriver.Chrome(options=chrome_options)
    print("Initialized Chrome WebDriver.")
except WebDriverException as e:
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
        print(f'Screenshot saved to {screenshot_path}')
    except Exception as e:
        print(f'Failed to capture screenshot "{name}": {e}')

# -----------------------------
# Function Definitions
# -----------------------------

def activate_easy_apply_filter():
    """
    Activates the "Easy Apply" filter to focus on jobs that offer this option.
    Ensures that the filter button is clickable and not obscured by overlays.
    """
    try:
        wait = WebDriverWait(driver, 20)  # Increased timeout for dynamic content

        # Wait for the filters widget to load
        print('Waiting for filters widget.')
        filters_widget = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'dhi-filters-widget')))
        print('Filters widget located.')

        # Locate the "Easy Apply" accordion within the filters widget using CSS Selector
        try:
            print('Locating "Easy Apply" accordion.')
            easy_apply_accordion = WebDriverWait(filters_widget, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'dhi-accordion[data-cy="accordion-easyApply"]'))
            )
            print('"Easy Apply" accordion located.')
        except TimeoutException:
            print('"Easy Apply" accordion not found within filters widget.')
            capture_screenshot('missing_easy_apply_accordion', subfolder='filters')
            driver.quit()
            exit(1)

        # Scroll the "Easy Apply" accordion into view
        driver.execute_script("arguments[0].scrollIntoView(true);", easy_apply_accordion)
        time.sleep(1)  # Wait for scrolling animation

        # Locate the filter button within the "Easy Apply" accordion using a more precise selector
        try:
            print('Locating "Easy Apply" filter button.')
            easy_apply_filter_button = easy_apply_accordion.find_element(
                By.XPATH, './/js-single-select-filter[@data-cy="filter-easyApply"]//button[@aria-label="Filter Search Results by Easy Apply"]'
            )
            print('"Easy Apply" filter button located.')
        except NoSuchElementException:
            print('"Easy Apply" filter button not found within accordion.')
            capture_screenshot('missing_easy_apply_filter_button', subfolder='filters')
            driver.quit()
            exit(1)

        # Wait until the "Easy Apply" filter button is clickable
        try:
            print('Waiting for "Easy Apply" filter button to be clickable.')
            easy_apply_filter_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, './/js-single-select-filter[@data-cy="filter-easyApply"]//button[@aria-label="Filter Search Results by Easy Apply"]'))
            )
        except TimeoutException:
            print('"Easy Apply" filter button is not clickable.')
            capture_screenshot('easy_apply_not_clickable', subfolder='filters')
            driver.quit()
            exit(1)

        # Check if the "Easy Apply" filter is already active
        aria_checked = easy_apply_filter_button.get_attribute('aria-checked')
        print(f'"Easy Apply" aria-checked: {aria_checked}')

        if aria_checked == 'true':
            print('"Easy Apply" filter is already active.')
        else:
            # Click using ActionChains to ensure the element is in view
            try:
                print('Attempting to click "Easy Apply" filter button.')
                ActionChains(driver).move_to_element(easy_apply_filter_button).click().perform()
            except (ElementClickInterceptedException, ElementNotInteractableException) as e:
                print(f'"Easy Apply" filter button not interactable: {e}. Attempting JavaScript click.')
                driver.execute_script("arguments[0].click();", easy_apply_filter_button)

            print('"Easy Apply" filter activated.')
            # Wait for the page to refresh after applying the filter
            time.sleep(3)  # Adjust as needed based on network speed

        # Verify that the URL contains the required parameters
        current_url = driver.current_url
        expected_params = 'filters.easyApply=true'
        if expected_params not in current_url:
            print(f'URL does not contain expected parameters: {expected_params}')
            # Optionally, navigate to the correct URL directly
            driver.get(f'https://www.dice.com/jobs?q={SEARCH_TERMS}&filters.easyApply=true')
            # Wait for job listings to load
            wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
            ))
            print('Navigated to filtered URL.')
        else:
            print('URL contains the expected filter parameters.')

    except (NoSuchElementException, TimeoutException) as e:
        print(f'Error activating "Easy Apply" filter: {e}')
        capture_screenshot('error_activating_easy_apply_filter', subfolder='filters')
        driver.quit()
        exit(1)
    except Exception as e:
        print(f"Unexpected error activating 'Easy Apply' filter: {e}")
        capture_screenshot('unexpected_error_easy_apply_filter', subfolder='filters')
        driver.quit()
        exit(1)

def log_available_buttons(job_card, job_title):
    """
    Logs all available buttons within a job card for debugging purposes.
    """
    try:
        buttons = job_card.find_elements(By.TAG_NAME, 'button')
        button_texts = [button.text for button in buttons]
        print(f'Available buttons for job "{job_title}": {button_texts}')

        # Capture a screenshot for visual debugging
        sanitized_title = sanitize_title(job_title)
        screenshot_path = os.path.join('screenshots', 'missing_easy_apply', f'screenshot_job_{sanitized_title}.png')
        driver.save_screenshot(screenshot_path)
        print(f'Screenshot saved to {screenshot_path}')
    except Exception as e:
        print(f'Error logging available buttons for "{job_title}": {e}')

def apply_to_job(job_card, job_title, applied_jobs):
    """
    Attempts to apply to a job by handling the navigation to the application page.
    """
    try:
        if job_title in applied_jobs:
            print(f'Skipping already applied job: {job_title}')
            return  # Skip if we've already applied to this job

        wait = WebDriverWait(driver, 20)  # Adjust timeout as needed

        # Scroll the job card into view
        print(f'Scrolling into view for job: {job_title}')
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
        time.sleep(1)  # Wait for scrolling animation

        # Click on the job title to open job details
        print(f'Locating job title link for: {job_title}')
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')

        # Wait until the title_element is clickable
        print(f'Waiting for job title to be clickable for: {job_title}')
        wait.until(EC.element_to_be_clickable((By.XPATH, './/a[@data-cy="card-title-link"]')))

        try:
            print(f'Attempting to click on job title: {job_title}')
            title_element.click()
            print(f'Clicked on job title: {job_title}')
        except (ElementClickInterceptedException, ElementNotInteractableException) as e:
            print(f'Click intercepted or element not interactable for job title: {job_title}. Trying JavaScript click.')
            driver.execute_script("arguments[0].click();", title_element)

        # Check if a new window has been opened
        original_window = driver.current_window_handle
        windows_after_click = driver.window_handles
        if len(windows_after_click) > 1:
            new_window = [window for window in windows_after_click if window != original_window][0]
            driver.switch_to.window(new_window)
            print(f'Switched to new window for job: {job_title}')
        else:
            # Job details opened in the same window
            print(f'Job details opened in the same window for job: {job_title}')

        # Wait for the job details page to load
        print(f'Waiting for job details to load for: {job_title}')
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        time.sleep(2)  # Additional wait to ensure all elements are loaded
        print(f'Job details loaded for: {job_title}')

        # Locate and click the "Easy Apply" button
        print(f'Locating "Easy Apply" button for job: {job_title}')
        easy_apply_button = driver.find_element(By.CSS_SELECTOR, 'apply-button-wc')
        driver.execute_script('arguments[0].scrollIntoView(true);', easy_apply_button)
        time.sleep(1)

        # Access the shadow root of the "Easy Apply" button
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', easy_apply_button)
        apply_now_button = shadow_root.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')
        print('Easy Apply button found')

        # Click the "Easy Apply" button
        try:
            apply_now_button.click()
            print("Clicked 'Easy Apply' button.")
        except Exception as e:
            print(f"Click failed: {e}, trying JavaScript click.")
            driver.execute_script("arguments[0].click();", apply_now_button)
            print("Clicked 'Easy Apply' button using JavaScript.")

        # Wait for navigation to the application page
        print('Waiting for navigation to the application page.')
        wait.until(EC.url_contains('/apply'))
        print('Navigated to application page.')

        # Now on the application page, proceed with the application
        # Wait for the "Next" button to appear
        print('Waiting for "Next" button on the application page.')
        next_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button.btn-next')
        ))
        print('"Next" button found.')

        # Click the "Next" button
        next_button.click()
        print('Clicked "Next" button.')

        # Wait for the resume upload field
        print('Waiting for resume upload field.')
        upload_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]')))
        print('Resume upload field found.')

        # Upload the resume
        upload_field.send_keys(RESUME_PATH)
        print(f'Uploaded resume for job: {job_title}')

        # Wait for the "Submit" button to be clickable
        print('Waiting for "Submit" button.')
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Submit")]')))
        print('"Submit" button found.')

        # Click the "Submit" button
        submit_button.click()
        print(f"Successfully applied to {job_title}")

        # Add the job to the set of applied jobs
        applied_jobs.add(job_title)

        # Close the new window or navigate back
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)
            print(f'Closed new window and switched back to original window after processing {job_title}')
        else:
            # Navigate back to the job listings page
            driver.back()
            print(f'Navigated back to job listings after processing {job_title}')

    except (NoSuchElementException, TimeoutException) as e:
        print(f'Error applying to "{job_title}": {e}')
        # Log available buttons and capture a screenshot
        log_available_buttons(job_card, job_title)
        capture_screenshot(f'error_applying_{sanitize_title(job_title)}', subfolder='easy_apply_errors')

    except Exception as e:
        print(f'Failed to apply to "{job_title}": {e}')
        capture_screenshot(f'error_applying_{sanitize_title(job_title)}', subfolder='easy_apply_errors')

    finally:
        # Ensure that any new window is closed and focus is back to the original window
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)
            print(f'Closed new window and switched back to original window after processing {job_title}')

    """
    Attempts to apply to a job by handling the navigation to the application page.
    """
    try:
        if job_title in applied_jobs:
            print(f'Skipping already applied job: {job_title}')
            return  # Skip if we've already applied to this job

        wait = WebDriverWait(driver, 20)  # Adjust timeout as needed

        # Scroll the job card into view
        print(f'Scrolling into view for job: {job_title}')
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
        time.sleep(1)  # Wait for scrolling animation

        # Click on the job title to open job details
        print(f'Locating job title link for: {job_title}')
        title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')

        # Wait until the title_element is clickable
        print(f'Waiting for job title to be clickable for: {job_title}')
        wait.until(EC.element_to_be_clickable((By.XPATH, './/a[@data-cy="card-title-link"]')))

        try:
            print(f'Attempting to click on job title: {job_title}')
            title_element.click()
            print(f'Clicked on job title: {job_title}')
        except (ElementClickInterceptedException, ElementNotInteractableException) as e:
            print(f'Click intercepted or element not interactable for job title: {job_title}. Trying JavaScript click.')
            driver.execute_script("arguments[0].click();", title_element)

        # Check if a new window has been opened
        original_window = driver.current_window_handle
        windows_after_click = driver.window_handles
        if len(windows_after_click) > 1:
            new_window = [window for window in windows_after_click if window != original_window][0]
            driver.switch_to.window(new_window)
            print(f'Switched to new window for job: {job_title}')
        else:
            # Job details opened in the same window
            print(f'Job details opened in the same window for job: {job_title}')

        # Wait for the job details page to load
        print(f'Waiting for job details to load for: {job_title}')
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "job-details")]')))
        time.sleep(2)  # Additional wait to ensure all elements are loaded
        print(f'Job details loaded for: {job_title}')

        # Locate and click the "Easy Apply" button
        print(f'Locating "Easy Apply" button for job: {job_title}')
        easy_apply_button = driver.find_element(By.CSS_SELECTOR, 'apply-button-wc')
        driver.execute_script('arguments[0].scrollIntoView(true);', easy_apply_button)
        time.sleep(1)

        # Access the shadow root of the "Easy Apply" button
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', easy_apply_button)
        apply_now_button = shadow_root.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary')
        print('Easy Apply button found')

        # Click the "Easy Apply" button
        try:
            apply_now_button.click()
            print("Clicked 'Easy Apply' button.")
        except Exception as e:
            print(f"Click failed: {e}, trying JavaScript click.")
            driver.execute_script("arguments[0].click();", apply_now_button)
            print("Clicked 'Easy Apply' button using JavaScript.")

        # Wait for navigation to the application page
        print('Waiting for navigation to the application page.')
        wait.until(EC.url_contains('/apply'))
        print('Navigated to application page.')

        # Now on the application page, proceed with the application
        # Wait for the "Next" button to appear
        print('Waiting for "Next" button on the application page.')
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Next")]')))
        print('"Next" button found.')

        # Click the "Next" button
        next_button.click()
        print('Clicked "Next" button.')

        # Wait for the resume upload field
        print('Waiting for resume upload field.')
        upload_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]')))
        print('Resume upload field found.')

        # Upload the resume
        upload_field.send_keys(RESUME_PATH)
        print(f'Uploaded resume for job: {job_title}')

        # Wait for the "Submit" button to be clickable
        print('Waiting for "Submit" button.')
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Submit")]')))
        print('"Submit" button found.')

        # Click the "Submit" button
        submit_button.click()
        print(f"Successfully applied to {job_title}")

        # Add the job to the set of applied jobs
        applied_jobs.add(job_title)

        # Close the new window or navigate back
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)
            print(f'Closed new window and switched back to original window after processing {job_title}')
        else:
            # Navigate back to the job listings page
            driver.back()
            print(f'Navigated back to job listings after processing {job_title}')

    except (NoSuchElementException, TimeoutException) as e:
        print(f'Error applying to "{job_title}": {e}')
        # Log available buttons and capture a screenshot
        log_available_buttons(job_card, job_title)
        capture_screenshot(f'error_applying_{sanitize_title(job_title)}', subfolder='easy_apply_errors')

    except Exception as e:
        print(f'Failed to apply to "{job_title}": {e}')
        capture_screenshot(f'error_applying_{sanitize_title(job_title)}', subfolder='easy_apply_errors')

    finally:
        # Ensure that any new window is closed and focus is back to the original window
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)
            print(f'Closed new window and switched back to original window after processing {job_title}')

def main():
    applied_jobs = set()  # Track jobs that have been applied to

    try:
        print('Navigating to Dice homepage.')
        # Enter search criteria
        driver.get('https://www.dice.com/')
        wait = WebDriverWait(driver, 20)  # Adjust timeout as needed
        print('Waiting for search field.')
        search_field = wait.until(EC.presence_of_element_located((By.ID, 'typeaheadInput')))
        search_field.clear()
        search_field.send_keys(SEARCH_TERMS)
        print(f'Entered search terms: {SEARCH_TERMS}')

        print('Locating search button.')
        search_button = driver.find_element(By.ID, 'submitSearch-button')
        search_button.click()
        print('Clicked search button.')

        # Activate the "Easy Apply" filter
        activate_easy_apply_filter()

        # Wait for job listings to load
        time.sleep(3)  # Add a small delay to ensure the page is loaded after applying the filter

        # Get the list of job postings
        print('Locating job cards.')
        job_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "card") and contains(@class, "search-card")]')
        print(f'Found {len(job_cards)} job postings.')

        for index, job_card in enumerate(job_cards, start=1):
            try:
                # Extract the job title using data-cy attribute
                print(f'Processing job {index}.')
                title_element = job_card.find_element(By.XPATH, './/a[@data-cy="card-title-link"]')
                job_title = title_element.text.strip()
                print(f'Job {index}: Found title: {job_title}')

            except NoSuchElementException:
                print(f'Job {index}: Title element not found.')
                # Debugging: Print the outer HTML of the job card
                job_card_html = job_card.get_attribute('outerHTML')
                print(f'Job {index} HTML: {job_card_html}')
                capture_screenshot(f'job_{index}_no_title', subfolder='job_card_errors')
                continue

            print(f'Job {index}: Title="{job_title}"')

            # Simplified criteria for applying
            if 'angular' in job_title.lower() and ('lead' in job_title.lower() or 'senior' in job_title.lower() or 'frontend' in job_title.lower()):
                print(f'Applying to job: {job_title}')
                apply_to_job(job_card, job_title, applied_jobs)

                # Pause for specified duration before the next application
                print(f"Waiting for {PAUSE_DURATION} seconds before the next application...")
                time.sleep(PAUSE_DURATION)
            else:
                print(f"Skipping job: {job_title}")

        print("Job application process completed.")
    except Exception as e:
        print(f"An error occurred in main(): {e}")
        capture_screenshot('main_exception', subfolder='main_errors')
    finally:
        driver.quit()

# -----------------------------
# Entry Point
# -----------------------------

if __name__ == '__main__':
    main()
