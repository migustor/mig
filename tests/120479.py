import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from time import sleep
import time


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    logging.info("Setting up the Chrome driver.")
    options = webdriver.ChromeOptions()
    return webdriver.Chrome(options=options)

def login(driver, username, password):
    logging.info(f"Logging in as {username}")
    driver.get("https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=950")
    try:
        username_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "login_name")))
        password_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "password")))
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()
        logging.info("Login successful.")
    except TimeoutException:
        logging.error("Timeout occurred while logging in.")
        return False
    return True

def check_and_click_radio_button(driver):
    retries = 3  # Number of retry attempts
    for attempt in range(retries):
        try:
            logging.info("Attempting to locate the 'Include in KPI' radio button (attempt {}/{}).".format(attempt + 1, retries))

            # Wait for the radio button to be present in the DOM
            radio_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "data_include_in_kpi")))

            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_button)
            time.sleep(1)  # Give the page a little time after scrolling

            # Set focus and click via JavaScript to ensure it is properly clicked
            driver.execute_script("arguments[0].focus(); arguments[0].click();", radio_button)
            logging.info("'Include in KPI' radio button clicked successfully.")
            return True

        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException) as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)  # Wait before retrying in case the element is dynamically loaded or obscured

    logging.error("Unable to interact with the 'Include in KPI' radio button after multiple attempts.")
    return False

def click_submit_button(driver):
    try:
        logging.info("Attempting to click the 'Submit' button.")
        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.btn.btn-primary.submit_report.btns_cer")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
        time.sleep(1)  # Ensure the button is in view
        submit_button.click()
        logging.info("'Submit' button clicked successfully.")
        return True
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException) as e:
        logging.error(f"Failed to click the 'Submit' button: {e}")
        return False

def verify_chart_and_table(driver):
    results = {"chart_found": False, "table_found": False}
    try:
        logging.info("Waiting for the chart and table to be loaded.")

        # Wait for the chart to be present
        box_chart = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "box_chart")))
        if box_chart:
            logging.info("Chart with ID 'box_chart' is present.")
            results["chart_found"] = True

        # Wait for the table to be present with a more flexible XPath
        table_heading = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='panel-heading']/h4[starts-with(text(), 'Customer Evolution')]"))
        )
        if table_heading:
            logging.info("Table with heading 'Customer Evolution' is present.")
            results["table_found"] = True

    except TimeoutException as e:
        logging.error(f"Timeout occurred while waiting for chart or table: {e}")

    return results

def generate_test_summary(results):
    logging.info("Generating test summary.")
    summary = "== Test Summary ==\n"
    summary += f"Chart with ID 'box_chart' found: {'Yes' if results['chart_found'] else 'No'}\n"
    summary += f"Table with heading 'Customer Evolution' found: {'Yes' if results['table_found'] else 'No'}\n"
    summary += "------------------------------------------\n"
    logging.info("Test summary generated.")
    logging.info(summary)

def main(username, password):
    driver = setup_driver()
    try:
        if login(driver, username, password):
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Ensure page load
            if check_and_click_radio_button(driver):
                logging.info("Radio button interaction successful.")
                if click_submit_button(driver):
                    logging.info("Submit button interaction successful.")
                    results = verify_chart_and_table(driver)
                    generate_test_summary(results)
                else:
                    logging.error("Submit button interaction failed.")
    finally:
        logging.info("Pausing to allow visual inspection of results. Close the browser manually to proceed.")
        sleep(5)  # Pause for 60 seconds for visual inspection
        driver.quit()

# Example usage
main("dmitri.dubkovetki@mteam.md", "12")
