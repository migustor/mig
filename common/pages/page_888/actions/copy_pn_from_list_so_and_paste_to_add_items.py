"""
Action to copy a part number from a sales order list and paste it into the 'Add More Items' panel search field.
"""
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import locators
from common.pages.page_888.locators import Page888Locators

def copy_pn_from_list_so_and_paste_to_add_items(driver, row_index=1, timeout=15):
    """
    Copies the first part number from the specified row in the SO list and pastes it
    into the 'Add More Items' panel search field.
    
    Args:
        driver: Selenium WebDriver
        row_index: Index of the row to copy from (1-based index as it's XPath)
        timeout: Timeout for waiting for elements (seconds)
        
    Returns:
        dict: Result of the operation {'success': bool, 'error': str or None, 'part_number': str or None}
    """
    logger = logging.getLogger('test')
    logger.info(f"Attempting to copy part number from row {row_index} and paste to Add More Items")
    
    try:
        # 1. Find the part number cell based on row index
        part_number_cells = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located(Page888Locators.PART_NUMBER_CELL)
        )
        
        if row_index > len(part_number_cells):
            error_msg = f"Row index {row_index} exceeds available rows ({len(part_number_cells)})"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "part_number": None}
        
        # Get the cell at the specified index (adjusting for zero-based indexing)
        part_number_cell = part_number_cells[row_index - 1]
        
        # Find the bold part number within the cell
        part_number_element = part_number_cell.find_element(*Page888Locators.PART_NUMBER_BOLD)
        
        # Extract the text (without the comma)
        part_number = part_number_element.text.rstrip(',')
        logger.info(f"Found part number: {part_number}")
        
        # 2. Click on "Add More Items" to open the panel
        add_items_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(Page888Locators.ADD_MORE_ITEMS_BUTTON)
        )
        add_items_button.click()
        logger.info("Clicked on 'Add More Items' button")
        
        # 3. Wait for the search textarea to be available
        search_textarea = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(Page888Locators.SEARCH_TEXTAREA)
        )
        
        # 4. Clear the textarea and paste the part number
        search_textarea.clear()
        search_textarea.send_keys(part_number)
        logger.info(f"Entered part number '{part_number}' into search field")
        
        # 5. Click the search button
        search_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(Page888Locators.SEARCH_BUTTON)
        )
        search_button.click()
        logger.info("Clicked the search button")
        
        # Wait for search results to appear (use fixed time instead of waiting for specific elements)
        time.sleep(5)
        
        return {
            "success": True,
            "error": None,
            "part_number": part_number
        }
        
    except TimeoutException as e:
        error_msg = f"Timeout waiting for element: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "part_number": None}
        
    except NoSuchElementException as e:
        error_msg = f"Element not found: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "part_number": None}
        
    except Exception as e:
        error_msg = f"Error copying part number and searching: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "part_number": None}