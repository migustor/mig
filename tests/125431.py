"""
Test script for validating the functionality to copy part numbers 
from a sales order list, paste them to 'Add More Items', and verify
warning triangles in barcode modals.

Test ID: 125431
"""
import logging
import time
import sys
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import common utilities
from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.utils.error_handling import jenkins_aware
from common.utils.retry_decorator import with_retry
from common.config.login.login_as_user import login_as_user

# Import page specific modules
from common.pages.page_888.page_info import get_page_888_url
from common.pages.page_888.actions.copy_pn_from_list_so_and_paste_to_add_items import copy_pn_from_list_so_and_paste_to_add_items
from common.pages.page_888.actions.verify_warning_triangles_in_barcode_modals import verify_warning_triangles_in_barcode_modals

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test')

# Test configuration - projects and sales orders to test
TEST_CONFIGS = [
    {
        "project_code": "ra_eu",
        "user_type": "ml",
        "sales_orders": [101032]
    },
    {
        "project_code": "at_eu",
        "user_type": "ml",
        "sales_orders": [1198]
    },
    {
        "project_code": "sm_us",
        "user_type": "ml",
        "sales_orders": [36853]
    },
    {
        "project_code": "sm_eu",
        "user_type": "ml",
        "sales_orders": [629952]
    },
    {
        "project_code": "lt_eu",
        "user_type": "ml",
        "sales_orders": [89121]
    },
    {
        "project_code": "et_eu",
        "user_type": "ml",
        "sales_orders": [278373]
    }
]

@jenkins_aware()
@with_retry(max_attempts=2)
def test_copy_pn_from_so_to_add_items(driver, project_code, user_type, sales_order_id):
    """
    Tests the functionality to copy a part number from a sales order,
    paste it to the Add More Items search, and verify warning triangles.
    
    Args:
        driver: Selenium WebDriver
        project_code: Code of the project to test
        user_type: User type to login as
        sales_order_id: ID of the sales order to test
        
    Returns:
        dict: Result of the test
    """
    logger.info(f"Starting test for project {project_code}, sales order {sales_order_id}")
    
    try:
        # Step 1: Login to the system
        login_result = login_as_user(driver, project_code, user_type)
        if not login_result["success"]:
            return {
                "success": False,
                "error": f"Login failed: {login_result['error']}",
                "step": "login",
                "project": project_code
            }
        
        # Step 2: Navigate to the sales order page
        so_url = get_page_888_url(project_code, sales_order_id)
        if not so_url:
            return {
                "success": False,
                "error": f"Could not generate URL for project {project_code}",
                "step": "navigation",
                "project": project_code
            }
        
        driver.get(so_url)
        logger.info(f"Navigated to sales order {sales_order_id}")
        
        # Wait for page to load
        time.sleep(2)
        
        # Step 3: Execute the action to copy part number and paste to Add Items
        copy_result = copy_pn_from_list_so_and_paste_to_add_items(driver)
        if not copy_result["success"]:
            return {
                "success": False,
                "error": f"Copy and paste action failed: {copy_result['error']}",
                "step": "copy_paste",
                "project": project_code
            }
        
        logger.info(f"Successfully copied part number {copy_result['part_number']} and pasted to Add Items")
        
        # Step 4: Verify warning triangles in barcode modals
        verify_result = verify_warning_triangles_in_barcode_modals(driver)
        if not verify_result["success"]:
            return {
                "success": False,
                "error": f"Warning triangle verification failed: {verify_result['error']}",
                "step": "verify_warnings",
                "project": project_code,
                "has_warnings_first_modal": verify_result["has_warnings_first_modal"],
                "has_warnings_second_modal": verify_result["has_warnings_second_modal"]
            }
        
        logger.info("Successfully verified warning triangles in both modals")
        
        return {
            "success": True,
            "error": None,
            "step": "complete",
            "project": project_code,
            "part_number": copy_result["part_number"],
            "has_warnings_first_modal": verify_result["has_warnings_first_modal"],
            "has_warnings_second_modal": verify_result["has_warnings_second_modal"]
        }
        
    except Exception as e:
        logger.error(f"Unexpected error during test: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "step": "unknown",
            "project": project_code
        }

def run_tests():
    """
    Main function to run tests for all configured projects and sales orders.
    """
    success_count = 0
    failure_count = 0
    results = []
    
    for config in TEST_CONFIGS:
        project_code = config["project_code"]
        user_type = config["user_type"]
        
        for order_id in config["sales_orders"]:
            logger.info(f"=== Testing project {project_code}, sales order {order_id} ===")
            
            driver = setup_chrome_driver(headless=False)
            try:
                result = test_copy_pn_from_so_to_add_items(driver, project_code, user_type, order_id)
                results.append({
                    "project_code": project_code,
                    "sales_order_id": order_id,
                    "result": result
                })
                
                if result["success"]:
                    success_count += 1
                    logger.info(f"Test PASSED for {project_code}, sales order {order_id}")
                else:
                    failure_count += 1
                    logger.error(f"Test FAILED for {project_code}, sales order {order_id}: {result['error']}")
            finally:
                release_driver(driver)
    
    # Print summary report
    logger.info("\n=== Test Summary ===")
    logger.info(f"Total tests: {success_count + failure_count}")
    logger.info(f"Passed: {success_count}")
    logger.info(f"Failed: {failure_count}")
    
    for result in results:
        status = "PASS" if result["result"]["success"] else "FAIL"
        logger.info(f"{status}: {result['project_code']}, Sales Order {result['sales_order_id']}")
        
        # Print additional details for each test
        if "has_warnings_first_modal" in result["result"]:
            logger.info(f"  First modal has warnings: {result['result']['has_warnings_first_modal']}")
        if "has_warnings_second_modal" in result["result"]:
            logger.info(f"  Second modal has warnings: {result['result']['has_warnings_second_modal']}")
    
    # Return non-zero exit code if any test failed (for Jenkins)
    return 0 if failure_count == 0 else 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)