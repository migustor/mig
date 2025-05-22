"""
End-to-end test for shipping functionality combining page 902, 905, and warehouse shipping
Tests all pages in sequence for each project without logging in again between pages
"""
import os
import time
import logging
import sys
import uuid
from datetime import datetime

# Generate a unique test ID for this test run
TEST_ID = f"combined_shipping_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Import functions for working with centralized driver pool
from common.utils.driver_setup import setup_chrome_driver, release_driver

# Import workflow for login
from common.config.login.login_as_user import login_as_user

# Import logout function
from common.config.logout.logout_from_system import logout_from_system

# Import page 902 actions
from common.pages.page_902.actions.click_add_shipping_package import click_add_shipping_package
from common.pages.page_902.actions.verify_dimension_changes import verify_dimension_change

# Import page 905 actions
from common.pages.page_905.actions.verify_dimension_changes import verify_weight_change
from common.pages.page_905.actions.click_add_shipping_package import add_shipping_package
from common.pages.page_907.actions.verify_shipping_costs import verify_shipping_costs

# Import warehouse shipping workflow
from common.pages.warehouse.goods_delivery.workflow.workflow_wh_check_auto_dhl_price import verify_dhl_cost_calculation

# Import retry decorator
from common.utils.retry_decorator import with_retry

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

