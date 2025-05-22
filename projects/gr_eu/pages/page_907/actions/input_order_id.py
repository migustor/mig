# projects/gr_eu/pages/page_907/actions/input_order_id.py
import logging
from selenium.common.exceptions import NoSuchElementException

from projects.gr_eu.pages.page_907.locators import Page907Locators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def input_order_id(driver, order_id, timeouts=None):
    """
    Inputs an order ID into the search field
    
    Args:
        driver: Selenium WebDriver
        order_id: The order ID to input
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info(f"Inputting order ID: {order_id}")
    
    try:
        # Find the order ID field
        order_id_field = driver.find_element(*Page907Locators.ORDER_ID_FIELD)
        
        # Clear existing value and input the new order ID
        order_id_field.clear()
        order_id_field.send_keys(str(order_id))
        
        logger.info(f"Successfully input order ID: {order_id}")
        return {"success": True, "error": None}
            
    except NoSuchElementException as nse:
        error_msg = f"Order ID field not found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error inputting order ID: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}