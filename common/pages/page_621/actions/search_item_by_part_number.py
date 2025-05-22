# common/pages/page_621/actions/search_item_by_part_number.py
"""
Module for searching an item by part number on page 621.
"""
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import locators
from common.pages.page_621.locators import Page621Locators

def search_item_by_part_number(driver, part_number, timeout=10):
    """
    Opens the item search panel, enters part number and performs search.
    This function only executes the search operation and confirms the search results are loaded.
    It does not extract or verify any data from search results.
    
    Args:
        driver: Selenium WebDriver
        part_number: Part number to search for
        timeout: Element wait timeout in seconds
        
    Returns:
        dict: Search result {'success': bool, 'error': str or None}
    """
    logger = logging.getLogger('test')
    logger.info(f"Searching for item with part number: {part_number}")
    
    try:
        # Find the panel header
        add_item_panel = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(Page621Locators.ADD_ITEM_PANEL_HEADER)
        )
        
        # Check if panel is already open by looking at the chevron icon
        chevron = add_item_panel.find_element(By.CSS_SELECTOR, ".glyphicon-chevron-up")
        is_open = 'open' in chevron.get_attribute('class')
        
        if not is_open:
            logger.info("Panel is closed, clicking to expand")
            add_item_panel.click()
            # Wait for panel to fully expand
            WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located(Page621Locators.PANEL_BODY)
            )
        else:
            logger.info("'Add New Item' panel is already open")
        
        # Enter part number in the search field
        logger.info(f"Entering part number: {part_number}")
        part_number_input = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(Page621Locators.PART_NUMBER_SEARCH_INPUT)
        )
        part_number_input.clear()
        part_number_input.send_keys(part_number)
        
        # Click the Search button
        logger.info("Clicking Search button")
        search_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(Page621Locators.SEARCH_BUTTON)
        )
        search_button.click()
        
        # Wait for search results to load
        logger.info("Waiting for search results")
        search_results_table = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(Page621Locators.SEARCH_RESULTS_TABLE)
        )
        time.sleep(2)  # Additional wait for table content to load
        
        # Return success since the search has been performed successfully
        return {"success": True, "error": None}
        
    except TimeoutException as te:
        error_msg = f"Timeout occurred during item search: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except NoSuchElementException as nse:
        error_msg = f"Element not found during item search: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Unexpected error during item search: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}