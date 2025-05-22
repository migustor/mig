import logging
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    logging.info("Setting up the Chrome driver.")
    options = webdriver.ChromeOptions()
    return webdriver.Chrome(options=options)

def login(driver, username, password):
    logging.info(f"Logging in as {username}")
    driver.get("https://stage28.office.eminiasystem.com/euwhse/receive/enter_po_number.cfm")
    try:
        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login_name")))
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()
        logging.info("Login successful.")
    except TimeoutException:
        logging.error(f"Timeout occurred while logging in for user {username}")

def enter_data(driver, document_number):
    try:
        logging.info(f"Entering document number: {document_number}")
        document_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "document_number")))
        document_input.send_keys(document_number)
        submit_button = driver.find_element(By.ID, "start_receiving")
        submit_button.click()
        logging.info("Data entered successfully.")
    except TimeoutException:
        logging.error("Timeout occurred while entering data.")
    except NoSuchElementException:
        logging.error("Input field or submit button not found.")

def enter_part_number(driver, part_number):
    try:
        logging.info(f"Entering part number: {part_number}")
        part_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "part_number")))
        part_input.send_keys(part_number)
        submit_button = driver.find_element(By.ID, "register_product")
        submit_button.click()
        logging.info("Part number entered successfully.")
    except TimeoutException:
        logging.error("Timeout occurred while entering part number.")
    except NoSuchElementException:
        logging.error("Input field or submit button not found.")

def generate_barcode():
    return f"0X{random.randint(0, 9999):04}"

def enter_barcodes(driver):
    while True:
        try:
            barcodes = generate_barcode()
            logging.info(f"Entering barcode: {barcodes}")
            barcode_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "barcodes")))
            barcode_input.send_keys(barcodes)
            submit_button = driver.find_element(By.ID, "submit_btn")
            submit_button.click()

            # Check for barcode error message
            time.sleep(2)  # Give some time for the error message to appear if any
            error_elements = driver.find_elements(By.CLASS_NAME, "scan_barcode_error")
            if error_elements:
                error_message = error_elements[0].text
                if "already exists in the system" in error_message:
                    logging.warning(f"Error occurred: {error_message}. Generating a new barcode.")
                    continue

            logging.info("Barcode entered successfully.")
            break
        except TimeoutException:
            logging.error("Timeout occurred while entering barcodes.")
        except NoSuchElementException:
            logging.error("Input field or submit button not found.")
            break

def enter_additional_inputs(driver, universal_input_value, box_qty_value):
    try:
        logging.info(f"Entering universal input: {universal_input_value}")
        universal_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "universal")))
        universal_input.send_keys(universal_input_value)
        logging.info(f"Entering box quantity: {box_qty_value}")
        box_qty_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "box_qty")))
        box_qty_input.send_keys(box_qty_value)
        submit_button = driver.find_element(By.ID, "nextItem")
        submit_button.click()
        logging.info("Additional inputs entered and submitted successfully.")
    except TimeoutException:
        logging.error("Timeout occurred while entering additional inputs.")
    except NoSuchElementException:
        logging.error("Input field or submit button not found.")

def check_part_number_received(driver):
    try:
        logging.info("Checking if part number received message is displayed.")
        message_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        message_text = message_element.text
        match = re.search(r"Part number \d+ received", message_text)
        if match:
            logging.info(f"Message found: {match.group(0)}")
            return True
        else:
            logging.warning("Expected message not found.")
            return False
    except TimeoutException:
        logging.error("Timeout occurred while checking part number received message.")
        return False
    except NoSuchElementException:
        logging.error("Message element not found.")
        return False

def generate_test_summary(part_number_received):
    logging.info("Generating test summary.")
    summary = "== Test Summary ==\n"
    summary += f"Part number received message found: {'Yes' if part_number_received else 'No'}\n"
    logging.info("Test summary generated.")
    return summary

if __name__ == "__main__":
    driver = setup_driver()
    try:
        username = "user3364@mteam.test"
        password = "12"
        document_number = "132341"
        part_number = "31402415"
        universal_input_value = "1"
        box_qty_value = "1"
        login(driver, username, password)
        time.sleep(2)  # Wait for login to complete if needed
        enter_data(driver, document_number)
        time.sleep(2)  # Wait for navigation to complete if needed
        enter_part_number(driver, part_number)
        time.sleep(2)  # Wait for navigation to complete if needed
        enter_barcodes(driver)
        time.sleep(2)  # Wait for navigation to complete if needed
        enter_additional_inputs(driver, universal_input_value, box_qty_value)
        time.sleep(2)  # Wait for navigation to complete if needed
        part_number_received = check_part_number_received(driver)
        summary = generate_test_summary(part_number_received)
        logging.info(summary)
        time.sleep(202)
    finally:
        driver.quit()
