import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from typing import Dict
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestResults:
    def __init__(self, site_name: str):
        self.site_name = site_name
        self.results = {
            "site_name": site_name,
            "login_status": False,
            "actions": {
                "success_button": False,
                "company_autocomplete": False,
                "quantity_input": False,
                "price_input": False,
                "plus_button": False
            },
            "final_element": {
                "found": False,
                "value": None,
                "expected_value": None
            },
            "timing": {
                "start_time": None,
                "end_time": None,
                "duration": None
            },
            "context": {
                "target_column": None
            }
        }

def setup_driver():
    """Setup and return Chrome WebDriver with proper headless configuration"""
    logging.info("Setting up the Chrome driver")
    options = webdriver.ChromeOptions()

    # Headless mode configuration
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument("--force-device-scale-factor=1")

    # Additional headers for better rendering
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--enable-javascript")

    return webdriver.Chrome(options=options)

def login(driver, site_config: dict, results: TestResults) -> bool:
    """Perform login on the website with improved error handling"""
    logging.info(f"Attempting to login to {results.site_name} as {site_config['username']}")
    try:
        driver.get(site_config['url'])

        # Wait for login form with increased timeout
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "login_name"))
        )
        password_input = driver.find_element(By.ID, "password")

        # Clear fields before entering credentials
        username_input.clear()
        username_input.send_keys(site_config['username'])
        password_input.clear()
        password_input.send_keys(site_config['password'])

        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()

        # Increased wait time for page load after login
        time.sleep(10)

        # Wait for table with increased timeout
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table'))
            )
            logging.info(f"Table loaded successfully on {results.site_name}")
        except:
            logging.warning(f"Initial table load timeout on {results.site_name}, waiting additional time")
            time.sleep(10)

        results.results["login_status"] = True
        logging.info(f"Login successful on {results.site_name}")
        return True

    except Exception as e:
        logging.error(f"Login failed on {results.site_name}: {str(e)}")
        results.results["login_status"] = False
        return False

def perform_actions(driver, results: TestResults, site_config: dict) -> bool:
    """Perform all required actions with improved error handling and retries"""
    try:
        # Increased initial wait time
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, 0)")

        logging.info(f"[{results.site_name}] Starting search for 'Qty Reserved' column")

        # Enhanced table waiting logic with multiple attempts
        max_attempts = 3
        attempt = 0
        table = None

        while attempt < max_attempts:
            try:
                # Wait for table with increased timeout
                table = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table'))
                )

                # Check for headers
                header_elements = table.find_elements(By.TAG_NAME, 'th')
                if header_elements:
                    logging.info(f"[{results.site_name}] Table headers found successfully")
                    break
                else:
                    logging.info(f"[{results.site_name}] Table found but headers not loaded, attempt {attempt + 1}")
                    time.sleep(5)
            except TimeoutException:
                logging.warning(f"[{results.site_name}] Table not found on attempt {attempt + 1}")

            attempt += 1
            if attempt < max_attempts:
                driver.refresh()
                time.sleep(5)

        if not table or not header_elements:
            logging.error(f"[{results.site_name}] Failed to load table with headers after {max_attempts} attempts")
            return False

        # Find target column
        target_column_index = None
        for index, header in enumerate(header_elements, 1):
            header_text = header.text.strip()
            logging.info(f"[{results.site_name}] Checking header {index}: '{header_text}'")
            if "Qty Reserved" in header_text:
                target_column_index = index
                results.results["context"]["target_column"] = index
                logging.info(f"[{results.site_name}] Found 'Qty Reserved' column at position {index}")
                break

        if not target_column_index:
            logging.error(f"[{results.site_name}] Column 'Qty Reserved' not found in the table")
            return False

        # Find and click success button
        try:
            target_cell = driver.find_element(
                By.CSS_SELECTOR,
                f'tr:nth-child(1) td:nth-child({target_column_index})'
            )

            success_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'button.btn.btn-success.pull-right.btn-xs.text-uppercase.z-depth-1'
                ))
            )

            # Ensure button is visible and clickable
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", success_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", success_button)
            results.results["actions"]["success_button"] = True
            logging.info(f"[{results.site_name}] Successfully clicked success button")

        except Exception as e:
            logging.error(f"[{results.site_name}] Failed to interact with success button: {str(e)}")
            return False

        # Fill company autocomplete with retries
        max_autocomplete_attempts = 3
        for attempt in range(max_autocomplete_attempts):
            try:
                logging.info(f"[{results.site_name}] Filling company autocomplete with value {site_config['autocomplete_value']} (attempt {attempt + 1})")
                company_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#offer_company_autocompleter'))
                )
                company_input.clear()
                company_input.send_keys(site_config['autocomplete_value'])

                time.sleep(2)  # Wait for autocomplete options

                autocomplete_option = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        f'li[data-value="{site_config["autocomplete_value"]}"]'
                    ))
                )
                autocomplete_option.click()
                results.results["actions"]["company_autocomplete"] = True
                break
            except Exception as e:
                if attempt == max_autocomplete_attempts - 1:
                    logging.error(f"[{results.site_name}] Failed to fill company autocomplete after {max_autocomplete_attempts} attempts: {str(e)}")
                    return False
                time.sleep(2)

        # Fill quantity
        try:
            logging.info(f"[{results.site_name}] Filling quantity")
            quantity_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#quantity'))
            )
            quantity_input.clear()
            quantity_input.send_keys("1")
            results.results["actions"]["quantity_input"] = True

        except Exception as e:
            logging.error(f"[{results.site_name}] Failed to fill quantity: {str(e)}")
            return False

        # Fill price
        try:
            logging.info(f"[{results.site_name}] Filling price")
            price_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input.form-control.input_price_format'))
            )
            price_input.clear()
            price_input.send_keys("122")
            results.results["actions"]["price_input"] = True

        except Exception as e:
            logging.error(f"[{results.site_name}] Failed to fill price: {str(e)}")
            return False

        # Click plus button
        try:
            logging.info(f"[{results.site_name}] Clicking plus button")
            plus_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.fas.fa-plus-square'))
            )
            plus_button.click()
            time.sleep(2)
            results.results["actions"]["plus_button"] = True
            return True

        except Exception as e:
            logging.error(f"[{results.site_name}] Failed to click plus button: {str(e)}")
            return False

    except Exception as e:
        logging.error(f"[{results.site_name}] Unexpected error during actions: {str(e)}")
        return False

