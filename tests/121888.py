import os
import logging
import time
import random
import string
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.common.exceptions import TimeoutException

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Driver options
script_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = script_dir
chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True,
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)
driver.maximize_window()

username = os.getenv("USERNAMEALEX")
password = os.getenv("PASSWORDALEX")

if not username or not password:
    logging.error("Environment variables USERNAMEALEX and PASSWORDALEX are not set in .env.")
    driver.quit()
    sys.exit(1)

def login_to_system(login_url):
    try:
        driver.get(login_url)
        logging.info(f"Navigating to the login page: {login_url}")

        time.sleep(1)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "login_name")))
        username_field.clear()
        username_field.send_keys(username)
        logging.info("Entered username.")

        time.sleep(1)
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        logging.info("Entered password.")

        time.sleep(1)
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        logging.info("Clicked the login button.")

        time.sleep(2)

    except Exception as e:
        logging.error(f"Error during login: {e}", exc_info=True)
        driver.quit()
        sys.exit(1)

def check_kilograms_on_page(page_url):
    try:
        driver.get(page_url)
        logging.info(f"Checking the dropdown on page: {page_url}")

        dropdown_element = wait.until(
            EC.presence_of_element_located((By.ID, "shipping_weight_type"))
        )
        select = Select(dropdown_element)
        selected_option = select.first_selected_option

        if selected_option.get_attribute("value") == "1":
            logging.info("The default option is 'Kilograms'. Test passed.")
            return True
        else:
            logging.error(
                f"Expected 'Kilograms', but got: '{selected_option.text.strip()}'. Test failed."
            )
            return False

    except TimeoutException:
        logging.error(f"The dropdown 'shipping_weight_type' was not found on page {page_url}.")
        return False
    except Exception as e:
        logging.error(f"Error checking the dropdown on page {page_url}: {e}", exc_info=True)
        return False

def generate_random_part_number(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def check_kilograms_selected(select_element_id="shipping_weight_type"):
    try:
        dropdown_element = wait.until(
            EC.presence_of_element_located((By.ID, select_element_id))
        )
        select = Select(dropdown_element)
        selected_option = select.first_selected_option
        if selected_option.get_attribute("value") == "1":
            logging.info("The default option is 'Kilograms'.")
            return True
        else:
            logging.error(
                f"Expected 'Kilograms', but got: '{selected_option.text.strip()}'."
            )
            return False
    except Exception as e:
        logging.error("Error checking 'Kilograms' on the current page:", exc_info=True)
        return False

def create_item_on_page_739(page_url):
    try:
        driver.get(page_url)
        logging.info(f"Opening page: {page_url}")

        part_number_input = wait.until(
            EC.presence_of_element_located((By.ID, "part_number_1"))
        )
        random_pn = generate_random_part_number(12)
        part_number_input.clear()
        part_number_input.send_keys(random_pn)
        logging.info(f"Entered random Part Number: {random_pn}")

        brand_dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "brand"))
        )
        Select(brand_dropdown).select_by_value("2595")
        logging.info("Selected Brand (value=2595).")

        quantity_field = wait.until(
            EC.presence_of_element_located((By.ID, "shipping_weight"))
        )
        quantity_field.clear()
        quantity_field.send_keys("1")
        logging.info("Entered '1' in the shipping_weight field.")

        create_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-warning[type='submit']")
        create_button.click()
        logging.info("Clicked the 'Create' button.")

        success_alert = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.alert.alert-success"))
        )
        logging.info("Item successfully created (success alert is displayed).")

        success_link = success_alert.find_element(By.TAG_NAME, "a")
        success_link_href = success_link.get_attribute("href")
        logging.info(f"Navigating via link: {success_link_href}")
        success_link.click()

        # Check if 'Kilograms' is selected
        return check_kilograms_selected()

    except Exception as e:
        logging.error(f"Error while creating an item on page {page_url}: {e}", exc_info=True)
        return False

def main():
    try:
        login_url = "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=39"
        login_to_system(login_url)

        # Test results
        link1_result = check_kilograms_on_page("https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=739")
        link2_result = check_kilograms_on_page("https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=22&phase=new")
        link3_result = create_item_on_page_739("https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=739")

        # Prepare summary text for each link
        link1_text = "Page 739 (Quick Create) - Test Passed" if link1_result else "Page 739 (Quick Create) - Test Failed"
        link2_text = "Page 22 (Simple Create) - Test Passed" if link2_result else "Page 22 (Simple Create) - Test Failed"
        link3_text = "Page 22 (Item Page) - Test Passed" if link3_result else "Page 22 (Item Page) - Test Failed"

        # Print summary report
        logging.info("TEST SUMMARY:")
        logging.info(link1_text)
        logging.info(link2_text)
        logging.info(link3_text)

        # If any test fails, exit with code 1
        if not (link1_result and link2_result and link3_result):
            sys.exit(1)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
