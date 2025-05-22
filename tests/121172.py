import os
import shutil  # For directory operations
import time
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service  # For specifying driver path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
)
import pandas as pd

def main():
    # Hardcoded credentials
    URL = 'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=634'  # Replace with your actual URL
    USERNAME = 'victor.moisei@mteam.md'        # Replace with your actual username
    PASSWORD = '12'        # Replace with your actual password

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Set up the download directory
    download_dir = os.path.abspath('downloads')
    os.makedirs(download_dir, exist_ok=True)

    # Add the headless option here
    headless = True  # Set to False if you want to see the browser GUI

    # Configure Chrome options for downloading files
    chrome_options = Options()
    prefs = {
        'download.default_directory': download_dir,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    }
    chrome_options.add_experimental_option('prefs', prefs)

    # Set user agent to desktop browser
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.6668.90 Safari/537.36"
    )
    chrome_options.add_argument(f'user-agent={user_agent}')

    # Add headless argument based on the headless variable
    if headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')  # May be necessary on Windows
        chrome_options.add_argument('--window-size=1920,1080')  # Set window size for headless mode
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--no-sandbox')  # Linux only
        chrome_options.add_argument('--disable-dev-shm-usage')  # Linux only
    else:
        # Set window size for non-headless mode
        chrome_options.add_argument('--start-maximized')

    # Initialize the webdriver with options
    driver = webdriver.Chrome(options=chrome_options)

    # Initialize test status variables
    test_passed = True
    selection_mb_in_system = False
    selection_mb_in_xls = False

    try:
        # Navigate to the URL
        driver.get(URL)
        logging.info("Navigated to URL.")

        # Check if logged in by checking for a known element that only appears after login
        try:
            # Wait for an element that indicates successful login
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.ID, 'date_range_from')  # Adjust this ID if necessary
                )
            )
            logging.info("Already logged in.")
        except TimeoutException:
            # Not logged in, so perform login
            logging.info("Not logged in, proceeding to login.")

            # Find the username and password fields
            logging.info("Locating username and password fields.")
            login_name_field = driver.find_element(By.ID, 'login_name')
            password_field = driver.find_element(By.ID, 'password')

            # Set the username and password using JavaScript
            logging.info("Setting login credentials using JavaScript.")
            driver.execute_script("arguments[0].value = arguments[1];", login_name_field, USERNAME)
            driver.execute_script("arguments[0].value = arguments[1];", password_field, PASSWORD)

            # Optional: Dispatch input events if necessary
            driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", login_name_field)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", password_field)

            # Click the submit button
            logging.info("Clicking the submit button.")
            submit_button = driver.find_element(
                By.XPATH, "//button[@type='submit' and contains(text(), 'Submit')]"
            )
            submit_button.click()

            # Wait for the page to load after login
            logging.info("Waiting for the page to load after login.")
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.ID, 'date_range_from')  # Adjust this ID if necessary
                    )
                )
                logging.info("Login successful.")
            except TimeoutException:
                logging.error("Login failed or took too long.")
                driver.save_screenshot('login_error.png')
                test_passed = False
                driver.quit()
                return

        # Instead of clicking "Show the top 10 open leads", execute the JavaScript code
        logging.info("Setting date range using JavaScript.")

        js_code = """
        (function(){
            // Get the current date
            var currentDate = new Date();
            // Get current year
            var year = currentDate.getFullYear();
            // Get current month index (0-11)
            var monthIndex = currentDate.getMonth();
            // Array of month abbreviations
            var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            var monthAbbr = monthNames[monthIndex];
            // Construct the date string in "DD-MMM-YYYY" format
            var dateString = "01-" + monthAbbr + "-" + year;
            // Parse the date string to a Date object using moment.js
            var dateObj = moment.utc(dateString, "DD-MMM-YYYY").toDate();
            // Set the value of the input field
            document.getElementById('date_range_from').value = dateString;
            // Update the datepicker's internal date value if jQuery and datepicker are available
            if (window.jQuery) {
                jQuery('#date_range_from').datepicker('setDate', dateObj);
                // Trigger the changeDate event to ensure all linked elements update
                jQuery('#input-daterange-date_range').trigger('changeDate');
            }
        })();
        """

        # Execute the JavaScript code in the browser
        driver.execute_script(js_code)
        logging.info("Date range set.")

        # Click the "Submit" button
        logging.info("Clicking the 'Submit' button.")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.search")
        submit_button.click()

        # Wait until the table is visible after clicking "Submit"
        try:
            table_element = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//table[contains(@class, 'table') and contains(@class, 'xvalignmiddle')]")
                )
            )
            logging.info("Table element found and is visible after submitting date range.")
        except TimeoutException:
            logging.error("Timeout while waiting for the table to be visible after submitting date range.")
            driver.save_screenshot('table_loading_error.png')
            test_passed = False
            # Optionally, save page source
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            # Exit the script
            driver.quit()
            return

        # Extract data from the table
        table_html = table_element.get_attribute('outerHTML')
        df_system = pd.read_html(table_html)[0]

        logging.info("Columns found in the system table:")
        logging.info(df_system.columns.tolist())

        # Check if 'Selection MB' column exists in system table
        if 'Selection MB' in df_system.columns:
            selection_mb_in_system = True
            logging.info("'Selection MB' column is present in the system table.")
        else:
            logging.error("'Selection MB' column is missing from the system table.")
            test_passed = False

        # Proceed to export the data
        # Attempt to click the span element if necessary
        try:
            chevron_icon = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@id='search-form']//span[contains(@class, 'glyphicon-chevron-up')]")
                )
            )
            # Scroll the span element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", chevron_icon)
            time.sleep(1)  # Optional wait to ensure the element is in view

            # Hide the interfering menuMobile element if it exists
            menu_mobile = driver.find_elements(By.ID, 'menuMobile')
            if menu_mobile:
                logging.info("menuMobile detected, attempting to hide it.")
                driver.execute_script("arguments[0].style.display = 'none';", menu_mobile[0])
                time.sleep(1)  # Optional wait after hiding the element

            try:
                chevron_icon.click()
                logging.info("Clicked on the chevron icon to expand/collapse the Leads Report panel.")
            except ElementClickInterceptedException:
                logging.warning("Click intercepted, attempting to click via JavaScript.")
                # Attempt JavaScript click
                driver.execute_script("arguments[0].click();", chevron_icon)
        except TimeoutException:
            logging.warning("Chevron icon not found or not needed.")

        # Click on the "Export To Spreadsheet" button
        export_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'export') and contains(., 'Export To Spreadsheet')]")
            )
        )
        export_button.click()
        logging.info("Clicked 'Export To Spreadsheet' button.")

        # Wait until the file is downloaded
        initial_files = set(os.listdir(download_dir))
        timeout = 60  # seconds
        start_time = time.time()
        file_downloaded = False
        downloaded_file = ''

        while time.time() - start_time < timeout:
            current_files = set(os.listdir(download_dir))
            new_files = current_files - initial_files
            for file_name in new_files:
                if file_name.endswith('.xls') or file_name.endswith('.xlsx'):
                    downloaded_file = os.path.join(download_dir, file_name)
                    # Check if the file is fully downloaded
                    if not file_name.endswith('.crdownload'):
                        file_downloaded = True
                        logging.info(f"Downloaded file: {downloaded_file}")
                        break
            if file_downloaded:
                break
            time.sleep(1)

        if not file_downloaded:
            logging.error("Download timed out.")
            test_passed = False
        else:
            # Open the downloaded xls file and read data
            df_xls = pd.read_excel(downloaded_file)

            logging.info("Columns found in the downloaded xls file:")
            logging.info(df_xls.columns.tolist())

            # Check if 'Selection MB' column exists in xls file
            if 'Selection MB' in df_xls.columns:
                selection_mb_in_xls = True
                logging.info("'Selection MB' column is present in the downloaded xls file.")
            else:
                logging.error("'Selection MB' column is missing from the downloaded xls file.")
                test_passed = False

            # Proceed with comparison only if both columns are present
            if selection_mb_in_system and selection_mb_in_xls:
                # Ensure both DataFrames have at least 10 rows
                if len(df_system) >= 10 and len(df_xls) >= 10:
                    df_system_top10 = df_system.head(10).reset_index(drop=True)
                    df_xls_top10 = df_xls.head(10).reset_index(drop=True)

                    def normalize_value(val):
                        if pd.isna(val) or val == '':
                            return None
                        elif isinstance(val, str):
                            # Remove any non-numeric characters
                            val = re.sub(r'[^\d\.\-]', '', val)
                            try:
                                return float(val)
                            except ValueError:
                                return val
                        else:
                            return val

                    comparison_results = []
                    for idx in range(10):
                        val_system = normalize_value(df_system_top10.at[idx, 'Selection MB'])
                        val_xls = normalize_value(df_xls_top10.at[idx, 'Selection MB'])

                        # Handle empty vs 0 case
                        if (val_system is None or val_system == '') and (val_xls == 0 or val_xls == '0$'):
                            match = True
                        else:
                            match = val_system == val_xls

                        comparison_results.append({
                            'Row': idx + 1,
                            'Selection MB_system': val_system,
                            'Selection MB_xls': val_xls,
                            'Match': match
                        })

                    comparison_df = pd.DataFrame(comparison_results)
                    logging.info("Comparison of 'Selection MB' column for the top 10 leads:")
                    logging.info(comparison_df)

                    # Check if all comparisons matched
                    if all(comparison_df['Match']):
                        logging.info("All 'Selection MB' values match for the top 10 leads.")
                    else:
                        logging.error("Mismatch found in 'Selection MB' values.")
                        test_passed = False
                else:
                    logging.error("Not enough rows in one of the tables to compare the top 10 leads.")
                    test_passed = False

    finally:
        # Test Summary
        logging.info("========== TEST SUMMARY ==========")
        if test_passed:
            logging.info("TEST PASSED: The test has successfully ended.")
            logging.info("'Selection MB' column is present in both system and xls files.")
        else:
            logging.error("TEST FAILED: The test did not complete successfully.")
            if not selection_mb_in_system:
                logging.error("Failure Reason: 'Selection MB' column missing from system table.")
            if not selection_mb_in_xls:
                logging.error("Failure Reason: 'Selection MB' column missing from xls file.")
            if not file_downloaded:
                logging.error("Failure Reason: Excel file was not downloaded.")
        logging.info("==================================")

        # Overwrite sensitive data
        USERNAME = None
        PASSWORD = None

        # Clear data structures
        variables_to_clear = [
            'df_system', 'df_xls', 'df_system_top10', 'df_xls_top10',
            'table_html', 'table_element', 'login_name_field',
            'password_field', 'submit_button', 'export_button',
            'comparison_results', 'comparison_df', 'chevron_icon',
            'menu_mobile', 'js_code'
        ]

        for var in variables_to_clear:
            if var in locals():
                exec(f"{var} = None")
                del locals()[var]

        # Delete the downloaded file securely
        if 'downloaded_file' in locals() and os.path.exists(downloaded_file):
            try:
                os.remove(downloaded_file)
                logging.info(f"Deleted downloaded file: {downloaded_file}")
            except Exception as e:
                logging.error(f"Error deleting file {downloaded_file}: {e}")

        # Delete the downloads directory
        if os.path.exists(download_dir):
            try:
                shutil.rmtree(download_dir)
                logging.info(f"Deleted downloads directory: {download_dir}")
            except Exception as e:
                logging.error(f"Error deleting downloads directory {download_dir}: {e}")

        # Close the browser
        driver.quit()

        # Delete driver instance
        driver = None
        del driver

if __name__ == '__main__':
    main()