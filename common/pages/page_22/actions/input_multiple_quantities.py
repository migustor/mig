# common/pages/page_22/actions/input_multiple_quantities.py
import logging
import time
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import locators for the page
from common.pages.page_22.locators import Page22Locators

def input_multiple_quantities(driver, timeout=10):
    """
    Inputs random unique values into multiple quantity_per_pallet fields on page ID=22.
    Steps:
    1. Input value in first field
    2. Click 'add new Qty per Pallet' button
    3. Input unique value in second field
    4. Click 'add new Qty per Pallet' button again
    5. Input unique value in third field
    
    Args:
        driver: Selenium WebDriver
        timeout (int): Maximum time to wait for elements
        
    Returns:
        dict: Result of the action {'success': bool, 'error': str or None, 'values': list}
    """
    logger = logging.getLogger('test')
    logger.info("Starting input of multiple quantity per pallet values")
    
    # Will store the generated values for verification later
    quantity_values = []
    
    # Helper function to generate a unique random value
    def generate_unique_value():
        possible_values = list(range(1, 11))  # Values from 1 to 10
        
        # Remove already used values from the possible values
        for used_value in quantity_values:
            if used_value in possible_values:
                possible_values.remove(used_value)
        
        # If all values have been used (unlikely with just 3 inputs), return a random one
        if not possible_values:
            return random.randint(1, 10)
            
        # Return a random value from the remaining possible values
        return random.choice(possible_values)
    
    try:
        # Step 1: Input value in first field
        value1 = generate_unique_value()
        quantity_values.append(value1)
        
        logger.info(f"Inputting first quantity value: {value1}")
        input_field1 = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(Page22Locators.QUANTITY_PER_PALLET_INPUT_1)
        )
        input_field1.clear()
        input_field1.send_keys(str(value1))
        time.sleep(0.5)
        
        # Step 2: Click 'add new Qty per Pallet' button
        logger.info("Clicking add new quantity button")
        add_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(Page22Locators.ADD_NEW_QUANTITY_BUTTON)
        )
        add_button.click()
        time.sleep(1)  # Wait for new field to appear
        
        # Step 3: Input unique value in second field
        value2 = generate_unique_value()
        quantity_values.append(value2)
        
        logger.info(f"Inputting second quantity value: {value2}")
        input_field2 = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(Page22Locators.QUANTITY_PER_PALLET_INPUT_2)
        )
        input_field2.clear()
        input_field2.send_keys(str(value2))
        time.sleep(0.5)
        
        # Step 4: Click 'add new Qty per Pallet' button again
        logger.info("Clicking add new quantity button again")
        add_button.click()
        time.sleep(1)  # Wait for new field to appear
        
        # Step 5: Input unique value in third field
        value3 = generate_unique_value()
        quantity_values.append(value3)
        
        logger.info(f"Inputting third quantity value: {value3}")
        input_field3 = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(Page22Locators.QUANTITY_PER_PALLET_INPUT_3)
        )
        input_field3.clear()
        input_field3.send_keys(str(value3))
        time.sleep(0.5)
        
        logger.info(f"Successfully entered all quantity values: {quantity_values}")
        return {"success": True, "error": None, "values": quantity_values}
        
    except TimeoutException as te:
        error_msg = f"Timeout when interacting with quantity fields: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "values": quantity_values}
        
    except NoSuchElementException as nse:
        error_msg = f"Could not find element when inputting quantities: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "values": quantity_values}
        
    except Exception as e:
        error_msg = f"Unexpected error when inputting multiple quantities: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "values": quantity_values}