@with_retry(max_attempts=2, retry_delay=5)
def test_project(driver, project_name, sales_order_id, box_id):
    """Run shipping functionality tests for a specific project across all shipping pages"""
    logger.info(f"======= Starting shipping tests for project: {project_name} =======")
    
    results = {
        "success": True,
        "page_902": {},
        "page_905": {},
        "warehouse": {}
    }
    
    try:
        # Step 1: Login with user "ml" (using this user for all tests)
        logger.info(f"Starting login process for project {project_name}")
        login_result = login_as_user(driver, project_name=project_name, user_type="ml", timeouts=TIMEOUTS)
        
        if not login_result["success"]:
            logger.error(f"Login error for {project_name}: {login_result['error']}")
            return {"success": False, "error": login_result["error"], "step": "login"}
        
        logger.info(f"Login successful for {project_name}")
        
        # ======================= Page 902 Tests =======================
        logger.info(f"Starting Page 902: Testing dimension change effects for sales order ID {sales_order_id}")
        
        # Step 2: Test dimension change effects on page 902
        dimension_result = verify_dimension_change(driver, project_name, sales_order_id)
        
        if not dimension_result["success"]:
            error_msg = f"Page 902 - Dimension change test failed: {dimension_result.get('error', 'Unknown error')}"
            logger.error(error_msg)
            results["success"] = False
            results["page_902"] = {
                "success": False,
                "error": error_msg,
                "step": "verify_dimension_change"
            }
        else:
            # Store dimension change results
            results["page_902"]["dimension_result"] = dimension_result
            
            # Step 3: Test adding shipping package on page 902
            logger.info(f"Page 902: Testing Add Shipping Package button for sales order ID {sales_order_id}")
            add_package_result = click_add_shipping_package(driver, project_name, sales_order_id)
            
            if not add_package_result["success"]:
                error_msg = f"Page 902 - Add shipping package test failed: {add_package_result.get('error', 'Unknown error')}"
                logger.error(error_msg)
                results["success"] = False
                results["page_902"] = {
                    "success": False,
                    "error": error_msg,
                    "step": "add_shipping_package"
                }
            else:
                # Store add package results
                results["page_902"]["add_package_result"] = add_package_result
                results["page_902"]["success"] = True
                logger.info(f"Page 902 tests completed successfully for project {project_name}")
        
        # ======================= Page 905 Tests =======================
        logger.info(f"Starting Page 905: Testing weight change effects for sales order ID {sales_order_id}")
        
        # Step 4: Test weight change effects on page 905
        weight_result = verify_weight_change(driver, project_name, sales_order_id)
        
        if not weight_result["success"]:
            error_msg = f"Page 905 - Weight change test failed: {weight_result.get('error', 'Unknown error')}"
            logger.error(error_msg)
            results["success"] = False
            results["page_905"] = {
                "success": False,
                "error": error_msg,
                "step": "verify_weight_change"
            }
        else:
            # Store weight change results
            results["page_905"]["weight_result"] = weight_result
            
            # Step 5: Test adding shipping package on page 905
            logger.info(f"Page 905: Testing Add Shipping Package for sales order ID {sales_order_id}")
            add_package_result_905 = add_shipping_package(driver, project_name, sales_order_id)
            
            if not add_package_result_905["success"]:
                error_msg = f"Page 905 - Add shipping package test failed: {add_package_result_905.get('error', 'Unknown error')}"
                logger.error(error_msg)
                results["success"] = False
                results["page_905"] = {
                    "success": False,
                    "error": error_msg,
                    "step": "add_shipping_package"
                }
            else:
                # Store add package results
                results["page_905"]["add_package_result"] = add_package_result_905
                results["page_905"]["success"] = True
                logger.info(f"Page 905 tests completed successfully for project {project_name}")
        
        # ======================= Warehouse Shipping Tests =======================
        logger.info(f"Starting Warehouse: Testing DHL cost calculation for SO ID {sales_order_id} and Box ID {box_id}")
        
        # Step 6: Test DHL cost calculation in warehouse
        wh_result = verify_dhl_cost_calculation(
            driver=driver,
            project_name=project_name,
            so_id=sales_order_id,
            box_id=box_id,
            new_weight=25  # Set a fixed test weight
        )
        
        if not wh_result["success"]:
            error_msg = f"Warehouse - DHL cost calculation failed: {wh_result.get('error', 'Unknown error')}"
            logger.error(error_msg)
            results["success"] = False
            results["warehouse"] = {
                "success": False,
                "error": error_msg,
                "step": wh_result.get("step", "verify_dhl_cost")
            }
        else:
            # Store warehouse results
            results["warehouse"] = {
                "success": True,
                "original_cost": wh_result.get("original_cost"),
                "new_cost": wh_result.get("new_cost"),
                "warning_text": wh_result.get("warning_text")
            }
            logger.info(f"Warehouse shipping tests completed successfully for project {project_name}")
        
        # ======================= Special SM_EU Extended Test =======================
        # Only for sm_eu project, add specialized test
        if project_name == "sm_eu":
            logger.info(f"Starting SM_EU specialized test: Add, verify and delete shipping box")
            
            # Import the specialized action for sm_eu
            try:
                from projects.sm_eu.pages.warehouse.goods_delivery.actions.add_new_shipping_box import add_new_shipping_box
                
                # Run the specialized test
                special_result = add_new_shipping_box(
                    driver=driver,
                    project_name=project_name,
                    sales_order_id=sales_order_id
                )
                
                # Store results
                results["sm_eu_special"] = special_result
                
                # If special test failed, update overall success
                if not special_result["success"]:
                    results["success"] = False
                    
                logger.info(f"SM_EU specialized test completed with status: {special_result['success']}")
                
            except ImportError as ie:
                error_msg = f"Failed to import sm_eu specialized action: {str(ie)}"
                logger.error(error_msg)
                results["sm_eu_special"] = {
                    "success": False,
                    "error": error_msg
                }
            except Exception as e:
                error_msg = f"Error during sm_eu specialized test: {str(e)}"
                logger.error(error_msg)
                results["sm_eu_special"] = {
                    "success": False,
                    "error": error_msg
                }
        
        # If we got here, return all results regardless of individual test success
        logger.info(f"All shipping tests completed for project {project_name}")
        return results
            
    except Exception as e:
        error_msg = f"Unexpected error during test for {project_name}: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    finally:
        # Ensure logout happens regardless of test outcome
        logout_from_system(driver, project_name)


