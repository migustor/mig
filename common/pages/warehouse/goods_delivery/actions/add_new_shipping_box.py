import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from common.utils.error_handling import jenkins_aware
from common.pages.warehouse.locators import WarehouseLocators

@jenkins_aware()
def add_new_shipping_box(driver, dimensions=None, carrier_name="DHL", project_name=None, wait_timeout=30):
    """
    Adds a new shipping box in the shipping popup and verifies the warning message appears.
    
    Args:
        driver: Selenium WebDriver (already switched to the iframe)
        dimensions: Dictionary with width, length, height, weight values (defaults to 10 for all)
        carrier_name: Name of the carrier to select (default "DHL")
        project_name: Project code to apply project-specific logic (e.g., 'ra_eu', 'sm_eu')
        wait_timeout: Maximum wait time in seconds
        
    Returns:
        dict: Result with success status and details
    """
    logger = logging.getLogger('test')
    logger.info("Starting to add a new shipping box")
    
    # Get locators from the class
    NEW_BOX_ELEMENTS = WarehouseLocators.NEW_BOX_ELEMENTS
    
    # Default dimensions if not provided
    if dimensions is None:
        dimensions = {
            "width": "10",
            "length": "10",
            "height": "10",
            "weight": "10"
        }
    
    try:
        # Click the "Add new box" link
        add_new_box_link = WebDriverWait(driver, wait_timeout).until(
            EC.element_to_be_clickable(NEW_BOX_ELEMENTS["add_new_box_link"])
        )
        logger.info("Clicking 'Add new box' link")
        driver.execute_script("arguments[0].click();", add_new_box_link)
        time.sleep(1)  # Wait for the form to appear
        
        # Enter dimensions
        logger.info(f"Entering dimensions: {dimensions}")
        
        # Width
        width_input = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(NEW_BOX_ELEMENTS["width_input"])
        )
        width_input.clear()
        width_input.send_keys(dimensions["width"])
        
        # Length
        length_input = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(NEW_BOX_ELEMENTS["length_input"])
        )
        length_input.clear()
        length_input.send_keys(dimensions["length"])
        
        # Height
        height_input = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(NEW_BOX_ELEMENTS["height_input"])
        )
        height_input.clear()
        height_input.send_keys(dimensions["height"])
        
        # Weight
        weight_input = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(NEW_BOX_ELEMENTS["weight_input"])
        )
        weight_input.clear()
        weight_input.send_keys(dimensions["weight"])
        
        # Select carrier (DHL)
        carrier_select_element = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(NEW_BOX_ELEMENTS["carrier_select"])
        )
        select = Select(carrier_select_element)
        logger.info(f"Selecting carrier: {carrier_name}")
        select.select_by_visible_text(carrier_name)
        time.sleep(2)  # Wait for potential AJAX calls
        
        # Check for the warning message
        try:
            warning_message = WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located(NEW_BOX_ELEMENTS["warning_message"])
            )
            warning_text = warning_message.text
            logger.info(f"Warning message found: {warning_text}")
            
            return {
                "success": True,
                "message": "Successfully added new box and verified warning message",
                "warning_text": warning_text
            }
        except TimeoutException:
            logger.warning("Warning message not found")
            return {
                "success": False,
                "message": "Failed to find expected warning message"
            }
        
    except Exception as e:
        logger.error(f"Error adding new shipping box: {str(e)}")
        return {
            "success": False,
            "message": "Error during adding new shipping box",
            "error": str(e)
        }