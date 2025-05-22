# /projects/at_eu/pages/page_836/actions/close_balance_warning.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from projects.at_eu.pages.page_836.locators import Page836Locators

def close_balance_warning(driver, timeouts=None):
    """
    Closes the balance warning popup by clicking OK button
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger('test')
    logger.info("Attempting to close balance warning popup")
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    
    try:
        # Wait for the OK button to be clickable
        logger.info("Waiting for OK button...")
        ok_button = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable(Page836Locators.POPUP_OK_BUTTON)
        )
        
        # Click the OK button
        logger.info("Clicking OK button...")
        ok_button.click()
        
        # Wait for popup to disappear
        logger.info("Waiting for popup to close...")
        WebDriverWait(driver, action_timeout).until(
            EC.invisibility_of_element_located(Page836Locators.POPUP_CONTAINER)
        )
        
        return {"success": True, "error": None}
            
    except TimeoutException as te:
        error_msg = f"Timeout waiting for OK button or closing popup: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error closing balance warning popup: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}