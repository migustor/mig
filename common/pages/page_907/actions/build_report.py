# projects/gr_eu/pages/page_907/actions/build_report.py
import logging
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from projects.gr_eu.pages.page_907.locators import Page907Locators

def build_report(driver, timeouts=None):
    """
    Clicks the 'Build Report' button
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger('test')
    logger.info("Clicking 'Build Report' button")
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    
    try:
        # Wait for the button to be clickable
        button = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable(Page907Locators.BUILD_REPORT_BUTTON)
        )
        
        # Click the button
        button.click()
        
        logger.info("Successfully clicked 'Build Report' button")
        return {"success": True, "error": None}
            
    except NoSuchElementException as nse:
        error_msg = f"Build Report button not found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    
    except ElementClickInterceptedException as eci:
        error_msg = f"Build Report button could not be clicked: {str(eci)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error clicking Build Report button: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}