def check_final_element(driver, results: TestResults) -> str:
    """Check the final element value with improved error handling"""
    try:
        logging.info(f"[{results.site_name}] Looking for final element")

        column_number = results.results["context"]["target_column"]
        time.sleep(2)

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                selector = f'tr:nth-child(1) td:nth-child({column_number}) tr:last-child td:nth-child(4)'
                final_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )

                element_text = final_element.text.strip()
                logging.info(f"[{results.site_name}] Found final element. Content: {element_text}")

                results.results["final_element"]["found"] = True
                results.results["final_element"]["value"] = element_text
                return element_text

            except Exception as e:
                if attempt == max_attempts - 1:
                    logging.error(f"[{results.site_name}] Final element not found after {max_attempts} attempts: {str(e)}")
                    break
                time.sleep(2)

        results.results["final_element"]["found"] = False
        return None

    except Exception as e:
        logging.error(f"[{results.site_name}] Error checking final element: {str(e)}")
        results.results["final_element"]["found"] = False
        return None

def test_site(site_config: dict, max_retries: int = 3) -> TestResults:
    """Test a single site with retry mechanism"""
    results = TestResults(site_config['name'])
    attempt = 1

    while attempt <= max_retries:
        driver = None
        try:
            logging.info(f"[{site_config['name']}] Starting attempt {attempt}/{max_retries}")
            results.results["timing"]["start_time"] = time.time()
            driver = setup_driver()

            # Login attempt
            if not login(driver, site_config, results):
                logging.warning(f"[{site_config['name']}] Login failed on attempt {attempt}")
                raise Exception("Login failed")

            # Perform actions
            if not perform_actions(driver, results, site_config):
                logging.warning(f"[{site_config['name']}] Actions failed on attempt {attempt}")
                raise Exception("Actions failed")

            # Check final element
            element_content = check_final_element(driver, results)
            if not element_content:
                logging.warning(f"[{site_config['name']}] Final element check failed on attempt {attempt}")
                raise Exception("Final element check failed")

            logging.info(f"[{site_config['name']}] Test completed successfully on attempt {attempt}")
            break  # Success - exit the retry loop

        except Exception as e:
            logging.error(f"[{site_config['name']}] Error on attempt {attempt}: {str(e)}")

            if attempt == max_retries:
                logging.error(f"[{site_config['name']}] All retry attempts exhausted")
            else:
                logging.info(f"[{site_config['name']}] Will retry in 5 seconds...")
                time.sleep(5)

        finally:
            if driver:
                results.results["timing"]["end_time"] = time.time()
                results.results["timing"]["duration"] = (
                    results.results["timing"]["end_time"] -
                    results.results["timing"]["start_time"]
                )
                driver.quit()
                logging.info(f"Browser closed for {site_config['name']} on attempt {attempt}")

        attempt += 1

    return results

