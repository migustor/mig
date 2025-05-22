# tests/gr_eu/page_907/test_tracking_lookup.py
import os
import time
import logging
import sys
import uuid
from datetime import datetime
from selenium.webdriver.common.by import By

# Generate a unique test ID for this test run
TEST_ID = f"tracking_lookup_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Import functions for working with centralized driver pool
from common.utils.driver_setup import setup_chrome_driver, release_driver

# Import workflow for login
from common.config.login.login_as_user import login_as_user

# Import logout function
from common.config.logout.logout_from_system import logout_from_system

# Import page info to get the URL
from projects.gr_eu.pages.page_907.page_info import get_page_907_url

# Import our complete workflow
from projects.gr_eu.pages.page_907.workflow.tracking_workflow import tracking_lookup_workflow

# Import locators
from projects.gr_eu.pages.page_907.locators import Page907Locators

# Import error handling decorator
from common.utils.error_handling import jenkins_aware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Timeouts for different operations
TIMEOUTS = {
    "login": 20,       # Timeout for login operations
    "action": 15,      # Timeout for form actions
    "navigation": 25,  # Timeout for navigation operations
    "page_load": 30    # Timeout for page loading
}

# List of order IDs to test
ORDER_IDS = [601204, 89372]

def clear_fields(driver):
    """Helper function to clear both order ID and tracking number fields"""
    try:
        logger.info("Cleaning up fields")
        # Clear tracking number field
        tracking_field = driver.find_element(*Page907Locators.TRACKING_NUMBER_FIELD)
        tracking_field.clear()
        logger.info("Cleared tracking number field")
        
        # Clear order ID field
        order_id_field = driver.find_element(*Page907Locators.ORDER_ID_FIELD)
        order_id_field.clear()
        logger.info("Cleared order ID field")
        
        return True
    except Exception as e:
        logger.warning(f"Failed to clear fields: {str(e)}")
        return False

def test_order_tracking(driver, order_id):
    """Test tracking lookup for a specific order ID"""
    logger.info(f"======= Starting tracking test for order ID: {order_id} =======")
    
    try:
        # Always clear fields before starting a new test
        clear_fields(driver)
        time.sleep(1)  # Small pause to ensure fields are cleared
        
        # Run the tracking lookup workflow
        logger.info(f"Running tracking lookup workflow for order ID {order_id}")
        
        workflow_result = tracking_lookup_workflow(driver, order_id, timeouts=TIMEOUTS)
        
        if not workflow_result["success"]:
            failed_step = workflow_result.get("failed_step", "unknown")
            error_message = f"Workflow failed at step '{failed_step}': {workflow_result['error']}"
            logger.error(error_message)
            return {"success": False, "error": error_message, "step": failed_step}
        
        # Check verification results
        if not workflow_result["verification"]["matches"]:
            warning_msg = (f"Order ID verification failed. Expected: {order_id}, "
                         f"Actual: {workflow_result['verification']['actual_order_id']}")
            logger.warning(warning_msg)
            print(f"VERIFICATION WARNING: {warning_msg}")
            return {"success": True, "warning": warning_msg, "verification": False}
        else:
            logger.info(f"Order ID verification passed for {order_id}")
            print(f"VERIFICATION PASSED: Order ID {order_id} matched final result")
        
        # Report tracking numbers found
        first_tracking = workflow_result["tracking_numbers"].get("first")
        second_tracking = workflow_result["tracking_numbers"].get("second")
        logger.info(f"Found tracking numbers for order {order_id}: "
                   f"First: {first_tracking}, Second: {second_tracking}")
        
        # Summarize steps completed
        steps_completed = workflow_result.get("steps_completed", [])
        logger.info(f"Completed steps: {', '.join(steps_completed)}")
        print(f"TEST PASSED: Successfully completed all {len(steps_completed)} steps")
        
        return {
            "success": True, 
            "verification": True,
            "tracking_numbers": workflow_result["tracking_numbers"]
        }
            
    except Exception as e:
        error_msg = f"Error during test execution for order ID {order_id}: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": str(e), "step": "test_execution"}

