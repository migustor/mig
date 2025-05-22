"""
Action to navigate to lead history for a specific item
"""
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Import locators
from common.pages.page_714.locators import LEAD_HISTORY_ELEMENTS

def navigate_to_lead_history(driver, url, timeouts=None):
    """
    Navigates to lead history page and opens the history view
    
    Args:
        driver: Selenium WebDriver
        url: URL of the lead history page
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger('test')
    logger.info(f"Navigating to lead history: {url}")
    
    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    navigation_timeout = timeouts.get("navigation", {}).get("page_load", 30)
    dropdown_timeout = timeouts.get("navigation", {}).get("dropdown", 35)
    history_button_timeout = timeouts.get("navigation", {}).get("history_button", 35)
    history_table_timeout = timeouts.get("navigation", {}).get("history_table", 35)
    
    try:
        # Navigate to the lead history page
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, navigation_timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.info("Page fully loaded")
        time.sleep(3)  # Additional time for AJAX
        
        # Select "All" option from the date range dropdown
        logger.info(f"Waiting for date dropdown element")
        dropdown = WebDriverWait(driver, dropdown_timeout).until(
            EC.presence_of_element_located(LEAD_HISTORY_ELEMENTS["date_diff_dropdown"])
        )
        
        dropdown.find_element(*LEAD_HISTORY_ELEMENTS["dropdown_option_all"]).click()
        time.sleep(2)
        
        # Click the history button to open history view
        logger.info(f"Waiting for history button element")
        history_button = WebDriverWait(driver, history_button_timeout).until(
            EC.element_to_be_clickable(LEAD_HISTORY_ELEMENTS["history_button"])
        )
        
        history_button.click()
        
        # Wait for history table to load
        time.sleep(5)
        
        # Verify history table is present with rows
        logger.info(f"Waiting for history table row element")
        WebDriverWait(driver, history_table_timeout).until(
            EC.presence_of_element_located(LEAD_HISTORY_ELEMENTS["history_table_row"])
        )
        
        time.sleep(3)  # Extra time for full loading
        
        logger.info("Successfully navigated to lead history")
        return {"success": True, "error": None}
        
    except TimeoutException as te:
        error_msg = f"Timeout during navigation to lead history: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error during navigation to lead history: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}