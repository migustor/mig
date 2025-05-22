# /projects/at_eu/pages/page_836/actions/verify_balance_warning.py
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from projects.at_eu.pages.page_836.locators import Page836Locators

def verify_balance_warning(driver, timeouts=None):
    """
    Verifies that warning popup about non-zero balance appears and has correct text
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the verification with success status, actual text and error message if any
    """
    logger = logging.getLogger('test')
    logger.info("Verifying balance warning popup")
    
    # Expected text in the popup
    expected_text = "Warning.\nNon-zero company balance."
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    
    try:
        # Wait for the popup to be visible
        logger.info("Waiting for warning popup to appear...")
        WebDriverWait(driver, action_timeout).until(
            EC.visibility_of_element_located(Page836Locators.POPUP_CONTAINER)
        )
        
        # Check if warning icon is visible
        warning_icon = WebDriverWait(driver, action_timeout).until(
            EC.visibility_of_element_located(Page836Locators.POPUP_WARNING_ICON)
        )
        
        # Get popup title text
        popup_title = WebDriverWait(driver, action_timeout).until(
            EC.visibility_of_element_located(Page836Locators.POPUP_TITLE)
        )
        
        actual_text = popup_title.text.strip()
        logger.info(f"Found popup text: '{actual_text}'")
        
        # Compare with expected text
        if actual_text == expected_text:
            logger.info("Popup text verification successful")
            return {
                "success": True, 
                "error": None, 
                "actual_text": actual_text,
                "matches": True
            }
        else:
            logger.warning(f"Popup text mismatch. Expected: '{expected_text}', Actual: '{actual_text}'")
            return {
                "success": True,  # Action succeeded but verification failed
                "error": None,
                "actual_text": actual_text,
                "matches": False
            }
            
    except TimeoutException as te:
        error_msg = f"Timeout waiting for balance warning popup: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "actual_text": None, "matches": False}
        
    except Exception as e:
        error_msg = f"Error verifying balance warning popup: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "actual_text": None, "matches": False}