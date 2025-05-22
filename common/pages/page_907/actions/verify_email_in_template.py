"""
Action to click Generate Template button and verify email address in template
"""
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import locators from locators file
from common.pages.page_907.locators import Page907Locators

logger = logging.getLogger('test')

def click_generate_template_and_verify_email(driver, expected_business_email, wait_time=10):
    """
    Clicks the 'Generate template' button, waits for modal to open, and verifies email
    
    Args:
        driver: Selenium WebDriver instance
        expected_business_email: The business email expected to be found in the template
        wait_time: Maximum time to wait for elements (in seconds)
        
    Returns:
        dict: Result of verification {'success': bool, 'email_found': str or None, 'matches': bool}
    """
    try:
        logger.info("Looking for Generate template button")
        # Wait for and click the Generate Template button
        template_button = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable(Page907Locators.TEMPLATE_BUTTON)
        )
        logger.info("Clicking Generate template button")
        template_button.click()
        
        # Wait for modal to appear
        logger.info("Waiting for template modal window to open")
        WebDriverWait(driver, wait_time).until(
            EC.visibility_of_element_located(Page907Locators.MODAL_WINDOW)
        )
        
        # Allow some time for modal content to fully load
        time.sleep(1)
        
        # Look for email address span
        logger.info("Looking for email address in template")
        email_span = WebDriverWait(driver, wait_time).until(
            EC.visibility_of_element_located(Page907Locators.EMAIL_SPAN)
        )
        
        # Get the email address from the span
        email_found = email_span.text.strip()
        logger.info(f"Found email in template: {email_found}")
        
        # Verify that it matches the expected business email
        matches = email_found == expected_business_email
        if matches:
            logger.info(f"Email in template matches expected business email: {expected_business_email}")
        else:
            logger.warning(f"Email mismatch! Expected: {expected_business_email}, Found: {email_found}")
        
        return {
            "success": True,
            "email_found": email_found,
            "matches": matches
        }
        
    except TimeoutException as e:
        logger.error(f"Timeout waiting for element: {str(e)}")
        return {"success": False, "error": f"Timeout error: {str(e)}", "email_found": None, "matches": False}
        
    except NoSuchElementException as e:
        logger.error(f"Element not found: {str(e)}")
        return {"success": False, "error": f"Element not found: {str(e)}", "email_found": None, "matches": False}
        
    except Exception as e:
        logger.error(f"Error while verifying email in template: {str(e)}")
        return {"success": False, "error": str(e), "email_found": None, "matches": False}