# common/pages/page_621/actions/verify_search_result_data.py
"""
Module for verifying item description and pallet quantity in search results on page 621.
"""
import logging
import re
from selenium.common.exceptions import NoSuchElementException

# Import locators
from common.pages.page_621.locators import Page621Locators

def verify_search_result_data(driver):
    """
    Verifies item description and extracts/validates pallet quantity data
    from already loaded search results.
    
    This function assumes that search has already been performed and search results
    are currently displayed on the page.
    
    Args:
        driver: Selenium WebDriver
        
    Returns:
        dict: Verification result {'success': bool, 'error': str or None, 
                               'pallet_data': str or None}
    """
    logger = logging.getLogger('test')
    logger.info("Verifying search result data")
    
    try:
        # Verify item description
        try:
            item_description = driver.find_element(*Page621Locators.SEARCH_RESULT_ITEM_DESCRIPTION).text
            logger.info(f"Found item: {item_description}")
        except NoSuchElementException:
            logger.warning("Item description not found in search results")
        
        # Find the "Qty per pallet" span in search results
        pallet_spans = driver.find_elements(*Page621Locators.SEARCH_RESULT_QTY_PER_PALLET_SPAN)
        
        if not pallet_spans:
            error_msg = "No 'Qty per pallet' information found in search results"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "pallet_data": None}
        
        # Get the text content of the first matching span
        pallet_text = pallet_spans[0].text.strip()
        logger.info(f"Found pallet data in search results: {pallet_text}")
        
        # Extract the actual pallet quantities using regex
        match = re.search(r'Qty per pallet:\s*(.*)', pallet_text)
        if match:
            pallet_values = match.group(1).strip()
            logger.info(f"Extracted pallet quantities from search results: {pallet_values}")
            
            # Verify that we have number values in the pallet data
            if re.search(r'\d', pallet_values):
                logger.info(f"Successfully verified pallet quantity data in search results: {pallet_values}")
                return {"success": True, "error": None, "pallet_data": pallet_values}
            else:
                error_msg = f"Pallet data found in search results but contains no numeric values: {pallet_values}"
                logger.warning(error_msg)
                return {"success": False, "error": error_msg, "pallet_data": pallet_values}
        else:
            error_msg = f"Could not extract pallet quantities from text in search results: {pallet_text}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "pallet_data": None}
                
    except NoSuchElementException as nse:
        error_msg = f"Element not found during verification of search results: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "pallet_data": None}
        
    except Exception as e:
        error_msg = f"Unexpected error during verification of search results: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "pallet_data": None}