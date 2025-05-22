# common/pages/page_714/actions/check_pallet_data.py
"""
Модуль для проверки данных о паллетах на странице 714.
"""
import logging
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import locators and page info
from common.pages.page_714.page_info import get_page_714_url
from common.pages.page_714.locators import LEAD_HISTORY_ELEMENTS

def check_item_pallet_data(driver, project_code, item_id, timeout=10):
    """
    Переходит на страницу 714 и проверяет данные о паллетах.
    
    Args:
        driver: Selenium WebDriver
        project_code: Код проекта (например, "ho_eu")
        item_id: ID товара для просмотра
        timeout: Таймаут ожидания элементов в секундах
        
    Returns:
        dict: Результат проверки {'success': bool, 'error': str или None, 'pallet_data': str или None}
    """
    logger = logging.getLogger('test')
    logger.info(f"Checking pallet data for item ID: {item_id} on page 714")
    
    try:
        # Generate URL for the item page
        item_url = get_page_714_url(project_code, item_id)
        logger.info(f"Navigating to URL: {item_url}")
        
        # Navigate to the page
        driver.get(item_url)
        time.sleep(3)  # Longer pause to allow page to load completely
        
        # First, make sure we have the main table
        item_table = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(LEAD_HISTORY_ELEMENTS["ITEM_TABLE"])
        )
        logger.info("Found item table on page 714")
        
        # Look for the pallet info using direct XPath
        # This is more reliable than trying to navigate through multiple elements
        pallet_spans = driver.find_elements(By.XPATH, "//span[contains(text(), 'Qty per pallet:')]")
        
        if not pallet_spans:
            # Try alternative approach - look for any span containing "pallet"
            pallet_spans = driver.find_elements(By.XPATH, "//span[contains(text(), 'pallet')]")
            
            if not pallet_spans:
                error_msg = "No 'Qty per pallet' information found on page 714"
                logger.error(error_msg)
                return {"success": False, "error": error_msg, "pallet_data": None}
        
        # Get the text content of the first matching span
        pallet_text = pallet_spans[0].text.strip()
        logger.info(f"Found pallet data on page 714: {pallet_text}")
        
        # Extract the actual pallet quantities using regex
        match = re.search(r'Qty per pallet:\s*(.*)', pallet_text)
        if match:
            pallet_values = match.group(1).strip()
            logger.info(f"Extracted pallet quantities on page 714: {pallet_values}")
            
            # Verify that we have number values in the pallet data
            if re.search(r'\d', pallet_values):
                logger.info(f"Successfully verified pallet quantity data on page 714: {pallet_values}")
                return {"success": True, "error": None, "pallet_data": pallet_values}
            else:
                error_msg = f"Pallet data found on page 714 but contains no numeric values: {pallet_values}"
                logger.warning(error_msg)
                return {"success": False, "error": error_msg, "pallet_data": pallet_values}
        else:
            error_msg = f"Could not extract pallet quantities from text on page 714: {pallet_text}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "pallet_data": None}
            
    except TimeoutException as te:
        error_msg = f"Timeout occurred on page 714: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "pallet_data": None}
        
    except NoSuchElementException as nse:
        error_msg = f"Element not found on page 714: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "pallet_data": None}
        
    except Exception as e:
        error_msg = f"Unexpected error on page 714: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "pallet_data": None}