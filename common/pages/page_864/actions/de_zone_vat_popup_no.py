"""
Action to click 'NO' button in VAT confirmation popup
"""
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def de_zone_vat_popup_no(driver):
    """
    Checks for expected text in the confirmation popup and clicks the 'NO' button.

    Args:
        driver: WebDriver instance

    Returns:
        dict: Result with success status and alert presence information
    """
    logger = logging.getLogger('- TEST - POPUP NO')
    logger.info("Checking alert text and clicking 'NO' button in confirmation popup")
    
    try:
        # Wait before checking
        time.sleep(1)
        
        # Expected text
        expected_text = "The client belongs to the DE zone. VAT must be calculated. Are you sure it's 0.00?"
        
        # Find the modal dialog content
        modal_elements = driver.find_elements(By.CSS_SELECTOR, ".ui-dialog-content")
        alert_present = False
        alert_text = ""
        
        if modal_elements:
            for element in modal_elements:
                if element.is_displayed():
                    alert_text = element.text.strip()
                    if expected_text in alert_text:
                        alert_present = True
                        logger.info("ALERT PRESENT")
                        break
        
        if not alert_present:
            logger.error(f"ALERT WRONG!!!! Text found: '{alert_text}'")
            return {
                "success": False, 
                "error": "Expected alert text not found",
                "alert_present": False,
                "alert_text": alert_text
            }
        
        # Find and click the NO button
        no_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='NO']"))
        )
        no_button.click()
        logger.info("Clicked 'NO' button")
        
        # Wait after clicking
        time.sleep(1)
        
        return {
            "success": True,
            "alert_present": True,
            "alert_text": alert_text
        }
        
    except Exception as e:
        error_msg = f"Error in popup handling: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}