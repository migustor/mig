"""
Action to restore original Invoice Net value
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
def de_zone_vat_add_old_inv_net(driver, project_name, document_id, original_inv_net):
    """
    Opens the specified document page and restores the original Invoice Net value.
    """
    logger = logging.getLogger('- TEST - OLD INV NET')
    logger.info(f"Restoring original Invoice Net value ({original_inv_net}) for document {document_id} in project {project_name}")
    
    # Generate and navigate to the URL
    url = get_page_864_url(project_name, document_id)
    if not url:
        return {"success": False, "error": f"Could not generate URL for project {project_name}"}
    
    driver.get(url)
    logger.info(f"Navigated to {url}")
    
    # Wait for page to load
    time.sleep(3)
    
    try:
        # Specifically find the Invoice Net input
        inv_net_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_net_amount']")
        
        if not inv_net_input.is_displayed() or not inv_net_input.is_enabled():
            return {"success": False, "error": "Invoice Net input field is not visible or enabled"}
            
        # Get the element ID for JavaScript operations
        inv_net_input_id = inv_net_input.get_attribute("id")
        
        # Get current value
        current_inv_net = inv_net_input.get_attribute("value")
        logger.info(f"Current Invoice Net value: {current_inv_net}")
        
        # Use JavaScript to set the value
        driver.execute_script(f"""
            document.getElementById('{inv_net_input_id}').value = '{original_inv_net}';
            const event = new Event('change', {{ bubbles: true }});
            document.getElementById('{inv_net_input_id}').dispatchEvent(event);
        """)
        logger.info(f"Restored Invoice Net value to {original_inv_net}")
        
        # Allow some time for the page to process the change
        time.sleep(1)
        
        return {"success": True}
        
    except Exception as e:
        error_msg = f"Error restoring Invoice Net value: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}