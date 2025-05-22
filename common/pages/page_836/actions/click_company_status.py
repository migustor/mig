# /projects/ag_eu/pages/page_836/actions/click_company_status.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from projects.ag_eu.pages.page_836.locators import Page836Locators

def click_company_status(driver, timeouts=None):
    """
    Clicks the company status edit button in the first row of the table
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger('test')
    logger.info("Attempting to click company status edit button")
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    
    try:
        # Wait for the button to be clickable
        logger.info("Waiting for company status edit button...")
        button = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable(Page836Locators.COMPANY_STATUS_BUTTON)
        )
        
        # Click the button
        logger.info("Clicking company status edit button...")
        button.click()
        
        # Wait a moment for popup to appear
        time.sleep(1)
        
        return {"success": True, "error": None}
            
    except TimeoutException as te:
        error_msg = f"Timeout waiting for company status button: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error clicking company status button: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}