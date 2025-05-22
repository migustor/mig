# projects/gr_eu/pages/page_907/actions/wait_for_element.py
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def wait_for_element(driver, locator, timeout=30, condition=EC.visibility_of_element_located, description="element"):
    """
    Wait for an element to satisfy a specific condition
    
    Args:
        driver: Selenium WebDriver
        locator: Tuple of (By.X, "locator string")
        timeout: Maximum time to wait in seconds
        condition: Expected condition to wait for (from selenium.webdriver.support.expected_conditions)
        description: Description of the element for logging purposes
        
    Returns:
        dict: Result of the action with success status and element if found
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info(f"Waiting for {description} with locator {locator} to appear...")
    
    try:
        element = WebDriverWait(driver, timeout).until(
            condition(locator)
        )
        logger.info(f"Successfully found {description}")
        
        return {"success": True, "error": None, "element": element}
            
    except TimeoutException as te:
        error_msg = f"Timeout waiting for {description}: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "element": None}
        
    except Exception as e:
        error_msg = f"Error while waiting for {description}: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "element": None}