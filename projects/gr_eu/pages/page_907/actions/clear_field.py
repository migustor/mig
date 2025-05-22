# projects/gr_eu/pages/page_907/actions/clear_field.py
import logging
from selenium.common.exceptions import NoSuchElementException

def clear_field(driver, locator, field_name, timeouts=None):
    """
    Clears a specific input field
    
    Args:
        driver: Selenium WebDriver
        locator: Tuple of (By.X, "locator string")
        field_name: Name of the field for logging purposes
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info(f"Clearing {field_name} field")
    
    try:
        # Find the field
        field = driver.find_element(*locator)
        
        # Clear the field
        field.clear()
        
        logger.info(f"Successfully cleared {field_name} field")
        return {"success": True, "error": None}
            
    except NoSuchElementException as nse:
        error_msg = f"{field_name} field not found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error clearing {field_name} field: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}