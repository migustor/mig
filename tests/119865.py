import os
import logging
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configure driver and options
script_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = script_dir  # Path for file downloads
chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument("--headless")

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)  # Wait up to 30 seconds

username = os.getenv('USERNAMEDIM')
password = os.getenv('PASSWORDDIM')

if not username or not password:
    logging.error("Please set the USERNAMEDIM and PASSWORDDIM variables in your .env file")
    driver.quit()
    exit(1)

# Function to log into the system
def login_to_system(login_url):
    try:
        # Navigate to the login page
        driver.get(login_url)
        logging.info(f"Navigated to login page: {login_url}")

        # Enter username and password
        username_field = wait.until(EC.presence_of_element_located((By.ID, "login_name")))
        username_field.clear()
        username_field.send_keys(username)
        logging.info("Username entered.")

        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        logging.info("Password entered.")

        # Click the "Submit" button
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        logging.info("Clicked the login button.")

    except Exception as e:
        logging.error(f"Error during login: {e}", exc_info=True)
        driver.quit()
        exit(1)

# Function to process a system given the login URL and target URL
def process_system(login_url, target_url):
    result = {
        'login_url': login_url,
        'target_url': target_url,
        'ps_number': None,
        'total_qty_on_hand': None,
        'match': None,
        'message': ''
    }
    try:
        # Login to the system
        login_to_system(login_url)

        # Navigate to the target page
        driver.get(target_url)
        logging.info(f"Navigated to target page: {target_url}")

        # Wait until the 'Qty On Hand' cells are present
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.xml15.xpl0.xmt5.xmb5.list-style-none.text-right")))
        logging.info("Found 'Qty On Hand' elements.")

        # Find all 'Qty On Hand' <ul> elements
        qty_on_hand_elements = driver.find_elements(By.CSS_SELECTOR, "ul.xml15.xpl0.xmt5.xmb5.list-style-none.text-right")

        max_ps_number = -1
        max_ps_element = None

        for ul in qty_on_hand_elements:
            qty_text = ul.text.strip()
            ps_number = None
            for line in qty_text.split('\n'):
                line = line.strip()
                if line.startswith("PS:"):
                    ps_value = line[3:].strip()
                    try:
                        ps_number = int(ps_value)
                    except ValueError:
                        ps_number = 0
                    break
            if ps_number is not None:
                if ps_number > max_ps_number:
                    max_ps_number = ps_number
                    max_ps_element = ul

        if max_ps_element is None:
            logging.error("No products found with 'PS:' in 'Qty On Hand' elements.")
            result['message'] = "No products found with 'PS:' in 'Qty On Hand' elements."
            return result  # Exit the function
        else:
            logging.info(f"Product with highest PS number: {max_ps_number}")
            result['ps_number'] = max_ps_number

        # Now find the parent row of max_ps_element
        parent_td = max_ps_element.find_element(By.XPATH, "./ancestor::td[1]")
        parent_tr = parent_td.find_element(By.XPATH, "./ancestor::tr[1]")

        # Within that row, find the 'Tools' cell by locating the cell containing the 'dropdown-hower' class
        tools_cell = parent_tr.find_element(By.XPATH, ".//td[.//div[contains(@class, 'dropdown-hower')]]")

        # Find the dropdown menu in the 'Tools' cell
        dropdown_menu = tools_cell.find_element(By.CSS_SELECTOR, "ul.dropdown-menu")

        # Make the dropdown menu visible via JavaScript
        driver.execute_script("arguments[0].style.display = 'block';", dropdown_menu)

        time.sleep(1)

        # Find the link with title='SPM'
        spm_link = dropdown_menu.find_element(By.XPATH, ".//a[@title='SPM']")

        driver.execute_script("arguments[0].click();", spm_link)
        logging.info("Clicked on the SPM link via JavaScript.")

        # Since the link opens in a new tab, switch to the new window
        time.sleep(2)  # Wait for new window to open
        current_window = driver.current_window_handle
        all_windows = driver.window_handles
        for handle in all_windows:
            if handle != current_window:
                driver.switch_to.window(handle)
                break

        # Wait until the new page is loaded
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        try:
            # Check if the 'Inventory Statistics' content is visible
            content = driver.find_element(By.ID, "inventory_statistics_content")
            if not content.is_displayed():
                # Locate the panel heading for 'Inventory Statistics'
                panel_heading = driver.find_element(By.XPATH, "//div[contains(@class, 'panel-heading') and contains(@class, 'pointer')]/h4[contains(text(), 'Inventory Statistics')]")
                # Click on it via JavaScript to expand the section
                driver.execute_script("arguments[0].click();", panel_heading)
                # Wait for the content to be visible
                wait.until(EC.visibility_of(content))
        except Exception as e:
            logging.error(f"Could not ensure 'Inventory Statistics' section is visible: {e}", exc_info=True)

        # Wait for the 'inventory_statistics' table to be present
        wait.until(EC.presence_of_element_located((By.ID, "inventory_statistics")))

        # Find the 'inventory_statistics' table
        inventory_statistics = driver.find_element(By.ID, "inventory_statistics")

        # Find the table within the 'inventory_statistics' section
        table = inventory_statistics.find_element(By.CSS_SELECTOR, "table.table")

        # Initialize variables
        total_qty_on_hand = None

        # Find all rows in the table body
        table_rows = table.find_elements(By.TAG_NAME, "tr")

        # Loop through the rows to find 'Qty on hand' row
        for row in table_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                row_label = cells[0].text.strip()
                if row_label == "Qty on hand":
                    # Found the 'Qty on hand' row
                    total_cell = cells[-1]  # Use the last cell for 'Total'
                    total_qty_text = total_cell.text.strip()
                    try:
                        total_qty_on_hand = int(total_qty_text)
                        result['total_qty_on_hand'] = total_qty_on_hand
                    except ValueError:
                        result['message'] = f"Could not convert '{total_qty_text}' to integer."
                    break  # No need to process further rows

        if total_qty_on_hand is not None:
            # Compare with the PS number
            result['match'] = (total_qty_on_hand == max_ps_number)
        else:
            result['message'] = "Could not find the total Qty on hand value on SPM page."

        # Close the SPM tab and switch back to the main window
        driver.close()
        driver.switch_to.window(current_window)

        # Clear cookies to prepare for next login
        driver.delete_all_cookies()

    except Exception as e:
        logging.error(f"An error occurred while processing the system: {e}", exc_info=True)
        result['message'] = str(e)
    finally:
        return result

