# /common/pages/page_925/actions/submit_form.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Import locators
from common.pages.page_925.locators import FORM_ELEMENTS

def submit_form(driver, timeouts=None):
    """
    Clicks the submit button on page 925
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger('test')
    logger.info("Attempting to submit form on page 925")
    
    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)  # Default to 15 if not specified
    
    try:
        # Wait for the submit button to be clickable
        logger.info("Waiting for submit button...")
        submit_button = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable(FORM_ELEMENTS["submit_button"])
        )
        
        # Click the submit button
        logger.info("Clicking submit button...")
        submit_button.click()
        
        # Wait for the page to reload and the results to appear
        time.sleep(3)
        
        # Return success
        logger.info("Form submitted successfully")
        return {"success": True, "error": None}
            
    except TimeoutException as te:
        error_msg = f"Timeout waiting for submit button: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error submitting form: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}