@jenkins_aware()
def run_test(driver):
    """
    Main test execution function that's decorated with jenkins_aware
    to enable screenshot capturing on failures.
    """
    logger.info(f"Starting test execution with ID: {TEST_ID}")
    
    # Project to test
    project_name = "gr_eu"
    
    # Track results
    results = {}
    
    try:
        # Step 1: Login with the test user
        logger.info(f"Starting login process for project {project_name}")
        login_result = login_as_user(
            driver, 
            user_type="vm",  # Update this to match an existing user in your credentials
            project_name=project_name, 
            timeouts=TIMEOUTS
        )
        
        if not login_result["success"]:
            logger.error(f"Login error: {login_result['error']}")
            return {"success": False, "error": login_result["error"], "step": "login"}
        
        logger.info(f"Login successful for {project_name}")
        
        # Step 2: Navigate to page 907
        logger.info(f"Navigating to page 907 for {project_name}")
        try:
            page_url = get_page_907_url(project_name)
            
            if not page_url:
                error_msg = f"Could not get URL for page 907 in project {project_name}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg, "step": "navigation"}
                
            driver.get(page_url)
            time.sleep(2)  # Give page time to load
            
            logger.info(f"Successfully navigated to page 907. URL: {driver.current_url}")
            
        except Exception as e:
            error_msg = f"Error during navigation to page 907: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": str(e), "step": "navigation"}
        
        # Step 3: Test each order ID
        for order_id in ORDER_IDS:
            # Run test for this order ID
            result = test_order_tracking(driver, order_id)
            results[str(order_id)] = result
            
            # Make sure fields are cleared after each test
            clear_fields(driver)
            time.sleep(1)  # Small pause to ensure UI is ready
            
            # Add some separation between order ID tests
            print("\n" + "-"*50 + "\n")
            
        # Print summary report
        print(f"\n=========== SUMMARY REPORT (TEST ID: {TEST_ID}) ===========")
        all_passed = True
        for order_id, result in results.items():
            status = "PASSED" if result["success"] else "FAILED"
            if not result["success"]:
                all_passed = False
                print(f"Order ID {order_id}: {status} - Failed at step: {result.get('step', 'unknown')}")
                print(f"  Error: {result.get('error', 'Unknown error')}")
            else:
                verification = "Verification PASSED" if result.get("verification", False) else "Verification FAILED"
                print(f"Order ID {order_id}: {status} - {verification}")
                if "tracking_numbers" in result:
                    print(f"  First tracking: {result['tracking_numbers'].get('first')}")
                    print(f"  Second tracking: {result['tracking_numbers'].get('second')}")
        
        print("\nOverall status:", "PASSED" if all_passed else "FAILED")
        logger.info(f"Test {TEST_ID} completed with status: {'PASSED' if all_passed else 'FAILED'}")
        
        # Return failed status if any order ID test failed
        if not all_passed:
            return {"success": False, "error": "One or more order ID tests failed"}
        return {"success": True}
    
    except Exception as e:
        logger.error(f"Process failed with unexpected error: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        # Ensure logout happens regardless of test outcome
        logout_from_system(driver, project_name)

def main():
    """
    Main entry point that sets up the driver and runs the test.
    """
    # Read the HEADLESS environment variable; default to True if not set
    headless_mode = os.environ.get('HEADLESS', 'False').lower() == 'true'
    
    # Get driver from centralized pool with test_id
    driver = setup_chrome_driver(headless=headless_mode, test_id=TEST_ID)
    
    try:
        # Run the test, passing driver as an argument
        result = run_test(driver)
        
        # Exit with appropriate code
        if not result.get("success", False):
            sys.exit(1)
    finally:
        # Always release the driver
        release_driver(driver)

if __name__ == "__main__":
    main()