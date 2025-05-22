# common/pages/page_22/actions/save_form.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import locators for the page
from common.pages.page_22.locators import Page22Locators

def save_form(driver, timeout=10):
    """
    Clicks the Save button on page ID=22.
    
    Args:
        driver: Selenium WebDriver
        timeout (int): Maximum time to wait for elements
        
    Returns:
        dict: Result of the action {'success': bool, 'error': str or None}
    """
    logger = logging.getLogger('test')
    logger.info("Attempting to save the form")
    
    try:
        # Wait for and click the save button
        logger.info("Waiting for Save button...")
        save_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(Page22Locators.SAVE_BUTTON)
        )
        save_button.click()
        logger.info("Save button clicked")
        
        # Short pause to let the save operation complete
        time.sleep(2)
        
        return {"success": True, "error": None}
        
    except TimeoutException as te:
        error_msg = f"Timeout during form save operation: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except NoSuchElementException as nse:
        error_msg = f"Could not find element during form save: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Unexpected error during form save: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}