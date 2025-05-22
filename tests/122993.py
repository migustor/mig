import logging
import sys
import time
import os
import uuid
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Import driver setup functions
from common.utils.driver_setup import setup_chrome_driver, release_driver

TEST_ID = f"122993_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Configure screenshot directory
screenshot_dir = r"J:\PUB5\E2E_Testing"
if not os.path.exists(SCREENSHOT_DIR):
    try:
        os.makedirs(SCREENSHOT_DIR)
    except Exception as e:
        logger.error(f"Failed to create screenshot directory {SCREENSHOT_DIR}: {str(e)}")
        SCREENSHOT_DIR = "screenshots"
        if not os.path.exists(SCREENSHOT_DIR):
            os.makedirs(SCREENSHOT_DIR)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def take_full_page_screenshot(driver, filename_prefix):
    """
    Takes a screenshot of the full page
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SCREENSHOT_DIR, f"{TEST_ID}_{filename_prefix}_{timestamp}.png")
    
    try:
        driver.save_screenshot(filename)
        logger.info(f"Full page screenshot saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to take screenshot: {str(e)}")
        
    return filename

def wait_for_element(driver, locator, by=By.CSS_SELECTOR, timeout=20, condition=EC.presence_of_element_located):
    """
    Wait for an element using fixed timeout
    """
    try:
        logging.info(f"Waiting for element '{locator}' with timeout {timeout}s (attempt 1/10)")
        element = WebDriverWait(driver, timeout).until(condition((by, locator)))
        logging.info(f"Element '{locator}' found after 1 attempt(s)")
        return element
    except TimeoutException:
        logging.error(f"Element '{locator}' not found with timeout {timeout}s")
        return None

def wait_for_page_load(driver, timeout=60):
    """
    Wait for page to fully load
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logging.info("Page fully loaded")
        return True
    except Exception as e:
        logging.error(f"Error waiting for page load: {str(e)}")
        return False

def check_report_results(driver):
    """
    Validate chart, table and data after report submission
    """
    report_results = {
        "chart_present": False,
        "table_present": False,
        "has_data": False
    }

    # Wait for page to load completely
    wait_for_page_load(driver)
    
    try:
        # Check for chart
        chart = wait_for_element(driver, "myChart", By.ID, timeout=45)
        if chart:
            report_results["chart_present"] = True
            logging.info("Chart visualization found and rendered")
        
        # Check for table
        table = wait_for_element(driver, "table-bordered", By.CLASS_NAME, timeout=45)
        if table:
            report_results["table_present"] = True
            logging.info("Results table found")
            
            # Check for data in table
            rows = wait_for_element(
                driver, 
                "table.table-bordered tbody tr:not(.th2)", 
                condition=EC.presence_of_all_elements_located,
                timeout=25
            )
            
            if rows:
                for row in rows[:10]:
                    try:
                        company_cell = row.find_element(By.CSS_SELECTOR, "td a")
                        if company_cell.text:
                            total_span = row.find_element(By.CSS_SELECTOR, "span.text-nowrap")
                            if "€" in total_span.text and not total_span.text.endswith("€ 0.00"):
                                report_results["has_data"] = True
                                logging.info(f"Found data: Company {company_cell.text} with total {total_span.text}")
                                break
                    except Exception:
                        continue
    except Exception as e:
        logging.error(f"Error while checking report results: {str(e)}")
        
    return report_results

def run_test(driver, username, password):
    """
    Run the test with simplified error handling and timeouts
    """
    results = {
        "login_successful": False,
        "page_loaded": False,
        "test_passed": False,
        "radio_buttons": {
            "Creation": {"present": False, "selected": False},
            "Mngr Ready to Ship": {"present": False, "selected": False},
            "Include in KPI": {"present": False, "selected": False}
        }
    }

    try:
        # Login
        logging.info(f"Attempting to login as {username}")
        driver.get("https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=950")
        
        wait_for_page_load(driver)
        
        username_input = wait_for_element(driver, "login_name", By.ID, timeout=18)
        password_input = wait_for_element(driver, "password", By.ID, timeout=15)
        
        if username_input and password_input:
            username_input.send_keys(username)
            password_input.send_keys(password)
            
            submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
            submit_button.click()
            
            # Wait for login form to disappear
            success = WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.ID, "login_name"))
            )
            
            if success:
                results["login_successful"] = True
                logging.info("Login successful")
                
                # Wait for page to load after login
                wait_for_page_load(driver)
                results["page_loaded"] = True
                
                # Check radio buttons
                radio_buttons = {
                    "Creation": "data_creation",
                    "Mngr Ready to Ship": "data_ready_mng",
                    "Include in KPI": "data_include_in_kpi"
                }
                
                for button_name, button_id in radio_buttons.items():
                    radio_button = wait_for_element(driver, button_id, By.ID, timeout=15)
                    if radio_button:
                        results["radio_buttons"][button_name]["present"] = True
                        results["radio_buttons"][button_name]["selected"] = radio_button.is_selected()
                        logging.info(f"Radio button {button_name} checked")
                
                # Submit report
                submit_button = wait_for_element(
                    driver, 
                    "input.btn.btn-primary.submit_report.btns_cer", 
                    timeout=28, 
                    condition=EC.element_to_be_clickable
                )
                
                if submit_button:
                    submit_button.click()
                    logging.info("Clicked submit button")
                    
                    # Wait for results page to load
                    wait_for_page_load(driver)
                    wait_for_page_load(driver) # Multiple checks as seen in logs
                    wait_for_page_load(driver)
                    
                    # Check report results
                    results["report_results"] = check_report_results(driver)
                    
                    # Determine test result
                    results["test_passed"] = (
                        results["radio_buttons"]["Include in KPI"]["selected"] and
                        results["report_results"]["chart_present"] and
                        results["report_results"]["table_present"] and
                        results["report_results"]["has_data"]
                    )
                    
                    if results["test_passed"]:
                        logging.info("Test passed successfully")
                    else:
                        logging.error("Test failed: One or more validations failed")
                        take_full_page_screenshot(driver, "test_failed")
    except Exception as e:
        logging.error(f"Test failed with error: {str(e)}")
        take_full_page_screenshot(driver, "exception")
    
    return results

def test_default_radio_selection(username, password, max_attempts=3):
    """
    Run test with retry capability (simplified)
    """
    attempt = 1
    final_results = None
    
    while attempt <= max_attempts:
        logger.info(f"Starting test attempt {attempt}/{max_attempts}")
        
        # Setup Chrome driver with test ID
        driver = setup_chrome_driver(headless=True, test_id=TEST_ID)
        
        try:
            results = run_test(driver, username, password)
            final_results = results
            
            if results["test_passed"]:
                break
            else:
                logger.warning(f"Test attempt {attempt} failed, will retry" if attempt < max_attempts else "All attempts failed")
        finally:
            # Always release the driver
            release_driver(driver)
        
        attempt += 1
        if attempt <= max_attempts:
            time.sleep(10)  # Wait between attempts
    
    return final_results

if __name__ == "__main__":
    logger.info(f"Starting test execution with ID: {TEST_ID}")
    USERNAME = "maxim.lupan@mteam.md"
    PASSWORD = "12"
    results = test_default_radio_selection(USERNAME, PASSWORD, max_attempts=3)
    
    if not results or not results["test_passed"]:
        logger.error(f"Test {TEST_ID} failed")
        sys.exit(1)
    else:
        logger.info(f"Test {TEST_ID} passed successfully")