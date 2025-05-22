# projects/gr_eu/pages/page_907/actions/wait_for_results.py
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from projects.gr_eu.pages.page_907.locators import Page907Locators

def wait_for_results(driver, timeouts=None):
    """
    Waits for the search results container to appear
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info("Waiting for search results to appear")
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    page_load_timeout = timeouts.get("page_load", 30)
    
    try:
        # Wait for the results container to be visible
        WebDriverWait(driver, page_load_timeout).until(
            EC.visibility_of_element_located(Page907Locators.RESULT_CONTAINER)
        )
        
        logger.info("Search results loaded successfully")
        return {"success": True, "error": None}
            
    except TimeoutException as te:
        error_msg = f"Timeout waiting for search results: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error waiting for search results: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}