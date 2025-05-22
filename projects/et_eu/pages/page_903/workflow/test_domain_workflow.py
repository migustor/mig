# common/pages/page_903/workflow/test_domain_workflow.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.pages.page_903.actions.login_to_domain import login_to_domain
from common.pages.page_903.locators import Page903Locators
from common.pages.page_903.page_info import get_page_903_url
from common.pages.page_903.actions.find_shipping_row import find_shipping_cost_row
from common.pages.page_903.actions.test_field_symbols import test_field_symbols

def test_domain_workflow(driver, domain, doc_id, symbols, username, password, timeouts=None):
    """
    Complete workflow to test a domain:
    1. Login to domain
    2. Navigate to page 903 with the specified document ID
    3. Find shipping cost row
    4. Test each shipping cost input with special symbols
    
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
        "fields_tested": {}
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
        
        # Step 3: Find shipping cost row
        logger.info(f"Step 3: Find shipping cost row")
        row_result = find_shipping_cost_row(driver, timeouts)
        if not row_result["success"]:
            result["failed_step"] = "find_shipping_row"
            result["error"] = row_result["error"]
            result["fields_tested"] = row_result["error"]
            return result
        
        shipping_inputs = row_result.get("shipping_inputs", [])
        if not shipping_inputs:
            result["failed_step"] = "find_shipping_inputs"
            result["error"] = "No shipping cost inputs found in row"
            result["fields_tested"] = "No shipping_cost fields found in the first row."
            return result
        
        result["steps_completed"].append("find_shipping_row")
        
        # Step 4: Test each shipping cost input
        logger.info(f"Step 4: Test shipping cost inputs with special symbols")
        field_results = {}
        
        for input_elem in shipping_inputs:
            field_id = input_elem.get_attribute("id") or input_elem.get_attribute("name") or "unknown_id"
            logger.info(f"Testing field {field_id}")
            
            field_result = test_field_symbols(driver, input_elem, symbols, timeouts)
            field_results[field_id] = field_result
            
            logger.info(f"Field {field_id} results - Accepted: {field_result['accepted']}, Rejected: {field_result['rejected']}")
        
        result["fields_tested"] = field_results
        result["steps_completed"].append("test_fields")
        
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