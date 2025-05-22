import time
import random
import logging
import os
import glob
import gc
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotInteractableException

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# Systems configuration
systems = [
    {
        'name': 'Sovamax',
        'login_url': 'https://stage15.office.sovasystem.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage15.office.sovasystem.com/sage/index.cfm?page_id=972&id=1502&action=edit'
    },
    {
        'name': 'RA',
        'login_url': 'https://stage15.office.ratrading.eu/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage15.office.ratrading.eu/sage/index.cfm?page_id=972&id=2362&action=edit'
    },
    {
        'name': 'Atlas',
        'login_url': 'https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=972&id=1&action=edit'
    },
    {
        'name': 'Eminia',
        'login_url': 'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=972&id=1235&action=edit'
    },
    {
        'name': 'Lanius',
        'login_url': 'https://stage15.office.laniustoys.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage15.office.laniustoys.com/sage/index.cfm?page_id=972&id=3836&action=edit'
    },
    {
        'name': 'DbReactor',
        'login_url': 'https://stage15.office.dbreactor.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage15.office.dbreactor.com/sage/index.cfm?page_id=972&id=1163&action=edit'
    },
    {
        'name': 'Horus',
        'login_url': 'https://stage15.office.horustrading.eu/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage15.office.horustrading.eu/sage/index.cfm?page_id=972&id=197&action=edit'
    },
    {
        'name': 'ARO',
        'login_url': 'https://stage15.office.arotrading.eu/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage15.office.arotrading.eu/sage/index.cfm?page_id=972&id=2&action=edit'
    },
    {
        'name': 'SovamaxUSA',
        'login_url': 'https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=972&id=33&action=edit'
    },
]

# Common credentials
DEFAULT_USERNAME = os.getenv('DEFAULT_USERNAME')
DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD')

# Sovamax credentials
SOVAMAX_USERNAME = "victor.moisei@mteam.md"
SOVAMAX_PASSWORD = "12"

# Check that credentials are provided
if not DEFAULT_USERNAME or not DEFAULT_PASSWORD:
    logger.error("Please set DEFAULT_USERNAME and DEFAULT_PASSWORD in your .env file.")
    exit(1)

if not SOVAMAX_USERNAME or not SOVAMAX_PASSWORD:
    logger.error("Please set SOVAMAX_USERNAME and SOVAMAX_PASSWORD in your .env file.")
    exit(1)

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = script_dir

# Configure Chrome options to set the download directory
chrome_options = Options()
chrome_prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", chrome_prefs)
chrome_options.add_argument('--start-maximized')

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

def log_in(system):
    try:
        driver.get(system['login_url'])
        logger.info(f"Logging into {system['name']}...")

        # Determine credentials to use
        if system['name'] == 'Sovamax':
            username = SOVAMAX_USERNAME
            password = SOVAMAX_PASSWORD
        else:
            username = DEFAULT_USERNAME
            password = DEFAULT_PASSWORD

        # Log in with credentials
        driver.find_element(By.NAME, 'login_name').send_keys(username)
        driver.find_element(By.NAME, 'password').send_keys(password)
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(@class, "btn btn-info btn-lg")]').click()
        logger.info("Login successful.")
        return True
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False

