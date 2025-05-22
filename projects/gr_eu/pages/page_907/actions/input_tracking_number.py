# projects/gr_eu/pages/page_907/actions/input_tracking_number.py
import logging
from selenium.common.exceptions import NoSuchElementException

from projects.gr_eu.pages.page_907.locators import Page907Locators

def input_tracking_number(driver, tracking_number, timeouts=None):
    """
    Inputs a tracking number into the tracking field
    
    Args:
        driver: Selenium WebDriver
        tracking_number: The tracking number to input
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info(f"Inputting tracking number: {tracking_number}")
    
    try:
        # Find the tracking number field
        tracking_field = driver.find_element(*Page907Locators.TRACKING_NUMBER_FIELD)
        
        # Clear existing value and input the new tracking number
        tracking_field.clear()
        tracking_field.send_keys(str(tracking_number))
        
        logger.info(f"Successfully input tracking number: {tracking_number}")
        return {"success": True, "error": None}
            
    except NoSuchElementException as nse:
        error_msg = f"Tracking number field not found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error inputting tracking number: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}