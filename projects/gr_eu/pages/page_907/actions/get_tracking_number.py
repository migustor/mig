# projects/gr_eu/pages/page_907/actions/get_tracking_number.py
import logging
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_tracking_number(driver, locator, tracking_type="first", timeouts=None):
    """
    Gets the tracking number text from the specified element
    
    Args:
        driver: Selenium WebDriver
        locator: Tuple of (By.X, "locator string")
        tracking_type: Description of which tracking number (for logging)
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status, tracking number and error message if any
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info(f"Getting {tracking_type} tracking number")
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    
    try:
        # Wait for the tracking number element to be visible
        tracking_element = WebDriverWait(driver, action_timeout).until(
            EC.visibility_of_element_located(locator)
        )
        
        # Get the text value
        tracking_number = tracking_element.text.strip()
        
        if not tracking_number:
            error_msg = f"{tracking_type} tracking number is empty"
            logger.warning(error_msg)
            return {"success": False, "error": error_msg, "tracking_number": None}
        
        logger.info(f"Successfully found {tracking_type} tracking number: {tracking_number}")
        return {"success": True, "error": None, "tracking_number": tracking_number}
            
    except NoSuchElementException as nse:
        error_msg = f"{tracking_type} tracking number element not found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "tracking_number": None}
        
    except Exception as e:
        error_msg = f"Error getting {tracking_type} tracking number: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "tracking_number": None}