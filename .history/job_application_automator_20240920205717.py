import configparser
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    InvalidArgumentException,
    WebDriverException,
)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

SEARCH_TERMS = config['DEFAULT']['SearchTerms']
RESUME_PATH = config['DEFAULT']['ResumePath']
PAUSE_DURATION = int(config['DEFAULT']['PauseDuration'])
EMAIL = config['DEFAULT']['Email']
PASSWORD = config['DEFAULT']['Password']

# Configure logging
logging.basicConfig(filename='application_log.txt', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Set up Chrome options
chrome_options = Options()
# Uncomment the following line to run the browser in headless mode
# chrome_options.add_argument('--headless')

# Initialize the WebDriver
try:
    driver = webdriver.Chrome(options=chrome_options)
except WebDriverException as e:
    logging.error(f'Error initializing Chrome WebDriver: {e}')
    print(f'Error initializing Chrome WebDriver: {e}')
    exit(1)

# Maximize window
driver.maximize_window()

def login_to_dice():
    try:
        driver.get('https://www.dice.com/dashboard/login')
        time.sleep(3)

        # Locate the email field by name
        email_field = driver.find_element(By.NAME, 'email')
        email_field.clear()
        email_field.send_keys(EMAIL)

        # Locate the "Continue" button by its data-testid attribute
        continue_button = driver.find_element(By.XPATH, '//button[contains(@data-testid, "sign-in-button")]')
        continue_button.click()
        time.sleep(3)

        # After clicking continue, locate the password field and enter the password
        password_field = driver.find_element(By.NAME, 'password')
        password_field.clear()
        password_field.send_keys(PASSWORD)

        # Locate the "Sign In" button and click it
        sign_in_button = driver.find_element(By.XPATH, '//button[contains(@data-testid, "submit-password")]')
        sign_in_button.click()
        time.sleep(5)
        
        logging.info('Successfully logged into Dice.')
        print("Successfully logged into Dice.")
    except NoSuchElementException as e:
        logging.error(f'Error during login: {e}')
        print(f"Error during login: {e}")
        driver.quit()
        exit(1)

def apply_to_job(job_link, job_title):
    try:
        if not job_link or not isinstance(job_link, str):
            logging.error(f'Invalid job link for "{job_title}": {job_link}')
            print(f"Invalid job link for \"{job_title}\": {job_link}")
            return

        driver.get(job_link)
        time.sleep(2)  # Wait for the page to load

        # Find the 'Apply' button; update the XPath if necessary
        apply_button = driver.find_element(By.XPATH, '//button[contains(text(), "Easy Apply")]')
        apply_button.click()
        time.sleep(2)

        # Upload resume
        upload_field = driver.find_element(By.NAME, 'resume')
        upload_field.send_keys(RESUME_PATH)
        time.sleep(2)

        # Submit application
        submit_button = driver.find_element(By.XPATH, '//button[contains(text(), "Submit")]')
        submit_button.click()
        logging.info(f'Successfully applied to {job_link}')
        print(f"Successfully applied to {job_link}")
    except NoSuchElementException as e:
        logging.error(f'Element not found while applying to {job_link}: {e}')
        print(f"Element not found while applying to {job_link}: {e}")
    except InvalidArgumentException as e:
        logging.error(f'Invalid URL "{job_link}": {e}')
        print(f"Invalid URL \"{job_link}\": {e}")
    except Exception as e:
        logging.error(f'Failed to apply to {job_link}: {e}')
        print(f"Failed to apply to {job_link}: {e}")

def main():
    login_to_dice()

    try:
        # Enter search criteria
        driver.get('https://www.dice.com/')
        time.sleep(3)
        search_field = driver.find_element(By.ID, 'typeaheadInput')
        search_field.clear()
        search_field.send_keys(SEARCH_TERMS)
        search_button = driver.find_element(By.ID, 'submitSearch-button')
        search_button.click()
        time.sleep(5)

        # Get the list of job postings
        jobs = driver.find_elements(By.XPATH, '//a[@data-cy="card-title-link"]')
        logging.info(f'Found {len(jobs)} job postings.')
        print(f'Found {len(jobs)} job postings.')

        for index, job in enumerate(jobs):
            job_title = job.text.strip()
            job_link = job.get_attribute('href')

            # Debugging: Log job titles and links
            logging.debug(f'Job {index + 1}: Title="{job_title}", Link="{job_link}"')
            print(f'Job {index + 1}: Title="{job_title}", Link="{job_link}"')

            # Check if the job title contains both "Angular" and "Senior Frontend Developer"
            if 'Angular' in job_title and 'Senior Frontend Developer' in job_title:
                print(f"Applying to job: {job_title}")
                logging.info(f"Applying to job: {job_title} | Link: {job_link}")
                apply_to_job(job_link, job_title)

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

if __name__ == '__main__':
    main()
