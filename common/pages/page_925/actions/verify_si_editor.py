# /common/pages/page_925/actions/verify_si_editor.py
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from common.utils.error_handling import jenkins_aware

# Import locators
from common.pages.page_925.locators import SI_EDITOR_ELEMENTS
@jenkins_aware()
def verify_si_editor(driver, si_id, timeouts=None, check_for_offers=None):
    """
    Verifies elements on the SI editor page
    
    Args:
        driver: Selenium WebDriver
        si_id: The SI ID being viewed
        timeouts: Dictionary with timeouts for various operations
        check_for_offers: If 'yes', expects to find offers table; if 'no', expects no offers table
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger('test')
    logger.info(f"Verifying SI editor page for SI ID: {si_id}")
    
    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)  # Default to 15 if not specified
    
    try:
        # Verify the URL contains the correct SI ID
        current_url = driver.current_url
        if f"&id={si_id}" in current_url and "&phase=edit" in current_url:
            logger.info(f"Successfully verified SI editor URL: {current_url}")
            
            # If we need to check for offers table
            if check_for_offers is not None:
                try:
                    # Try to find the offers table rows with a short timeout
                    time.sleep(1)  # Brief pause to ensure page is fully loaded
                    
                    # Check for actual data rows
                    offers_rows = driver.find_elements(*SI_EDITOR_ELEMENTS["offers_table_rows"])
                    has_offers_data = len(offers_rows) > 0
                    
                    if has_offers_data:
                        logger.info("Offers table with data found on the page")
                    else:
                        logger.info("No offers table with data found on the page")
                    
                    # Check expectations based on the check_for_offers parameter
                    if check_for_offers.lower() == 'yes' and not has_offers_data:
                        error_msg = "Expected to find offers table with data but none was found"
                        logger.error(error_msg)
                        return {"success": False, "error": error_msg}
                    elif check_for_offers.lower() == 'no' and has_offers_data:
                        error_msg = "Expected no offers table with data but found one"
                        logger.error(error_msg)
                        return {"success": False, "error": error_msg}
                    
                    logger.info(f"Successfully verified offers table condition (check_for_offers={check_for_offers})")
                    
                except Exception as e:
                    error_msg = f"Error checking for offers table: {str(e)}"
                    logger.error(error_msg)
                    return {"success": False, "error": error_msg}
            
            return {"success": True, "error": None}
        else:
            error_msg = f"URL does not match expected SI editor URL: {current_url}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
            
    except TimeoutException as te:
        error_msg = f"Timeout waiting for SI editor elements: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error verifying SI editor page: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}