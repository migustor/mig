# common/pages/page_903/actions/find_shipping_row.py
import logging
from selenium.common.exceptions import NoSuchElementException

from common.pages.page_903.locators import Page903Locators

def find_shipping_cost_row(driver, timeouts=None):
    """
    Finds the first row that contains shipping cost inputs
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status, row element and error message if any
    """
    logger = logging.getLogger('test')
    logger.info("Looking for shipping cost row")
    
    try:
        # Find all table rows
        rows = driver.find_elements(*Page903Locators.SHIPPING_COST_ROW)
        logger.info(f"Found {len(rows)} table rows")
        
        # Check each row for shipping cost inputs
        for row in rows:
            shipping_inputs = row.find_elements(*Page903Locators.SHIPPING_COST_INPUTS)
            if shipping_inputs:
                logger.info(f"Found shipping cost row with {len(shipping_inputs)} shipping cost inputs")
                return {
                    "success": True, 
                    "error": None,
                    "row": row,
                    "shipping_inputs": shipping_inputs
                }
        
        # If we get here, no rows had shipping cost inputs
        logger.warning("No row found with shipping cost inputs")
        return {"success": False, "error": "No row found with shipping_cost fields", "row": None}
            
    except NoSuchElementException as nse:
        error_msg = f"No table rows found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "row": None}
        
    except Exception as e:
        error_msg = f"Error finding shipping cost row: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "row": None}