# Main script execution
results = []

try:
    # RA system
    ra_login_url = "https://stage15.office.ratrading.eu/sage/?logout"
    ra_target_url = "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=621&phase=edit&lead_id=120602"

    result = process_system(ra_login_url, ra_target_url)
    results.append(result)

    # SMUSA system
    smusa_login_url = "https://stage15.office.sovamaxusa.com/sage/?logout"
    smusa_target_url = "https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=621&phase=edit&lead_id=8301"

    result = process_system(smusa_login_url, smusa_target_url)
    results.append(result)

    # SMEU system
    smeu_login_url = "https://stage15.office.sovasystem.com/sage/?logout"
    smeu_target_url = "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=621&phase=edit&lead_id=204001"

    result = process_system(smeu_login_url, smeu_target_url)
    results.append(result)

    # AG system
    ag_login_url = "https://stage15.office.agavasystem.com/sage/?logout"
    ag_target_url = "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=621&phase=edit&lead_id=9600"

    result = process_system(ag_login_url, ag_target_url)
    results.append(result)

except Exception as e:
    logging.error(f"An error occurred in the main script: {e}", exc_info=True)

finally:
    logging.info("\n==== TEST SUMMARY ====")
    error_detected = False

    for result in results:
        if result['match'] is None:
            logging.error(f"Processing of URL {result['target_url']} failed: {result['message']}")
            error_detected = True
        elif result['match']:
            logging.info(f"For URL {result['target_url']}: PS number {result['ps_number']} matches Total Qty on hand from SPM page {result['total_qty_on_hand']}.")
        else:
            logging.warning(f"For URL {result['target_url']}: PS number {result['ps_number']} does NOT match Total Qty on hand from SPM page {result['total_qty_on_hand']}.")

    if error_detected:
        sys.exit(1)

    # Close the driver after a delay
    time.sleep(5)
    driver.quit()
    logging.info("Driver closed.")
