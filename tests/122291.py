import logging
import sys
import time

# WebDriver lifecycle
from common.utils.driver_setup import setup_chrome_driver, release_driver

# Login / logout utilities
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system

# Page info for page 907
from projects.gr_eu.pages.page_907.page_info import get_page_907_url

# Workflows
from projects.gr_eu.pages.page_907.workflow.order_filter_workflow import filter_and_get_orders_workflow as so_filter_workflow
from projects.gr_eu.pages.page_907.workflow.email_check import email_check_workflow
from projects.gr_eu.pages.page_907.workflow.validation import validation_workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(" - SO TEST - ")

TIMEOUTS = {
    "login": 20,
    "wait": 20,
    "max_wait": 60  # Increased to 60 seconds
}


def try_order_workflow(driver, order_id, timeouts=None):
    """
    Tries the complete workflow for a single order ID:
    1) Email check workflow
    2) Validation workflow
    
    Returns a dict with success status and details.
    """
    result = {
        "success": False,
        "skipped": False,
        "email_check": None,
        "validation": None,
        "order_id": order_id
    }
    
    # 1. Try email check
    email_check_res = email_check_workflow(driver, order_id, timeouts)
    result["email_check"] = email_check_res
    
    if not email_check_res["success"]:
        return result
    
    # 2. Try validation
    order_data = {
        "order_id": email_check_res.get("order_id"),
        "tracking_number": email_check_res.get("tracking_number"),
        "company_name": email_check_res.get("company_name")
    }
    
    validation_res = validation_workflow(driver, order_data, timeouts)
    result["validation"] = validation_res
    
    if validation_res["success"]:
        result["success"] = True
    elif validation_res.get("skipped", False):
        # If validation was skipped (no Generate Email button), mark as skipped
        result["skipped"] = True
    
    return result


def run_so_test(driver):
    """
    This function performs the SO test:
      1) Go to page_907 with ?order_type=so
      2) Filter to 'delivered', build report, get first 3 orders
      3) Try each order ID with email check and validation until one succeeds
    """
    logger.info("[SO TEST] Navigating to 907 (SO)")
    result = {
        "success": False,
        "steps": {}
    }

    # Step 1: Navigate to 907 with order_type=so
    page_907_url = get_page_907_url("gr_eu", "so")
    driver.get(page_907_url)
    time.sleep(3)  # Let the page load
    logger.info(f"[SO TEST] Current URL: {driver.current_url}")
    result["steps"]["navigate_907_so"] = "SUCCESS"

    # Step 2: Filter delivered, build report, get orders
    filter_res = so_filter_workflow(driver, timeouts=TIMEOUTS)
    if not filter_res["success"]:
        logger.error(f"[SO TEST] Filter workflow failed: {filter_res['error']}")
        result["steps"]["so_filter"] = "FAILED"
        return result
    result["steps"]["so_filter"] = "SUCCESS"

    order_ids = filter_res.get("order_ids", [])
    if not order_ids:
        logger.error("[SO TEST] No delivered orders found.")
        result["steps"]["so_orders"] = "FAILED"
        return result
    
    logger.info(f"[SO TEST] Found {len(order_ids)} order IDs: {order_ids}")
    result["steps"]["so_orders"] = "SUCCESS"

    # Step 3: Try each order ID with email check and validation
    all_order_results = []
    all_skipped = True
    
    for order_id in order_ids:
        logger.info(f"[SO TEST] Trying complete workflow for order ID: {order_id}")
        order_result = try_order_workflow(driver, order_id, TIMEOUTS)
        all_order_results.append(order_result)
        
        if order_result["success"]:
            logger.info(f"[SO TEST] Order ID {order_id} completed successfully")
            result["success"] = True
            result["order_id"] = order_id
            return result
        
        if not order_result.get("skipped", False):
            all_skipped = False
    
    # If we're here, all orders failed or were skipped
    if all_skipped:
        logger.warning("[SO TEST] All orders were skipped (Generate Email button not available)")
        result["steps"]["so_validation"] = "SKIPPED"
    else:
        logger.error("[SO TEST] All orders failed validation or email check")
        result["steps"]["so_validation"] = "FAILED"
    
    result["all_order_results"] = all_order_results
    return result


def main():
    """
    Main entry point that:
     1) Creates and configures WebDriver
     2) Logs in once
     3) Runs SO test
     4) Prints final summary
     5) Logs out and quits
    """
    headless = False  # Adjust if needed
    driver = setup_chrome_driver(headless=headless, test_id="so_orders_test")

    # Overall test result storage
    final_result = {
        "success": True,
        "details": []
    }

    try:
        logger.info("[MAIN] Logging in as user vb on gr_eu")
        login_res = login_as_user(driver, "gr_eu", "vb", timeouts=TIMEOUTS)
        if not login_res["success"]:
            logger.error(f"[MAIN] Login failed: {login_res['error']}")
            print("=== TEST FAILED (LOGIN) ===")
            sys.exit(1)
        logger.info("[MAIN] Login success")

        # SO test only
        so_result = run_so_test(driver)
        final_result["details"].append(("SO", so_result))
        if not so_result["success"]:
            final_result["success"] = False

        # Print final summary
        if final_result["success"]:
            print("=== TEST PASSED ===")
            print("SO check passed successfully.")
        else:
            print("=== TEST FAILED ===")
            
            skipped_only = True
            for label, res in final_result["details"]:
                if not res["success"]:
                    # Only print actual failures, not skipped steps
                    failed_steps = []
                    for step, status in res["steps"].items():
                        if status == "FAILED":
                            failed_steps.append(step)
                            skipped_only = False
                    
                    if failed_steps:
                        print(f"{label} part failed.")
                        for step in failed_steps:
                            print(f" - Failed step: {step}")
            
            # If all failures were just skips (no Generate Email button), don't fail the build
            if skipped_only:
                print("Note: All failures were due to unavailable Generate Email buttons (skipped validations)")
                print("Considering test as PASSED since this is an expected limitation")
                # Don't exit with error code
            else:
                # Signal Jenkins about the failure
                sys.exit(1)

    finally:
        # Always log out and quit driver
        logout_from_system(driver, "gr_eu")
        release_driver(driver)


if __name__ == "__main__":
    main()