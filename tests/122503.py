from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Start Chrome in full screen
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Set URL, login credentials
url = "https://stage5.office.sovasystem.com/sage/index.cfm?page_id=903&phase=edit&id=15041"
username = "valeriu.bistritchi@mteam.md"
password = "F9e361a12589"

# Open URL
driver.get(url)
logging.info("Opened the target URL for login.")

try:
    # Login
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login_name"))).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    logging.info("Logged in successfully.")

    # Wait for documents to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@id='inv_attached']")))
    logging.info("Waiting for documents to load after login.")

    # Wait for processing to start then click Process/Parse
    time.sleep(3)

    # Execute JavaScript to click Process/Parse button for DHL document
    js_code = """
    const buttons = document.querySelectorAll('a[onclick]');
    buttons.forEach(button => {
        if (button.getAttribute('onclick').includes('DHL_31_10_2024.pdf')) {
            button.click();
            console.log("Process/Parse button clicked!");
        }
    });
    """
    driver.execute_script(js_code)
    logging.info("Executed JavaScript to locate and click the Process/Parse button.")

    # Wait for processing to start after clicking Process/Parse
    time.sleep(3)

    # Initialize variables to capture and count AJAX requests
    ajax_request_count = 0
    start_time = time.time()

    # Check for AJAX requests related to parsing with JavaScript logging
    while True:
        time.sleep(1)
        requests = driver.execute_script("return performance.getEntriesByType('resource');")
        
        # Filter requests for parsing-specific AJAX calls and count them
        ajax_requests = [
            req for req in requests 
            if "index.cfm?page_id=903&phase=get_parsed_invoice" in req['name']
        ]
        ajax_request_count = len(ajax_requests)

        # If no more new AJAX requests appear for a few seconds, break the loop
        if ajax_request_count > 0 and (time.time() - start_time) > 5:
            break

    # Log the final AJAX request count
    logging.info(f"Processing completed. Number of AJAX requests made: {ajax_request_count}")

finally:
    driver.quit()
    logging.info("Browser closed.")
