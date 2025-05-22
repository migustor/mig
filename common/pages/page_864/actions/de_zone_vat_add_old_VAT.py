"""
Action to restore original VAT value
"""
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.pages.page_864.locators import Page864Locators
from common.pages.page_864.page_info import get_page_864_url
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def de_zone_vat_add_old_VAT(driver, project_name, document_id, original_vat):
    """
    Opens the specified document page and restores the original VAT value.
    """
    logger = logging.getLogger('- TEST - OLD VAT')
    logger.info(f"Restoring original VAT value ({original_vat}) for document {document_id} in project {project_name}")
    
    # Generate and navigate to the URL
    url = get_page_864_url(project_name, document_id)
    if not url:
        return {"success": False, "error": f"Could not generate URL for project {project_name}"}
    
    driver.get(url)
    logger.info(f"Navigated to {url}")
    
    # Wait for page to load
    time.sleep(3)
    
    try:
        # Specifically find the VAT input
        vat_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_vat_amount']")
        
        if not vat_input.is_displayed() or not vat_input.is_enabled():
            return {"success": False, "error": "VAT input field is not visible or enabled"}
            
        # Get the element ID for JavaScript operations
        vat_input_id = vat_input.get_attribute("id")
        
        # Get current value
        current_vat = vat_input.get_attribute("value")
        logger.info(f"Current VAT value: {current_vat}")
        
        # Use JavaScript to set the value
        driver.execute_script(f"""
            document.getElementById('{vat_input_id}').value = '{original_vat}';
            const event = new Event('change', {{ bubbles: true }});
            document.getElementById('{vat_input_id}').dispatchEvent(event);
        """)
        logger.info(f"Restored VAT value to {original_vat}")
        
        # Allow some time for the page to process the change
        time.sleep(1)
        
        return {"success": True}
        
    except Exception as e:
        error_msg = f"Error restoring VAT value: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}