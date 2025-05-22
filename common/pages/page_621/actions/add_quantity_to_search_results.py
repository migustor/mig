# common/pages/page_621/actions/add_quantity_to_search_results.py
"""
Module for adding quantity to a search result item on page 621.
"""
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from common.pages.page_621.locators import Page621Locators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def add_quantity_to_item(driver, item_id, quantity=2, timeout=10):
    """
    Sets a quantity value for a specific item in search results and clicks the Add button.
    
    Args:
        driver: Selenium WebDriver
        item_id: ID of the item input field (e.g., 'item_35033')
        quantity: Quantity to enter (default: 2)
        timeout: Element wait timeout in seconds
        
    Returns:
        dict: Result of the operation {'success': bool, 'error': str or None}
    """
    logger = logging.getLogger('test')
    logger.info(f"Setting quantity {quantity} for item ID: {item_id} and clicking Add button")
    
    try:
        # Wait for search results container to be present
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "ism_search_results"))
        )
        
        # Найти поле ввода количества
        input_field = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, item_id))
        )
        
        # Очистить поле и ввести новое значение
        input_field.clear()
        input_field.send_keys(str(quantity))
        
        # Найти и нажать кнопку Add
        add_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(Page621Locators.SEARCH_RESULTS_ADD_BUTTON)
        )
        add_button.click()
        
        # Небольшая задержка для обработки запроса
        time.sleep(2)
        
        logger.info(f"Successfully added quantity {quantity} for item {item_id}")
        return {"success": True, "error": None}
        
    except TimeoutException as te:
        error_msg = f"Timeout waiting for elements: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except NoSuchElementException as nse:
        error_msg = f"Element not found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Unexpected error when adding item quantity: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}