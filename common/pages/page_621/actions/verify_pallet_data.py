# common/pages/page_621/actions/verify_pallet_data.py
"""
Модуль для проверки данных о паллетах в таблице лидов на странице 621.
"""
import logging
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import locators
from common.pages.page_621.locators import Page621Locators

def verify_pallet_quantity_data(driver, timeout=10):
    """
    Проверяет наличие данных о количестве на паллете в таблице лидов и извлекает ID товара и партномер.
    
    Args:
        driver: Selenium WebDriver
        timeout: Таймаут ожидания элементов в секундах
        
    Returns:
        dict: Результат проверки {'success': bool, 'error': str или None, 
                                'pallet_data': str или None, 'item_id': str или None, 
                                'part_number': str или None}
    """
    logger = logging.getLogger('test')
    logger.info("Verifying pallet quantity data in lead items table")
    
    try:
        # Wait for the table to be loaded
        table = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(Page621Locators.LEAD_ITEMS_TABLE)
        )
        
        # Find the "Qty per pallet" span element
        pallet_spans = driver.find_elements(*Page621Locators.QTY_PER_PALLET_SPAN)
        
        if not pallet_spans:
            error_msg = "No 'Qty per pallet' information found in the table"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "pallet_data": None, "item_id": None, "part_number": None}
        
        # Get the text content of the first matching span
        pallet_text = pallet_spans[0].text.strip()
        logger.info(f"Found pallet data: {pallet_text}")
        
        # Extract the actual pallet quantities using regex
        match = re.search(r'Qty per pallet:\s*(.*)', pallet_text)
        if match:
            pallet_values = match.group(1).strip()
            logger.info(f"Extracted pallet quantities: {pallet_values}")
            
            # Extract item ID from the history link
            item_id = extract_item_id(driver, timeout)
            if not item_id:
                logger.warning("Could not extract item ID from the table")
            else:
                logger.info(f"Extracted item ID: {item_id}")
            
            # Extract part number
            part_number = extract_part_number(driver, timeout)
            if not part_number:
                logger.warning("Could not extract part number from the table")
            else:
                logger.info(f"Extracted part number: {part_number}")
            
            # Verify that we have number values in the pallet data
            if re.search(r'\d', pallet_values):
                logger.info(f"Successfully verified pallet quantity data: {pallet_values}")
                return {
                    "success": True, 
                    "error": None, 
                    "pallet_data": pallet_values,
                    "item_id": item_id,
                    "part_number": part_number
                }
            else:
                error_msg = f"Pallet data found but contains no numeric values: {pallet_values}"
                logger.warning(error_msg)
                return {
                    "success": False, 
                    "error": error_msg, 
                    "pallet_data": pallet_values,
                    "item_id": item_id,
                    "part_number": part_number
                }
        else:
            error_msg = f"Could not extract pallet quantities from text: {pallet_text}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "pallet_data": None, "item_id": None, "part_number": None}
            
    except TimeoutException as te:
        error_msg = f"Timeout occurred waiting for lead items table: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "pallet_data": None, "item_id": None, "part_number": None}
        
    except NoSuchElementException as nse:
        error_msg = f"Table element not found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "pallet_data": None, "item_id": None, "part_number": None}
        
    except Exception as e:
        error_msg = f"Unexpected error during pallet data verification: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "pallet_data": None, "item_id": None, "part_number": None}

def extract_item_id(driver, timeout=10):
    """
    Извлекает ID товара из ссылки истории товара.
    
    Args:
        driver: Selenium WebDriver
        timeout: Таймаут ожидания элементов в секундах
        
    Returns:
        str: ID товара или None, если не удалось извлечь
    """
    logger = logging.getLogger('test')
    try:
        # Find the link to item history
        history_links = driver.find_elements(*Page621Locators.ITEM_HISTORY_LINK)
        
        if not history_links:
            logger.warning("No item history links found in the table")
            return None
            
        # Extract item ID from the first history link's href attribute
        link_href = history_links[0].get_attribute('href')
        
        # Use regex to extract the item_id parameter
        match = re.search(r'item_id=(\d+)', link_href)
        if match:
            return match.group(1)
        else:
            logger.warning(f"Could not extract item_id from link: {link_href}")
            return None
            
    except Exception as e:
        logger.error(f"Error extracting item ID: {str(e)}")
        return None

def extract_part_number(driver, timeout=10):
    """
    Извлекает партномер товара из таблицы.
    
    Args:
        driver: Selenium WebDriver
        timeout: Таймаут ожидания элементов в секундах
        
    Returns:
        str: Партномер товара или None, если не удалось извлечь
    """
    logger = logging.getLogger('test')
    try:
        # Find the strong element containing the part number
        part_number_elements = driver.find_elements(*Page621Locators.PART_NUMBER_STRONG)
        
        if not part_number_elements:
            logger.warning("No part number elements found in the table")
            return None
        
        # Get the text from the first matching element
        for element in part_number_elements:
            part_number = element.text.strip()
            if part_number:  # If we found a non-empty part number
                return part_number
                
        logger.warning("Part number element found but text is empty")
        return None
            
    except Exception as e:
        logger.error(f"Error extracting part number: {str(e)}")
        return None