def direct_action(system):
    df = None
    download_file_name = None
    try:
        # Navigate directly to the specified page
        driver.get(system['notifications_url'])
        logger.info("Navigated to direct page.")

        # Wait for the "Export XLS for Customer" button to appear, then click it
        export_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'btn-success') and contains(text(), 'Export XLS for Customer')]"))
        )
        export_button.click()
        logger.info("'Export XLS for Customer' button clicked.")

        # Wait for the "Export Column settings" header to appear and click it
        export_settings_header = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, '//h6[contains(@class, "d-inline-block") and text()="Export Column settings"]'))
        )
        export_settings_header.click()
        logger.info("'Export Column settings' header clicked.")

        # Verify 'Image Link' column in export settings
        try:
            image_link_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "thumbnail small")]/input[@name="customer_export_list" and @value="image_link"]'))
            )
            logger.info("'Image Link' export column is present.")
        except Exception as e:
            logger.error(f"'Image Link' export column not present: {e}")
            return False

        # Hide the overlapping "Back to top" button if present
        # (This helps avoid element click interception by floating elements)
        driver.execute_script("let backTop = document.getElementById('back-to-top'); if (backTop) { backTop.style.display='none'; }")

        # Click 'Confirm' button to initiate the download
        confirm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "gp-order-status-confirm") and text()="Confirm"]'))
        )
        # Scroll the button into view (center) before clicking
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_button)
        time.sleep(1)  # Allow any final animation or overlap to resolve

        try:
            confirm_button.click()
            logger.info("'Confirm' button clicked.")
        except ElementNotInteractableException:
            # If still not interactable, scroll again or wait
            driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
            time.sleep(1)
            confirm_button.click()
            logger.info("'Confirm' button clicked after scroll.")

        # Track the new .xls file in download directory
        initial_files = set(glob.glob(os.path.join(download_dir, 'presale_effort*.xls')))

        # Wait up to 30 seconds for a new file to appear
        for _ in range(30):
            current_files = set(glob.glob(os.path.join(download_dir, 'presale_effort*.xls')))
            new_files = current_files - initial_files
            if new_files:
                download_file_name = new_files.pop()
                logger.info(f"File downloaded: {download_file_name}")
                break
            time.sleep(1)

        if not download_file_name:
            logger.error("No downloaded XLS file found within the timeout.")
            return False

        # Read the XLS file and verify "Image Link" text in the first row
        df = pd.read_excel(download_file_name, header=None)
        first_row = df.iloc[0].astype(str).tolist()
        if "Image link" in first_row:
            logger.info("'Image Link' text found in the first row of the file.")
        else:
            logger.error("'Image Link' text not found in the first row.")
            return False

        return True
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        driver.save_screenshot('error_screenshot.png')
        return False
    finally:
        # Ensure the DataFrame is closed and memory released
        if df is not None:
            del df
        gc.collect()
        # Delete the downloaded file
        if download_file_name and os.path.exists(download_file_name):
            try:
                os.remove(download_file_name)
                logger.info(f"Deleted downloaded file: {download_file_name}")
            except PermissionError:
                logger.warning(f"File {download_file_name} is in use; will retry during final cleanup.")

def cleanup_downloads_and_memory():
    # Retry logic for deleting all files in download directory
    for file in glob.glob(os.path.join(download_dir, 'presale_effort*.xls')):
        for attempt in range(3):
            try:
                os.remove(file)
                logger.info(f"Deleted file: {file}")
                break
            except PermissionError:
                logger.warning(f"File {file} is in use, retrying ({attempt + 1}/3)...")
                time.sleep(1)

    # Run garbage collection to free up memory
    gc.collect()
    logger.info("Memory cleaned up.")

def main():
    test_results = {}
    for system in systems:
        logger.info(f"\nStarting tests for {system['name']}")
        if log_in(system) and direct_action(system):
            logger.info(f"Tests for {system['name']} passed successfully.")
            test_results[system['name']] = 'Passed'
        else:
            logger.error(f"Tests for {system['name']} failed.")
            test_results[system['name']] = 'Failed'
        driver.delete_all_cookies()  # Clear cookies before next system

    # Summary of test results
    logger.info("\nTest Summary:")
    any_failed = False
    for system_name, result in test_results.items():
        logger.info(f"{system_name}: {result}")
        if result == 'Failed':
            any_failed = True

    # Cleanup downloaded files and memory after all tests
    cleanup_downloads_and_memory()
    driver.quit()

    # If there's a failed test, exit with error code 1
    if any_failed:
        logger.error("Some tests have failed. Exiting with error code 1.")
        exit(1)

if __name__ == "__main__":
    main()
