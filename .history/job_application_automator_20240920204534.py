# job_application_automator.py

import configparser
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

SEARCH_TERMS = config['DEFAULT']['SearchTerms']
RESUME_PATH = config['DEFAULT']['ResumePath']
PAUSE_DURATION = int(config['DEFAULT']['PauseDuration'])
EMAIL = config['DEFAULT']['Email']
PASSWORD = config['DEFAULT']['Password']

# Configure logging
logging.basicConfig(filename='application_log.txt', level=logging.INFO)

# Set up Chrome options
chrome_options = Options()
# Uncomment the following line to run the browser in headless mode
# chrome_options.add_argument('--headless')

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Maximize window
driver.maximize_window()

def login_to_dice():
    driver.get('https://www.dice.com/dashboard/login')
    time.sleep(3)
    
    # Locate the email field by name
    email_field = driver.find_element(By.NAME, 'email')
    email_field.clear()
    email_field.send_keys(EMAIL)
    
    # Locate the "Continue" button by its text or another attribute
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

def apply_to_job(job_link):
    driver.get(job_link)
    time.sleep(2)  # Wait for the page to load

    try:
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
    except Exception as e:
        logging.error(f'Failed to apply to {job_link}: {e}')
        print(f"Failed to apply to {job_link}: {e}")

def main():
    login_to_dice()

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

    for index, job in enumerate(jobs):
        job_title = job.text

        # Check if the job title contains both "Angular" and "Senior Frontend Developer"
        if 'Angular' in job_title and 'Senior Frontend Developer' in job_title:
            print(f"Applying to job: {job_title}")
            job_link = job.get_attribute('href')
            apply_to_job(job_link)

            # Pause for specified duration before the next application
            print(f"Waiting for {PAUSE_DURATION} seconds before the next application...")
            time.sleep(PAUSE_DURATION)
        else:
            print(f"Skipping job: {job_title}")

    print("Job application process completed.")

if __name__ == '__main__':
    try:
        main()
    finally:
        driver.quit()
