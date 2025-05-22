# projects/gr_eu/pages/page_907/workflow/tracking_workflow.py
import logging

# Import individual actions
from projects.gr_eu.pages.page_907.actions.input_order_id import input_order_id
from projects.gr_eu.pages.page_907.actions.build_report import build_report
from projects.gr_eu.pages.page_907.actions.wait_for_results import wait_for_results
from projects.gr_eu.pages.page_907.actions.get_tracking_number import get_tracking_number
from projects.gr_eu.pages.page_907.actions.input_tracking_number import input_tracking_number
from projects.gr_eu.pages.page_907.actions.clear_field import clear_field
from projects.gr_eu.pages.page_907.actions.verify_order_id import verify_order_id
from projects.gr_eu.pages.page_907.locators import Page907Locators

def tracking_lookup_workflow(driver, order_id, timeouts=None):
    """
    Complete workflow for tracking number lookup:
    1. Input order ID and build report
    2. Find first tracking number
    3. Input first tracking number, clear order ID, build report
    4. Find second tracking number
    5. Input second tracking number, build report
    6. Verify final order ID matches original
    
    Args:
        driver: Selenium WebDriver
        order_id: The order ID to look up
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the workflow with success status, details and step information
    """
    logger = logging.getLogger('test')
    logger.info(f"Starting workflow: tracking lookup for order ID {order_id}")
    
    result = {
        "success": False,
        "steps_completed": [],
        "failed_step": None,
        "error": None,
        "tracking_numbers": {},
        "verification": {
            "matches": False,
            "actual_order_id": None
        }
    }
    
    # Step 1: Input order ID
    logger.info("Step 1: Input order ID")
    input_result = input_order_id(driver, order_id, timeouts)
    if not input_result["success"]:
        result["failed_step"] = "input_order_id"
        result["error"] = f"Failed to input order ID: {input_result['error']}"
        return result
    
    result["steps_completed"].append("input_order_id")
    
    # Step 2: Build report
    logger.info("Step 2: Build report with order ID")
    build_result = build_report(driver, timeouts)
    if not build_result["success"]:
        result["failed_step"] = "build_report_order_id"
        result["error"] = f"Failed to build report: {build_result['error']}"
        return result
    
    result["steps_completed"].append("build_report_order_id")
    
    # Step 3: Wait for results
    logger.info("Step 3: Wait for search results")
    wait_result = wait_for_results(driver, timeouts)
    if not wait_result["success"]:
        result["failed_step"] = "wait_for_results_order_id"
        result["error"] = f"Failed to wait for results: {wait_result['error']}"
        return result
    
    result["steps_completed"].append("wait_for_results_order_id")
    
    # Step 4: Get first tracking number
    logger.info("Step 4: Get first tracking number")
    tracking1_result = get_tracking_number(
        driver, 
        Page907Locators.FIRST_TRACKING_LINK, 
        tracking_type="first", 
        timeouts=timeouts
    )
    if not tracking1_result["success"]:
        result["failed_step"] = "get_first_tracking"
        result["error"] = f"Failed to get first tracking number: {tracking1_result['error']}"
        return result
    
    first_tracking = tracking1_result["tracking_number"]
    result["tracking_numbers"]["first"] = first_tracking
    result["steps_completed"].append("get_first_tracking")
    
    # Step 5: Clear order ID field 
    logger.info("Step 5: Clear order ID field")
    clear_result = clear_field(driver, Page907Locators.ORDER_ID_FIELD, "order ID", timeouts)
    if not clear_result["success"]:
        result["failed_step"] = "clear_order_id"
        result["error"] = f"Failed to clear order ID: {clear_result['error']}"
        return result
    
    result["steps_completed"].append("clear_order_id")
    
    # Step 6: Input first tracking number
    logger.info("Step 6: Input first tracking number")
    input_tracking_result = input_tracking_number(driver, first_tracking, timeouts)
    if not input_tracking_result["success"]:
        result["failed_step"] = "input_first_tracking"
        result["error"] = f"Failed to input first tracking number: {input_tracking_result['error']}"
        return result
    
    result["steps_completed"].append("input_first_tracking")
    
    # Step 7: Build report with first tracking
    logger.info("Step 7: Build report with first tracking number")
    build_result2 = build_report(driver, timeouts)
    if not build_result2["success"]:
        result["failed_step"] = "build_report_first_tracking"
        result["error"] = f"Failed to build report with first tracking: {build_result2['error']}"
        return result
    
    result["steps_completed"].append("build_report_first_tracking")
    
    # Step 8: Wait for results
    logger.info("Step 8: Wait for search results after first tracking")
    wait_result2 = wait_for_results(driver, timeouts)
    if not wait_result2["success"]:
        result["failed_step"] = "wait_for_results_first_tracking"
        result["error"] = f"Failed to wait for results after first tracking: {wait_result2['error']}"
        return result
    
    result["steps_completed"].append("wait_for_results_first_tracking")
    
    # Step 9: Get second tracking number
    logger.info("Step 9: Get second tracking number")
    tracking2_result = get_tracking_number(
        driver, 
        Page907Locators.SECOND_TRACKING_LINK, 
        tracking_type="second", 
        timeouts=timeouts
    )
    if not tracking2_result["success"]:
        result["failed_step"] = "get_second_tracking"
        result["error"] = f"Failed to get second tracking number: {tracking2_result['error']}"
        return result
    
    second_tracking = tracking2_result["tracking_number"]
    result["tracking_numbers"]["second"] = second_tracking
    result["steps_completed"].append("get_second_tracking")
    
    # Step 10: Clear tracking field
    logger.info("Step 10: Clear tracking number field")
    clear_result2 = clear_field(driver, Page907Locators.TRACKING_NUMBER_FIELD, "tracking number", timeouts)
    if not clear_result2["success"]:
        result["failed_step"] = "clear_tracking"
        result["error"] = f"Failed to clear tracking field: {clear_result2['error']}"
        return result
    
    result["steps_completed"].append("clear_tracking")
    
    # Step 11: Input second tracking number
    logger.info("Step 11: Input second tracking number")
    input_tracking_result2 = input_tracking_number(driver, second_tracking, timeouts)
    if not input_tracking_result2["success"]:
        result["failed_step"] = "input_second_tracking"
        result["error"] = f"Failed to input second tracking number: {input_tracking_result2['error']}"
        return result
    
    result["steps_completed"].append("input_second_tracking")
    
    # Step 12: Build report with second tracking
    logger.info("Step 12: Build report with second tracking number")
    build_result3 = build_report(driver, timeouts)
    if not build_result3["success"]:
        result["failed_step"] = "build_report_second_tracking"
        result["error"] = f"Failed to build report with second tracking: {build_result3['error']}"
        return result
    
    result["steps_completed"].append("build_report_second_tracking")
    
    # Step 13: Wait for results
    logger.info("Step 13: Wait for search results after second tracking")
    wait_result3 = wait_for_results(driver, timeouts)
    if not wait_result3["success"]:
        result["failed_step"] = "wait_for_results_second_tracking"
        result["error"] = f"Failed to wait for results after second tracking: {wait_result3['error']}"
        return result
    
    result["steps_completed"].append("wait_for_results_second_tracking")
    
    # Step 14: Verify final order ID
    logger.info("Step 14: Verify final order ID matches original")
    verify_result = verify_order_id(driver, order_id, timeouts)
    
    # Store verification results
    result["verification"]["matches"] = verify_result.get("matches", False)
    result["verification"]["actual_order_id"] = verify_result.get("actual_order_id")
    
    if not verify_result["success"]:
        result["failed_step"] = "verify_order_id"
        result["error"] = f"Failed to verify order ID: {verify_result['error']}"
        return result
    
    result["steps_completed"].append("verify_order_id")
    
    # All steps completed successfully
    result["success"] = True
    logger.info(f"Workflow completed successfully for order ID {order_id}")
    
    return result