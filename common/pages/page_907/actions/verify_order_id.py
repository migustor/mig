# projects/gr_eu/pages/page_907/actions/verify_order_id.py
import logging
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from projects.gr_eu.pages.page_907.locators import Page907Locators

def verify_order_id(driver, expected_order_id, timeouts=None):
    """
    Verifies that the final order ID displayed matches the expected value
    
    Args:
        driver: Selenium WebDriver
        expected_order_id: The expected order ID to verify against
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the verification with success status, actual ID and match result
    """
    logger = logging.getLogger('test')
    logger.info(f"Verifying final order ID matches expected: {expected_order_id}")
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    
    try:
        # Wait for the order ID element to be visible
        order_element = WebDriverWait(driver, action_timeout).until(
            EC.visibility_of_element_located(Page907Locators.FINAL_ORDER_LINK)
        )
        
        # Get the text value
        actual_order_id = order_element.text.strip()
        
        # Check if it matches the expected ID
        matches = actual_order_id == str(expected_order_id)
        
        if matches:
            logger.info(f"Verification successful: Final order ID {actual_order_id} matches expected {expected_order_id}")
        else:
            logger.warning(f"Verification failed: Final order ID {actual_order_id} does NOT match expected {expected_order_id}")
        
        return {
            "success": True, 
            "error": None, 
            "actual_order_id": actual_order_id,
            "matches": matches
        }
            
    except NoSuchElementException as nse:
        error_msg = f"Final order ID element not found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "actual_order_id": None, "matches": False}
        
    except Exception as e:
        error_msg = f"Error verifying final order ID: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "actual_order_id": None, "matches": False}