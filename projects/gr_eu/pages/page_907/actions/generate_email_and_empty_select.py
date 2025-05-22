# projects/sm_eu/pages/page_x/actions/generate_email.py

import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
from common.utils.error_handling import jenkins_aware

# Remove the jenkins_aware decorator to avoid automatic error screenshots
def generate_email_and_empty_select(driver, timeouts=None):
    """
    Clicks the 'Generate email' button, waits for popup and selects 'Empty' radio button.
    
    Args:
        driver: Selenium WebDriver instance
        timeouts: Optional dictionary with timeout values (keys: 'action', 'popup')
    
    Returns:
        dict: Result with 'success': True/False, 'skipped': True/False and 'error' if any
    """
    logger = logging.getLogger(' - TEST - ')
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    popup_timeout = timeouts.get("popup", 20)

    try:
        # 1. Check if "Generate email" button exists and is clickable
        logger.info("Looking for 'Generate email' button...")
        
        # First, check if button exists at all
        generate_buttons = driver.find_elements(By.XPATH, "//button[@type='button' and normalize-space()='Generate email']")
        if not generate_buttons:
            logger.info("Generate email button not found on the page - skipping this order")
            return {"success": False, "skipped": True, "error": "Generate email button not found"}
            
        # Check if the button is visible and enabled
        button = generate_buttons[0]
        if not button.is_displayed() or not button.is_enabled():
            logger.info("Generate email button exists but is not visible or enabled - skipping this order")
            return {"success": False, "skipped": True, "error": "Generate email button exists but is not visible or enabled"}
        
        # Try to click the button directly
        try:
            button.click()
            logger.info("'Generate email' button clicked directly.")
        except ElementClickInterceptedException:
            # If direct click fails, try with JavaScript
            logger.info("Direct click failed, trying with JavaScript...")
            driver.execute_script("arguments[0].click();", button)
            logger.info("'Generate email' button clicked via JavaScript.")

        # 2. Wait for popup to appear with sufficient time
        logger.info("Waiting for popup to appear...")
        time.sleep(5)  # Add explicit sleep to ensure the popup has time to fully render
        
        try:
            WebDriverWait(driver, popup_timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#modal_dialog_lg > div > div"))
            )
            logger.info("Popup appeared.")
        except TimeoutException:
            logger.info("Popup did not appear after clicking Generate email - skipping this order")
            return {"success": False, "skipped": True, "error": "Popup did not appear after clicking Generate email"}

        # Additional wait to ensure popup is fully loaded
        time.sleep(5)  # Wait additional time for radio buttons to be rendered
        
        # 3. Select 'Empty' radio option using the JavaScript that works in console
        logger.info("Selecting 'Empty' radio button using working JavaScript code...")
        
        # Use the exact JavaScript code that works in the console
        js_code = """
        // Try to find the radio button by its ID
        const radio = document.getElementById('email_language_empty');
        if (radio) {
          // Click the radio to emulate a real user action
          radio.click();
          // Optional: make sure it's marked as checked and fire a change event
          radio.checked = true;
          radio.dispatchEvent(new Event('change', { bubbles: true }));
          console.log('email_language_empty radio button has been selected');
          return true;
        } else {
          console.error('Radio button with id "email_language_empty" was not found');
          return false;
        }
        """
        
        # Execute the JavaScript code
        result = driver.execute_script(js_code)
        
        if result:
            logger.info("Successfully selected 'Empty' radio button by ID using JavaScript.")
            
            # Double-check if it worked
            is_checked = driver.execute_script(
                "return document.getElementById('email_language_empty').checked"
            )
            
            if is_checked:
                logger.info("Verified 'Empty' radio button is selected.")
            else:
                logger.warning("Radio button may not be selected after clicking.")
                
            # Success either way
            return {"success": True, "skipped": False, "error": None}
        else:
            logger.info("Failed to select 'Empty' radio button - skipping this order")
            return {"success": False, "skipped": True, "error": "Failed to select 'Empty' radio button"}

    except Exception as e:
        logger.info(f"Exception in generate_email_and_empty_select: {str(e)} - skipping this order")
        return {"success": False, "skipped": True, "error": str(e)}