@jenkins_aware()
def run_test(driver):
    """
    Main test function that accepts driver as an argument.
    This allows the jenkins_aware decorator to create screenshots on errors.
    """
    logger.info(f"Starting combined shipping test execution with ID: {TEST_ID}")
    
    # Track results
    results = {}
    
    try:
        # Define projects to test with their sales order IDs and box IDs
        # Add more projects as needed
        test_cases = [
            {"project_name": "sm_eu", "sales_order_id": "629790", "box_id": "349895"},
            {"project_name": "ra_eu", "sales_order_id": "100755", "box_id": "79264"},
            {"project_name": "ho_eu", "sales_order_id": "1272", "box_id": "2020"},
            {"project_name": "lt_eu", "sales_order_id": "88104", "box_id": "93380"},
            {"project_name": "ag_eu", "sales_order_id": "50323", "box_id": "53272"},
            {"project_name": "dr_eu", "sales_order_id": "1768", "box_id": "2347"},
            {"project_name": "et_eu", "sales_order_id": "276990", "box_id": "203115"}
        ]
        
        for test_case in test_cases:
            project_name = test_case["project_name"]
            sales_order_id = test_case["sales_order_id"]
            box_id = test_case["box_id"]
            
            # Run test for this project
            result = test_project(driver, project_name, sales_order_id, box_id)
            results[project_name] = result
            
            # Add some separation between project tests
            print("\n" + "-"*50 + "\n")
        
        # Add a special verification for sm_eu shipping costs
        logger.info("Running additional shipping cost verification for sm_eu")
        sm_eu_sales_order_id = test_cases[-1]["sales_order_id"]  # Using the last test case (sm_eu)
        sm_eu_box_id = test_cases[-1]["box_id"]

        # Verify shipping costs on logistics page (gr_eu login required)
        shipping_costs_result = verify_shipping_costs(
            driver=driver,
            target_project="sm_eu",
            order_id=sm_eu_sales_order_id,
            box_ids=[sm_eu_box_id]
        )

        # Add results to the existing results dictionary
        results["sm_eu_logistics"] = shipping_costs_result
            
        # Print summary report
        print(f"\n=========== SUMMARY REPORT (TEST ID: {TEST_ID}) ===========")
        all_passed = True
        failed_projects = []
        
        for project, result in results.items():
            # Skip non-project entries (like sm_eu_logistics)
            if project == "sm_eu_logistics":
                continue
                
            project_status = "PASSED" if result["success"] else "FAILED"
            print(f"\n{project}: Overall Status - {project_status}")
            
            if not result["success"] and "error" in result and "step" in result:
                # Handle case where early failure prevented test structure
                all_passed = False
                failed_projects.append(project)
                if "error" in result and "step" in result:
                    print(f"  Failed at step: {result.get('step', 'unknown')}")
                    print(f"  Error: {result.get('error', 'Unknown error')}")
                    continue
            
            # Print Page 902 results
            page_902 = result.get("page_902", {})
            if page_902:
                page_902_status = "PASSED" if page_902.get("success", False) else "FAILED"
                print(f"  Page 902: {page_902_status}")
                
                if page_902_status == "FAILED":
                    all_passed = False
                    print(f"    Failed at step: {page_902.get('step', 'unknown')}")
                    print(f"    Error: {page_902.get('error', 'Unknown error')}")
                else:
                    # Print dimension change results
                    if "dimension_result" in page_902:
                        dim_result = page_902["dimension_result"]
                        value_changed = dim_result.get("value_changed", False)
                        print(f"    Dimension change test: {'Value Changed' if value_changed else 'Value NOT Changed'}")
                        print(f"    Initial: {dim_result.get('initial_value')}, New: {dim_result.get('new_value')}")
                    
                    # Print add package results
                    if "add_package_result" in page_902:
                        add_pkg = page_902["add_package_result"]
                        error_found = add_pkg.get("error_found", False)
                        print(f"    Error message: {'Found' if error_found else 'NOT Found'}")
                        if error_found:
                            print(f"    Message: {add_pkg.get('error_message')}")
            
            # Print Page 905 results
            page_905 = result.get("page_905", {})
            if page_905:
                page_905_status = "PASSED" if page_905.get("success", False) else "FAILED"
                print(f"  Page 905: {page_905_status}")
                
                if page_905_status == "FAILED":
                    all_passed = False
                    print(f"    Failed at step: {page_905.get('step', 'unknown')}")
                    print(f"    Error: {page_905.get('error', 'Unknown error')}")
                else:
                    # Print weight change results
                    if "weight_result" in page_905:
                        weight_result = page_905["weight_result"]
                        value_changed = weight_result.get("value_changed", False)
                        print(f"    Weight change test: {'Value Changed' if value_changed else 'Value NOT Changed'}")
                        print(f"    Initial: {weight_result.get('initial_value')}, New: {weight_result.get('new_value')}")
                    
                    # Print add package results
                    if "add_package_result" in page_905:
                        add_pkg = page_905["add_package_result"]
                        error_found = add_pkg.get("error_found", False)
                        print(f"    Error message: {'Found' if error_found else 'NOT Found'}")
                        if error_found:
                            print(f"    Message: {add_pkg.get('error_message')}")
            
            # Print Warehouse results
            warehouse = result.get("warehouse", {})
            if warehouse:
                warehouse_status = "PASSED" if warehouse.get("success", False) else "FAILED"
                print(f"  Warehouse: {warehouse_status}")
                
                if warehouse_status == "FAILED":
                    all_passed = False
                    print(f"    Failed at step: {warehouse.get('step', 'unknown')}")
                    print(f"    Error: {warehouse.get('error', 'Unknown error')}")
                else:
                    # Print DHL cost calculation results
                    original_cost = warehouse.get("original_cost", "N/A")
                    new_cost = warehouse.get("new_cost", "N/A")
                    print(f"    DHL cost calculation: Original: {original_cost}, New: {new_cost}")
                    if original_cost != new_cost:
                        print(f"    Cost changed as expected: Yes")
                    else:
                        print(f"    Cost changed as expected: No (Warning)")
                    warning_text = warehouse.get("warning_text")
                    if warning_text:
                        print(f"    Warning message: {warning_text}")
            
            # Print Logistics shipping costs verification for sm_eu only
            if project == "sm_eu" and "sm_eu_special" in result:
                sm_eu_special = result.get("sm_eu_special", {})
                sm_eu_special_status = "PASSED" if sm_eu_special.get("success", False) else "FAILED"
                print(f"  SM_EU Specialized Test: {sm_eu_special_status}")
                
                if sm_eu_special_status == "FAILED":
                    all_passed = False
                    print(f"    Error: {sm_eu_special.get('error', 'Unknown error')}")
                else:
                    # Print add box results
                    if "add_box_result" in sm_eu_special:
                        add_box = sm_eu_special["add_box_result"]
                        print(f"    Add Box: {'PASSED' if add_box.get('success', False) else 'FAILED'}")
                        if "warning_text" in add_box:
                            print(f"    Warning Text: {add_box['warning_text']}")
                    
                    # Print logistics verification results
                    if "logistics_result" in sm_eu_special:
                        logistics = sm_eu_special["logistics_result"]
                        print(f"    Logistics Verification: {'PASSED' if logistics.get('success', False) else 'FAILED'}")
                        if logistics.get("success", False) and "costs" in logistics:
                            for box_id, cost in logistics["costs"].items():
                                print(f"    Box ID: {box_id}, Cost: {cost}")
                    
                    # Print delete box results
                    if "delete_box_result" in sm_eu_special:
                        delete_box = sm_eu_special["delete_box_result"]
                        print(f"    Delete Box: {'PASSED' if delete_box.get('success', False) else 'FAILED'}")
                        if "message" in delete_box:
                            print(f"    Message: {delete_box['message']}")
        
        print("\nOverall status:", "PASSED" if all_passed else "FAILED")
        logger.info(f"Test {TEST_ID} completed with status: {'PASSED' if all_passed else 'FAILED'}")
        
        # Signal error if any project failed
        if not all_passed:
            error_msg = f"Failed projects: {', '.join(failed_projects)}"
            logger.error(error_msg)
            logger.error("Exiting with error code 1")
            sys.exit(1)
        return {"success": True}
    except Exception as e:
        logger.error(f"Process failed with unexpected error: {str(e)}")
        sys.exit(1)


def main():
    """
    Main entry point that creates the driver and passes it to the decorated function.
    """
    # Read the HEADLESS environment variable; default to True if not set
    headless_mode = os.environ.get('HEADLESS', 'False').lower() == 'true'
    
    # Create driver with unique test_id
    driver = setup_chrome_driver(headless=headless_mode, test_id=TEST_ID)
    
    try:
        # Run the test with driver as argument
        run_test(driver)  # Result is already handled by jenkins_aware decorator
    finally:
        # Always release the driver
        release_driver(driver)


if __name__ == "__main__":
    main()