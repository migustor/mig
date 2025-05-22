# /common/pages/page_925/actions/select_yes_offers.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# Import locators
from common.pages.page_925.locators import FORM_ELEMENTS

def select_yes_offers(driver, timeouts=None):
    """
    Selects the 'Yes' radio button for offers condition
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger('test')
    logger.info("Selecting 'Yes' for offers condition")
    
    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)  # Default to 15 if not specified
    
    try:
        # First, try to find the radio button label
        logger.info("Locating Yes radio button label...")
        
        yes_radio_label = WebDriverWait(driver, action_timeout).until(
            EC.presence_of_element_located(FORM_ELEMENTS["has_yes_offers_label"])
        )
        
        # Click the label instead of the input directly (more reliable)
        logger.info("Clicking 'Yes' radio button label...")
        yes_radio_label.click()
        
        # Wait a moment to ensure changes are registered
        time.sleep(1)
        
        # Verify selection by checking the input's checked state
        yes_radio_input = driver.find_element(*FORM_ELEMENTS["has_yes_offers_radio"])
        
        if yes_radio_input.is_selected():
            logger.info("Successfully selected 'Yes' radio button")
            return {"success": True, "error": None}
        else:
            # Try one more direct click on the input if the label click didn't work
            logger.warning("Label click didn't select radio button. Trying direct click...")
            yes_radio_input.click()
            time.sleep(1)
            
            if yes_radio_input.is_selected():
                logger.info("Successfully selected 'Yes' radio button with direct click")
                return {"success": True, "error": None}
            else:
                error_msg = "Failed to select 'Yes' radio button after multiple attempts"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
    except StaleElementReferenceException:
        # If we encounter a stale element, try again with a different approach
        try:
            logger.warning("Encountered stale element. Trying alternative approach...")
            # Using JavaScript to click the radio button
            driver.execute_script("document.getElementById('has_yes_offers').click();")
            time.sleep(1)
            
            # Verify selection
            is_selected = driver.execute_script("return document.getElementById('has_yes_offers').checked;")
            if is_selected:
                logger.info("Successfully selected 'Yes' radio button with JavaScript")
                return {"success": True, "error": None}
            else:
                error_msg = "Failed to select 'Yes' radio button with JavaScript"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
        except Exception as js_e:
            error_msg = f"Error using JavaScript fallback for 'Yes' radio button: {str(js_e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
            
    except TimeoutException as te:
        error_msg = f"Timeout waiting for 'Yes' radio button: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error selecting 'Yes' radio button: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}