# common/pages/page_22/actions/clear_quantity_fields.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import locators for the page
from common.pages.page_22.locators import Page22Locators

def clear_quantity_fields(driver, timeout=10):
    """
    Clears all quantity_per_pallet input fields on page ID=22.
    
    Args:
        driver: Selenium WebDriver
        timeout (int): Maximum time to wait for elements
        
    Returns:
        dict: Result of the action {'success': bool, 'error': str or None, 'cleared_count': int}
    """
    logger = logging.getLogger('test')
    logger.info("Attempting to clear all quantity per pallet fields")
    
    try:
        # Find all quantity input fields using the common class
        logger.info("Finding all quantity input fields...")
        quantity_fields = driver.find_elements(*Page22Locators.ALL_QUANTITY_INPUTS)
        
        cleared_count = 0
        # Clear each field
        for field in quantity_fields:
            try:
                field.clear()
                cleared_count += 1
                logger.info(f"Cleared field: {field.get_attribute('id')}")
                time.sleep(0.2)  # Small pause between operations
            except Exception as e:
                logger.warning(f"Could not clear field {field.get_attribute('id')}: {str(e)}")
        
        logger.info(f"Successfully cleared {cleared_count} quantity fields")
        return {"success": True, "error": None, "cleared_count": cleared_count}
        
    except TimeoutException as te:
        error_msg = f"Timeout when trying to clear quantity fields: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "cleared_count": 0}
        
    except NoSuchElementException as nse:
        error_msg = f"Could not find quantity fields to clear: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "cleared_count": 0}
        
    except Exception as e:
        error_msg = f"Unexpected error when clearing quantity fields: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "cleared_count": 0}