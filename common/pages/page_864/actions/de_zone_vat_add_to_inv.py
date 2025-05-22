"""
Action to add VAT amount to Invoice Net amount for German zone VAT checking
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
def de_zone_vat_add_to_inv(driver, project_name, document_id, original_vat):
    """
    Opens the specified document page, gets the Invoice Net amount,
    adds the original VAT value to it, and sets the new total as the Invoice Net amount.
    """
    logger = logging.getLogger('- TEST - ADD VAT TO INV NET')
    logger.info(f"Adding VAT to Invoice Net for document {document_id} in project {project_name}")
    
    # Generate and navigate to the URL
    url = get_page_864_url(project_name, document_id)
    if not url:
        return {"success": False, "error": f"Could not generate URL for project {project_name}"}
    
    driver.get(url)
    logger.info(f"Navigated to {url}")
    
    # Wait for page to load
    time.sleep(3)
    
    try:
        # Specifically find the Invoice Net input (not the VAT input)
        inv_net_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_net_amount']")
        
        if not inv_net_input.is_displayed() or not inv_net_input.is_enabled():
            return {"success": False, "error": "Invoice Net input field is not visible or enabled"}
            
        # Get the element ID for JavaScript operations
        inv_net_input_id = inv_net_input.get_attribute("id")
        
        # Get original Invoice Net value
        original_inv_net = inv_net_input.get_attribute("value")
        logger.info(f"Original Invoice Net value: {original_inv_net}")
        
        # Convert to float and add with original VAT
        try:
            inv_net_float = float(original_inv_net.replace(',', ''))
            original_vat_float = float(original_vat.replace(',', ''))
            new_inv_net = inv_net_float + original_vat_float
            new_inv_net_str = f"{new_inv_net:.2f}"
            logger.info(f"New Invoice Net calculation: {inv_net_float} + {original_vat_float} = {new_inv_net}")
        except ValueError as ve:
            error_msg = f"Error converting values to float: {str(ve)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Use JavaScript to set the value
        driver.execute_script(f"""
            document.getElementById('{inv_net_input_id}').value = '{new_inv_net_str}';
            const event = new Event('change', {{ bubbles: true }});
            document.getElementById('{inv_net_input_id}').dispatchEvent(event);
        """)
        logger.info(f"Set Invoice Net value to {new_inv_net_str}")
        
        # Allow some time for the page to process the change
        time.sleep(1)
        
        return {
            "success": True, 
            "original_inv_net": original_inv_net
        }
        
    except Exception as e:
        error_msg = f"Error updating Invoice Net: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}