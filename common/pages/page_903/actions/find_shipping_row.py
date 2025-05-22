# common/pages/page_903/actions/find_shipping_row.py
import logging
from selenium.common.exceptions import NoSuchElementException

from common.pages.page_903.locators import Page903Locators

def find_shipping_cost_row(driver, timeouts=None):
    """
    Finds all shipping cost inputs in the table
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status, shipping inputs and error message if any
    """
    logger = logging.getLogger('test')
    logger.info("Looking for all shipping cost inputs in the table")
    
    try:
        # Find all shipping cost inputs directly, regardless of row
        all_shipping_inputs = driver.find_elements(*Page903Locators.SHIPPING_COST_INPUTS)
        
        if all_shipping_inputs:
            logger.info(f"Found {len(all_shipping_inputs)} shipping cost inputs in total")
            return {
                "success": True, 
                "error": None,
                "shipping_inputs": all_shipping_inputs
            }
        else:
            logger.warning("No shipping cost inputs found in the table")
            return {"success": False, "error": "No shipping_cost fields found", "shipping_inputs": []}
            
    except NoSuchElementException as nse:
        error_msg = f"Error finding shipping cost inputs: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "shipping_inputs": []}
        
    except Exception as e:
        error_msg = f"Error finding shipping cost inputs: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "shipping_inputs": []}