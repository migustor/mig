# common/pages/page_903/workflow/test_domain_workflow.py
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.pages.page_903.actions.login_to_domain import login_to_domain
from common.pages.page_903.locators import Page903Locators
from common.pages.page_903.page_info import get_page_903_url
from common.pages.page_903.actions.test_field_symbols import test_field_symbols

def test_domain_workflow(driver, domain, doc_id, symbols, username, password, timeouts=None):
    """
    Complete workflow to test a domain:
    1. Login to domain
    2. Navigate to page 903 with the specified document ID
    3. Find shipping cost inputs
    4. Test each shipping cost input with special symbols
    5. Test the brokerage field with numeric input and check if ship_cost_diff changes
    
    Args:
        driver: Selenium WebDriver
        domain: Domain to test
        doc_id: Document ID to test
        symbols: Special symbols to test
        username: Username for login
        password: Password for login
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the workflow with success status, details and field test results
    """
    logger = logging.getLogger('test')
    logger.info(f"Starting workflow: test domain {domain} with document ID {doc_id}")
    
    result = {
        "success": False,
        "domain": domain,
        "steps_completed": [],
        "failed_step": None,
        "error": None,
        "fields_tested": {},
        "brokerage_test": {}
    }
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 5)
    page_load_timeout = timeouts.get("page_load", 15)
    
    try:
        # Step 1: Login to domain
        logger.info(f"Step 1: Login to {domain}")
        login_result = login_to_domain(driver, domain, username, password, timeouts)
        if not login_result["success"]:
            result["failed_step"] = "login"
            result["error"] = login_result["error"]
            return result
        
        result["steps_completed"].append("login")
        
        # Step 2: Navigate to page 903
        logger.info(f"Step 2: Navigate to page 903 with document ID {doc_id}")
        try:
            page_url = get_page_903_url(domain, doc_id)
            driver.get(page_url)
            
            # Wait for page to load
            WebDriverWait(driver, page_load_timeout).until(
                EC.presence_of_element_located(Page903Locators.BODY)
            )
            
            logger.info(f"Successfully navigated to page 903. URL: {driver.current_url}")
            result["steps_completed"].append("navigation")
            
        except Exception as e:
            result["failed_step"] = "navigation"
            result["error"] = f"Error navigating to page 903: {str(e)}"
            return result
        
        # Step 3: Find all shipping cost inputs and clear them
        logger.info(f"Step 3: Find shipping cost inputs")
        try:
            # Find all shipping cost inputs by ID or name
            all_shipping_inputs = driver.find_elements(By.CSS_SELECTOR, "input[id*='shipping_cost'], input[name*='shipping_cost']")
            
            if not all_shipping_inputs:
                result["failed_step"] = "find_shipping_inputs"
                result["error"] = "No shipping cost inputs found"
                result["fields_tested"] = "No shipping_cost fields found."
                return result
            
            # Clear all shipping cost inputs first
            logger.info("Clearing all shipping cost fields before testing")
            for input_elem in all_shipping_inputs:
                field_id = input_elem.get_attribute("id") or input_elem.get_attribute("name") or "unknown_id"
                try:
                    initial_value = input_elem.get_attribute("value")
                    input_elem.clear()
                    logger.info(f"Cleared field {field_id} (initial value: {initial_value})")
                except Exception as e:
                    logger.warning(f"Could not clear field {field_id}: {str(e)}")
            
            # Click on an empty part of the screen and wait
            driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(1)
            
            # Get names/IDs of all shipping cost inputs found
            all_field_ids = [input_elem.get_attribute("id") or input_elem.get_attribute("name") or "unknown_id" 
                            for input_elem in all_shipping_inputs]
            
            # Log ALL found shipping cost fields
            logger.info(f"Found ALL shipping cost fields: {all_field_ids}")
            
            # Take only the first 3 inputs (or fewer if less than 3 exist)
            shipping_inputs = all_shipping_inputs[:min(3, len(all_shipping_inputs))]
            test_field_ids = [input_elem.get_attribute("id") or input_elem.get_attribute("name") or "unknown_id" 
                             for input_elem in shipping_inputs]
            
            logger.info(f"Will test the first {len(shipping_inputs)} fields: {test_field_ids}")
            result["steps_completed"].append("find_shipping_inputs")
            
            # Find the brokerage field specifically
            brokerage_fields = [input_elem for input_elem in all_shipping_inputs 
                              if 'brokerage' in (input_elem.get_attribute("id") or '').lower()]
            
            if brokerage_fields:
                brokerage_field = brokerage_fields[0]
                brokerage_id = brokerage_field.get_attribute("id") or brokerage_field.get_attribute("name") or "unknown"
                logger.info(f"Found brokerage field: {brokerage_id}")
                result["brokerage_field_found"] = True
                
                # Extract the order ID and type from the brokerage field ID
                # Format is typically "shipping_cost_brokerage_X_Y" where X is order type and Y is order ID
                if '_' in brokerage_id:
                    id_parts = brokerage_id.split('_')
                    if len(id_parts) >= 5:  # Has enough parts
                        order_type = id_parts[-2]
                        order_id = id_parts[-1]
                        logger.info(f"Extracted order type: {order_type}, order ID: {order_id}")
                        
                        # Look for the corresponding ship_cost_diff element
                        ship_cost_diff_selector = f"span[id*='ship_cost_diff'][id$='_{order_id}'], span[id*='ship_cost_diff'][id$='_{order_type}_{order_id}']"
                        ship_cost_diff_elements = driver.find_elements(By.CSS_SELECTOR, ship_cost_diff_selector)
                        
                        if ship_cost_diff_elements:
                            ship_cost_diff_elem = ship_cost_diff_elements[0]
                            ship_cost_diff_id = ship_cost_diff_elem.get_attribute("id") or "unknown"
                            logger.info(f"Found ship_cost_diff element: {ship_cost_diff_id}")
                            result["ship_cost_diff_found"] = True
                        else:
                            logger.warning(f"No ship_cost_diff element found for order type {order_type}, order ID {order_id}")
                            result["ship_cost_diff_found"] = False
                    else:
                        logger.warning(f"Could not extract order type and ID from brokerage field ID: {brokerage_id}")
                        result["ship_cost_diff_found"] = False
                else:
                    logger.warning(f"Brokerage field ID does not have expected format: {brokerage_id}")
                    result["ship_cost_diff_found"] = False
            else:
                logger.warning("No brokerage field found")
                result["brokerage_field_found"] = False
                result["ship_cost_diff_found"] = False
            
        except Exception as e:
            result["failed_step"] = "find_shipping_inputs"
            result["error"] = f"Error finding shipping cost inputs: {str(e)}"
            return result
        
        # Step 4: Test each shipping cost input
        logger.info(f"Step 4: Test shipping cost inputs with special symbols")
        field_results = {}
        
        for i, input_elem in enumerate(shipping_inputs):
            field_id = input_elem.get_attribute("id") or input_elem.get_attribute("name") or "unknown_id"
            logger.info(f"Testing field #{i+1}: {field_id}")
            
            field_result = test_field_symbols(driver, input_elem, symbols, timeouts)
            field_results[field_id] = field_result
            
            logger.info(f"Field {field_id} results - Accepted: {field_result['accepted']}, Rejected: {field_result['rejected']}")
        
        result["fields_tested"] = field_results
        result["steps_completed"].append("test_fields")
        
        # Step 5: Test inputting a number to the brokerage field and check ship_cost_diff
        if result.get("brokerage_field_found", False) and result.get("ship_cost_diff_found", False):
            logger.info(f"Step 5: Testing input of number 100 to brokerage field and checking ship_cost_diff")
            
            # First get the current ship_cost_diff value
            original_diff_value = ship_cost_diff_elem.text.strip()
            logger.info(f"Current value of ship_cost_diff element: {original_diff_value}")
            
            # Clear the brokerage field and input the number 100
            brokerage_field.clear()
            brokerage_field.send_keys("100")
            
            # Click on an empty part of the screen (the body element is a safe choice)
            logger.info("Clicking on empty part of screen")
            driver.find_element(By.TAG_NAME, "body").click()
            
            # Wait 2 seconds for any JavaScript to run and UI to update
            logger.info("Waiting 2 seconds for UI update")
            time.sleep(2)
            
            # Check the ship_cost_diff value again
            new_diff_value = ship_cost_diff_elem.text.strip()
            logger.info(f"New value of ship_cost_diff element after inputting 100 to brokerage: {new_diff_value}")
            
            # Check if the value changed
            if new_diff_value == original_diff_value:
                logger.info("ship_cost_diff value did not change - PASS")
                diff_unchanged = True
            else:
                logger.warning(f"ship_cost_diff value changed from {original_diff_value} to {new_diff_value} - FAIL")
                diff_unchanged = False
            
            # Store the results
            result["brokerage_test"] = {
                "brokerage_field_id": brokerage_id,
                "ship_cost_diff_id": ship_cost_diff_id,
                "input_value": "100",
                "original_diff_value": original_diff_value,
                "new_diff_value": new_diff_value,
                "diff_unchanged": diff_unchanged
            }
            
            result["steps_completed"].append("test_brokerage_field")
        
        # All steps completed successfully
        result["success"] = True
        logger.info(f"Domain test workflow completed successfully for {domain}")
        
        return result
            
    except Exception as e:
        error_msg = f"Unexpected error during domain test workflow: {str(e)}"
        logger.error(error_msg)
        
        if not result["failed_step"]:
            result["failed_step"] = "unexpected_error"
            
        result["error"] = error_msg
        return result