def generate_test_summary(results: TestResults) -> str:
    """Generate a summary of the test execution"""
    summary = f"\n=== {results.site_name.upper()} TEST EXECUTION SUMMARY ===\n"

    # Login Status
    summary += "\nLogin Status:\n"
    icon = "[+]" if results.results["login_status"] else "[-]"
    summary += f"{icon} Authentication: {'Successful' if results.results['login_status'] else 'Failed'}\n"

    # Actions Status
    summary += "\nActions Status:\n"
    for action, status in results.results["actions"].items():
        icon = "[+]" if status else "[-]"
        action_name = action.replace("_", " ").title()
        summary += f"{icon} {action_name}: {'Success' if status else 'Failed'}\n"

    # Final Element Status
    summary += "\nFinal Element Status:\n"
    if results.results["final_element"]["found"]:
        summary += f"[+] Element Found: Yes\n"
        summary += f"[+] Element Value: {results.results['final_element']['value']}\n"

        if results.results["final_element"]["expected_value"]:
            is_match = results.results["final_element"]["value"] == results.results["final_element"]["expected_value"]
            icon = "[+]" if is_match else "[-]"
            summary += f"{icon} Value Match: {'Yes' if is_match else 'No'}\n"
            if not is_match:
                summary += f"    Expected: {results.results['final_element']['expected_value']}\n"
                summary += f"    Actual: {results.results['final_element']['value']}\n"
    else:
        summary += "[-] Element Found: No\n"

    # Test Duration
    if results.results["timing"]["duration"]:
        summary += f"\nTest Duration: {results.results['timing']['duration']:.2f} seconds\n"

    summary += "\n=================\n"
    return summary

def main():
    # Configuration for sites with specific autocomplete values
    sites_config = [
        {
            "name": "Ra Trading",
            "url": "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=972&id=2212&action=edit",
            "username": "maxim.lupan@mteam.md",
            "password": "12",
            "autocomplete_value": "188759"
        },
        {
            "name": "Agava Trading",
            "url": "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=972&id=92&action=edit",
            "username": "maxim.lupan@mteam.md",
            "password": "12",
            "autocomplete_value": "188759"
        },
        {
            "name": "SM USA",
            "url": "https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=972&id=42&action=edit",
            "username": "maxim.lupan@mteam.md",
            "password": "12",
            "autocomplete_value": "526928"
        },
        {
            "name": "SM EU",
            "url": "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=972&id=1544&action=edit",
            "username": "maxim.lupan@mteam.md",
            "password": "12",
            "autocomplete_value": "492730"
        },
        {
            "name": "Lanius",
            "url": "https://stage15.office.laniustoys.com/sage/index.cfm?page_id=972&id=3847&action=edit",
            "username": "maxim.lupan@mteam.md",
            "password": "12",
            "autocomplete_value": "157665"
        },
        {
            "name": "dbR",
            "url": "https://stage15.office.dbreactor.com/sage/index.cfm?page_id=972&id=1184&action=edit",
            "username": "maxim.lupan@mteam.md",
            "password": "12",
            "autocomplete_value": "1557"
        },
        {
            "name": "Horus",
            "url": "https://stage15.office.horustrading.eu/sage/index.cfm?page_id=972&id=235&action=edit",
            "username": "maxim.lupan@mteam.md",
            "password": "12",
            "autocomplete_value": "46282"
        },
        {
            "name": "Atlas",
            "url": "https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=972&id=8&action=edit",
            "username": "maxim.lupan@mteam.md",
            "password": "12",
            "autocomplete_value": "1557"
        },
        {
            "name": "Argon",
            "url": "https://stage15.office.argontrading.de/sage/index.cfm?page_id=972&id=1&action=edit",
            "username": "maxim.lupan@mteam.md",
            "password": "12",
            "autocomplete_value": "123"
        }
    ]

    all_results = []
    has_failures = False

    for site_config in sites_config:
        max_retries = site_config.get("max_retries", 3)  # Default to 3 retries if not specified
        results = test_site(site_config, max_retries)
        all_results.append(results)

        # Check for failures
        if not results.results["login_status"]:
            has_failures = True
        for action_status in results.results["actions"].values():
            if not action_status:
                has_failures = True
        if not results.results["final_element"]["found"]:
            has_failures = True

    print("\n=== COMPLETE TEST RESULTS ===")
    for results in all_results:
        summary = generate_test_summary(results)
        print(summary)

    if has_failures:
        sys.exit(1)  # Exit with error code for Jenkins
    sys.exit(0)      # Exit with success code

if __name__ == "__main__":
    main()
