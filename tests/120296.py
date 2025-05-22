import os
import time
import logging
import traceback
import sys
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = script_dir  

# Configure Chrome options
chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
#chrome_options.add_argument('--headless')

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)  # Increased timeout to 30 seconds

# Login credentials
username = "alexandru.rabdau@mteam.md" 
password = "12" 

# List to hold test results
test_results = []

# Variable to hold the result of the show_top field check
show_top_check_result = None

try:
    # Navigate to the login page
    login_url = "https://stage15.office.ratrading.eu/sage/?logout"
    driver.get(login_url)
    logging.info("Navigated to login page.")

    # Log into the system
    username_field = wait.until(EC.presence_of_element_located((By.ID, "login_name")))
    username_field.send_keys(username)
    logging.info("Entered username.")

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)
    logging.info("Entered password.")

    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()
    logging.info("Clicked Submit button.")
    

    # Navigate to the main page
    main_page_url = "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=639"
    driver.get(main_page_url)
    logging.info("Navigated to main page.")

    # Wait for page to load
    time.sleep(2)

    # Function to check if the 'show_top' field is empty
    def check_show_top_field():
        try:
            show_top_field = wait.until(EC.presence_of_element_located((By.ID, "show_top")))
            show_top_value = show_top_field.get_attribute('value').strip()
            if show_top_value == '':
                message = "Show Top is empty."
                logging.info(message)
                return {'status': 'PASSED', 'message': message}
            else:
                message = f"Show Top is not empty. Value: '{show_top_value}'"
                logging.warning(message)
                return {'status': 'FAILED', 'message': message}
        except Exception as e:
            error_message = f"An error occurred while checking 'show_top' field: {type(e).__name__}: {e}"
            logging.error(error_message)
            logging.error("Traceback:")
            logging.error(traceback.format_exc())
            return {'status': 'ERROR', 'message': error_message}

    # Perform the 'show_top' field check once
    show_top_check_result = check_show_top_field()

    # Function to perform tests based on checkbox selections
    def test_columns(show_max_dos=False, show_avg_dos=False):
        test_case_result = {
            'show_max_dos': show_max_dos,
            'show_avg_dos': show_avg_dos,
            'table_errors': [],
            'excel_errors': [],
            'exception': None
        }
        try:
            # Navigate back to the main page to reset the state
            driver.get(main_page_url)
            logging.info("Reloaded the main page.")

            # Wait for page to load
            time.sleep(2)

            # Locate checkboxes and labels
            show_max_dos_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@for='show_max_dos']")))
            show_avg_dos_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@for='show_avg_dos']")))
            show_max_dos_checkbox = driver.find_element(By.ID, "show_max_dos")
            show_avg_dos_checkbox = driver.find_element(By.ID, "show_avg_dos")

            # Set 'Show Max DoS' checkbox
            if show_max_dos:
                if not show_max_dos_checkbox.is_selected():
                    show_max_dos_label.click()
                    logging.info("'Show Max DoS' checkbox selected.")
            else:
                if show_max_dos_checkbox.is_selected():
                    show_max_dos_label.click()
                    logging.info("'Show Max DoS' checkbox deselected.")

            # Set 'Show Avg DoS' checkbox
            if show_avg_dos:
                if not show_avg_dos_checkbox.is_selected():
                    show_avg_dos_label.click()
                    logging.info("'Show Avg DoS' checkbox selected.")
            else:
                if show_avg_dos_checkbox.is_selected():
                    show_avg_dos_label.click()
                    logging.info("'Show Avg DoS' checkbox deselected.")

            # Wait after clicking checkboxes
            time.sleep(1)

            # Click the Search button
            search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and normalize-space(text())='Search']")))
            search_button.click()
            logging.info("Clicked the Search button.")

            # Wait for the table to load
            table_xpath = "//table[contains(@class, 'table-bordered') and contains(@class, 'table-striped') and contains(@class, 'xvalignmiddle')]"
            wait.until(EC.presence_of_element_located((By.XPATH, f"{table_xpath}//th")))
            logging.info("Table loaded.")

            # Retrieve table headers
            headers = driver.find_elements(By.XPATH, f"{table_xpath}//th")
            header_texts = [header.text.strip() for header in headers]
            logging.info(f"Table headers: {header_texts}")

            # Define expected columns based on checkbox selections
            expected_columns = ["Item Image", "Part Number", "Item Info", "BC", "Qty",
                                "Unit Cost", "Total Cost", "Price Offer", "Tools"]
            if show_max_dos:
                expected_columns.append("Max DoS")
            if show_avg_dos:
                expected_columns.append("Avg DoS")

            # Remove duplicates
            expected_columns = list(set(expected_columns))

            # Check for expected columns in the table
            for col in expected_columns:
                count = header_texts.count(col)
                if count > 0:
                    logging.info(f"Column '{col}' is present in the table.")
                    if count > 1:
                        warning_message = f"Column '{col}' appears {count} times in the table headers."
                        logging.warning(warning_message)
                        test_case_result['table_errors'].append(warning_message)
                else:
                    error_message = f"Column '{col}' is missing from the table."
                    logging.error(error_message)
                    test_case_result['table_errors'].append(error_message)

            # Then, click the Export button
            export_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "export_btn")))
            export_button.click()
            logging.info("Clicked the Export button.")

            # Wait for the file to download
            before_download = set(os.listdir(download_dir))
            timeout = 30
            start_time = time.time()
            downloaded_file = None

            while True:
                time.sleep(1)
                after_download = set(os.listdir(download_dir))
                new_files = after_download - before_download
                if new_files:
                    downloaded_file = new_files.pop()
                    if downloaded_file.endswith('.xls') or downloaded_file.endswith('.xlsx'):
                        logging.info(f"Downloaded file: {downloaded_file}")
                        downloaded_file_path = os.path.join(download_dir, downloaded_file)
                        break
                    else:
                        continue  # Ignore non-Excel files
                elif time.time() - start_time > timeout:
                    logging.error("File download timed out.")
                    test_case_result['excel_errors'].append("File download timed out.")
                    return
            time.sleep(2)  # Ensure file writing is complete

            # Check if the file exists and is not empty
            if os.path.exists(downloaded_file_path) and os.path.getsize(downloaded_file_path) > 0:
                logging.info(f"Downloaded file size: {os.path.getsize(downloaded_file_path)} bytes")
                # Read the Excel file and check columns
                try:
                    df = pd.read_excel(downloaded_file_path)
                    excel_columns = df.columns.tolist()
                    logging.info(f"Excel columns: {excel_columns}")
                except Exception as e:
                    error_message = f"Error reading Excel file: {e}"
                    logging.error(error_message)
                    test_case_result['excel_errors'].append(error_message)
                    # Optionally, rename the file for inspection
                    error_file = os.path.join(download_dir, f'error_file_{int(time.time())}.xls')
                    os.rename(downloaded_file_path, error_file)
                    logging.info(f"Renamed the problematic file to: {error_file}")
                    return
            else:
                error_message = "Downloaded file is missing or empty."
                logging.error(error_message)
                test_case_result['excel_errors'].append(error_message)
                return

            # Define expected columns for the Excel report
            expected_excel_columns = ["Item id", "Brand", "Part Number", "Description",
                                      "Box Condition", "Price Offer", "Total QTY", "Unit Cost", "Total Cost"]
            if show_max_dos:
                expected_excel_columns.append("Max DoS")
            if show_avg_dos:
                expected_excel_columns.append("Avg DoS")

            # Check for expected columns in the Excel file
            for col in expected_excel_columns:
                if col in excel_columns:
                    logging.info(f"Column '{col}' is present in the Excel report.")
                else:
                    error_message = f"Column '{col}' is missing from the Excel report."
                    logging.error(error_message)
                    test_case_result['excel_errors'].append(error_message)

            # Clean up the downloaded file
            os.remove(downloaded_file_path)
            logging.info(f"Deleted downloaded file: {downloaded_file_path}")

        except Exception as e:
            error_message = f"An error occurred during test: {type(e).__name__}: {e}"
            logging.error(error_message)
            logging.error("Traceback:")
            logging.error(traceback.format_exc())
            driver.save_screenshot(f'error_screenshot_{int(time.time())}.png')
            test_case_result['exception'] = error_message
        finally:
            test_results.append(test_case_result)

    # Perform tests with different checkbox combinations
    test_columns(show_max_dos=False, show_avg_dos=False)
    test_columns(show_max_dos=True, show_avg_dos=False)
    test_columns(show_max_dos=False, show_avg_dos=True)
    test_columns(show_max_dos=True, show_avg_dos=True)

    # Summarize test results
    logging.info("=== Test Summary ===")
    all_tests_passed = True

    # Include the 'show_top' field check result
    logging.info("Show Top Field Check:")
    if show_top_check_result['status'] == 'PASSED':
        logging.info(f" - {show_top_check_result['message']}")
    elif show_top_check_result['status'] == 'FAILED':
        logging.error(f" - {show_top_check_result['message']}")
        all_tests_passed = False
    else:
        logging.error(f" - {show_top_check_result['message']}")
        all_tests_passed = False

    for idx, result in enumerate(test_results):
        test_description = f"Test {idx+1} with show_max_dos={result['show_max_dos']}, show_avg_dos={result['show_avg_dos']}"
        if result['exception']:
            logging.error(f"{test_description} FAILED due to exception.")
            logging.error(f"Exception: {result['exception']}")
            all_tests_passed = False
        elif result['table_errors'] or result['excel_errors']:
            logging.error(f"{test_description} FAILED with errors.")
            if result['table_errors']:
                logging.error("Table errors:")
                for error in result['table_errors']:
                    logging.error(f" - {error}")
            if result['excel_errors']:
                logging.error("Excel report errors:")
                for error in result['excel_errors']:
                    logging.error(f" - {error}")
            all_tests_passed = False
        else:
            logging.info(f"{test_description} PASSED with no errors, all expected columns were found in HTML and xls file")

    if all_tests_passed:
        logging.info("All tests passed successfully. No problems were detected during testing.")
    else:
        logging.error("Some tests failed. Please see the details above.")
        sys.exit(1)

except Exception as e:
    logging.error(f"An unexpected error occurred: {type(e).__name__}: {e}")
    logging.error("Traceback:")
    logging.error(traceback.format_exc())

finally:
    # Close the WebDriver
    driver.quit()
    logging.info("Closed the browser.")