# /projects/at_eu/pages/page_836/actions/open_company_link.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from projects.at_eu.pages.page_836.locators import Page836Locators

def open_company_link(driver, timeouts=None):
    """
    Clicks on the company link in the first row, opening it in a new tab
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status, new tab handle and error message if any
    """
    logger = logging.getLogger('test')
    logger.info("Attempting to open company link in a new tab")
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    navigation_timeout = timeouts.get("navigation", 25)
    
    try:
        # Store current window handle
        current_handle = driver.current_window_handle
        current_handles = driver.window_handles
        
        # Wait for the company link to be clickable
        logger.info("Waiting for company link...")
        company_link = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable(Page836Locators.COMPANY_LINK)
        )
        
        # Click the link (it should open in a new tab)
        logger.info("Clicking company link...")
        company_link.click()
        
        # Wait for new tab to open
        logger.info("Waiting for new tab to open...")
        WebDriverWait(driver, navigation_timeout).until(
            lambda d: len(d.window_handles) > len(current_handles)
        )
        
        # Get the new window handle (the new tab)
        new_handles = [handle for handle in driver.window_handles if handle != current_handle]
        if not new_handles:
            raise Exception("No new tab was opened")
        
        new_handle = new_handles[-1]
        
        # Switch to the new tab
        logger.info("Switching to new tab...")
        driver.switch_to.window(new_handle)
        
        # Wait a moment for the page to load
        time.sleep(2)
        
        # Get the URL of the new page
        new_url = driver.current_url
        logger.info(f"Successfully opened company link in new tab. URL: {new_url}")
        
        return {
            "success": True, 
            "error": None,
            "original_handle": current_handle,
            "new_handle": new_handle,
            "url": new_url
        }
            
    except TimeoutException as te:
        error_msg = f"Timeout waiting for company link: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error opening company link: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}