import configparser
import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    InvalidArgumentException,
    WebDriverException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

SEARCH_TERMS = config['DEFAULT']['SearchTerms']
RESUME_PATH = config['DEFAULT']['ResumePath']
PAUSE_DURATION = int(config['DEFAULT']['PauseDuration'])
EMAIL = config['DEFAULT']['Email']
PASSWORD = config['DEFAULT']['Password']

# Check if resume exists
if not os.path.isfile(RESUME_PATH):
    print(f'Resume file not found at path: {RESUME_PATH}')
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
        wait = WebDriverWait(driver, 10)

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

        # Wait until dashboard loads by checking URL or specific element
        wait.until(EC.url_contains('/dashboard'))

        logging.info('Successfully logged into Dice.')
        print("Successfully logged into Dice.")
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f'Error during login: {e}')
        print(f"Error during login: {e}")
        driver.quit()
        exit(1)

def apply_to_job(job_card, job_title):
    try:
        wait = WebDriverWait(driver, 10)
        
        # Find and click the 'Easy Apply' button within the job card
        apply_button = job_card.find_element(By.XPATH, './/button[contains(text(), "Easy Apply")]')
        apply_button.click()
        logging.info(f'Clicked "Easy Apply" for job: {job_title}')
        print(f'Clicked "Easy Apply" for job: {job_title}')
        
        # Wait for the resume upload field to be present
        upload_field = wait.until(EC.presence_of_element_located((By.NAME, 'resume')))
        upload_field.send_keys(RESUME_PATH)
        logging.info(f'Uploaded resume for job: {job_title}')
        print(f'Uploaded resume for job: {job_title}')
        
        # Wait for the 'Submit' button to be clickable and click it
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Submit")]')))
        submit_button.click()
        logging.info(f'Successfully applied to {job_title}')
        print(f"Successfully applied to {job_title}")
        
        # Optionally, wait for a confirmation message or element
        # wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Application submitted")]')))
        
    except NoSuchElementException as e:
        logging.error(f'Element not found while applying to "{job_title}": {e}')
        print(f'Element not found while applying to "{job_title}": {e}')
    except TimeoutException as e:
        logging.error(f'Timeout while applying to "{job_title}": {e}')
        print(f'Timeout while applying to "{job_title}": {e}')
    except Exception as e:
        logging.error(f'Failed to apply to "{job_title}": {e}')
        print(f'Failed to apply to "{job_title}": {e}')

def main():
    login_to_dice()

    try:
        # Enter search criteria
        driver.get('https://www.dice.com/')
        wait = WebDriverWait(driver, 10)
        search_field = wait.until(EC.presence_of_element_located((By.ID, 'typeaheadInput')))
        search_field.clear()
        search_field.send_keys(SEARCH_TERMS)
        search_button = driver.find_element(By.ID, 'submitSearch-button')
        search_button.click()

        # Wait until job listings are loaded
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "card search-card")]')))

        # Get the list of job postings
        job_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "card search-card")]')
        logging.info(f'Found {len(job_cards)} job postings.')
        print(f'Found {len(job_cards)} job postings.')

        for index, job_card in enumerate(job_cards, start=1):
            try:
                # Extract the job title
                title_element = job_card.find_element(By.XPATH, './/h5/a[@data-cy="card-title-link"]')
                job_title = title_element.text.strip()
            except NoSuchElementException:
                logging.warning(f'Job {index}: Title element not found.')
                print(f'Job {index}: Title element not found.')
                continue

            # Debugging: Log job titles
            logging.debug(f'Job {index}: Title="{job_title}"')
            print(f'Job {index}: Title="{job_title}"')

            # Check if the job title contains both "Angular" and "Senior Frontend Developer"
            if 'Angular' in job_title and 'Senior Frontend Developer' in job_title:
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

if __name__ == '__main__':
    main()
