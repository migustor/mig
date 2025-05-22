"""
Action to verify warning triangles in barcode modals.
"""
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import locators
from common.pages.page_888.locators import Page888Locators

def verify_warning_triangles_in_barcode_modals(driver, timeout=15):
    """
    Checks for warning triangles in both barcode modal windows.
    This action should be called after a part number search has been performed.
    
    Args:
        driver: Selenium WebDriver
        timeout: Timeout for waiting for elements (seconds)
        
    Returns:
        dict: Result of the verification {'success': bool, 'error': str or None,
              'has_warnings_first_modal': bool, 'has_warnings_second_modal': bool}
    """
    logger = logging.getLogger('test')
    logger.info("Starting verification of warning triangles in barcode modals")
    
    try:
        # 1. Click on the get_barcodes link
        get_barcodes_link = None
        try:
            get_barcodes_link = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(Page888Locators.GET_BARCODES_LINK)
            )
            logger.info("Found get_barcodes link")
        except TimeoutException:
            # Execute JavaScript to find and click the link
            logger.info("Trying JavaScript to find get_barcodes link")
            driver.execute_script("document.querySelectorAll('a[onclick^=\"get_barcodes\"]')[0].click();")
        else:
            get_barcodes_link.click()
            
        logger.info("Clicked on get_barcodes link")
        
        # 2. Wait for the modal to appear
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(Page888Locators.MODAL_DIALOG)
        )
        logger.info("Modal opened")
        
        # 3. Check for warning triangles in the first modal
        has_warnings_first_modal = len(driver.find_elements(*Page888Locators.WARNING_TRIANGLE_ICON)) > 0
        logger.info(f"First modal has warning triangles: {has_warnings_first_modal}")
        
        # 4. Close the modal
        close_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(Page888Locators.MODAL_CLOSE_BUTTON)
        )
        close_button.click()
        logger.info("Closed first modal")
        
        # Wait for modal to disappear
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(Page888Locators.MODAL_DIALOG)
        )
        
        # 5. Click on the updateReservedBarcodes link
        update_reserved_link = None
        try:
            update_reserved_link = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(Page888Locators.UPDATE_RESERVED_BARCODES_LINK)
            )
            logger.info("Found updateReservedBarcodes link")
        except TimeoutException:
            # Execute JavaScript to find and click the link
            logger.info("Trying JavaScript to find updateReservedBarcodes link")
            driver.execute_script("document.querySelectorAll('a[onclick^=\"updateReservedBarcodes\"]')[0].click();")
        else:
            update_reserved_link.click()
            
        logger.info("Clicked on updateReservedBarcodes link")
        
        # 6. Wait for the second modal to appear
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(Page888Locators.MODAL_DIALOG)
        )
        logger.info("Second modal opened")
        
        # 7. Check for warning triangles in the second modal
        has_warnings_second_modal = len(driver.find_elements(*Page888Locators.WARNING_TRIANGLE_ICON)) > 0
        logger.info(f"Second modal has warning triangles: {has_warnings_second_modal}")
        
        # 8. Close the second modal
        close_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(Page888Locators.MODAL_CLOSE_BUTTON)
        )
        close_button.click()
        logger.info("Closed second modal")
        
        # Test is successful if warning triangles were found in both modals
        has_warnings = has_warnings_first_modal and has_warnings_second_modal
        success = has_warnings  # Test passes if warning triangles are found
        
        return {
            "success": success,
            "error": None if success else "Warning triangles not found in both modals",
            "has_warnings_first_modal": has_warnings_first_modal,
            "has_warnings_second_modal": has_warnings_second_modal,
            "has_warnings": has_warnings
        }
        
    except TimeoutException as e:
        error_msg = f"Timeout waiting for element: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False, 
            "error": error_msg, 
            "has_warnings_first_modal": False,
            "has_warnings_second_modal": False
        }
        
    except NoSuchElementException as e:
        error_msg = f"Element not found: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False, 
            "error": error_msg,
            "has_warnings_first_modal": False,
            "has_warnings_second_modal": False
        }
        
    except Exception as e:
        error_msg = f"Error during verification: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False, 
            "error": error_msg,
            "has_warnings_first_modal": False,
            "has_warnings_second_modal": False
        }