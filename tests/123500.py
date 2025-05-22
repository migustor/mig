# tests/124500.py
"""
Test ID: 124500
Description: Test document upload functionality for leads on page ID=621 and configuration on page ID=696
             with quantity per pallet management on page ID=22
"""
import logging
import sys
import os
import time
import re
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import utility functions
from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.utils.error_handling import jenkins_aware
from common.utils.retry_decorator import with_retry
from common.config.login.login_as_user import login_as_user

# Import page-specific modules
from common.pages.page_621.page_info import get_page_621_url
from common.pages.page_621.actions.upload_file import upload_project_document, process_uploaded_document
from common.pages.page_621.actions.create_lead_button import click_create_button
from common.pages.page_696.actions.configure_columns import configure_document_columns
from common.pages.page_621.actions.verify_pallet_data import verify_pallet_quantity_data
from common.pages.page_714.actions.check_pallet_data import check_item_pallet_data
from common.pages.page_621.actions.search_item_by_part_number import search_item_by_part_number
from common.pages.page_621.actions.verify_search_result_data import verify_search_result_data

# Import quantity management workflows
from common.pages.page_22.workflow.update_quantity_workflow import update_quantity_workflow
from common.pages.page_22.workflow.clear_and_save_workflow import clear_and_save_workflow
from common.pages.page_22.page_info import get_page_22_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test')

# Company IDs and Item IDs for testing 
COMPANY_IDS = {
    "sm_eu": "830813",
    "ho_eu": "107247",
    "ra_eu": "517820",
    "et_eu": "410753",
    "ag_eu": "206666"
}

# Item IDs for page 22
ITEM_IDS = {
    "sm_eu": "142502",
    "ho_eu": "51486",
    "ra_eu": "3915",
    "et_eu": "21510875",
    "ag_eu": "93415"     
}

# Set fixed document directory path
DOCUMENTS_DIR = r"J:\PUB28\E2E_Testing\trunk\tests\documents\123500"

@jenkins_aware()
@with_retry(max_attempts=2)
def test_document_upload(driver, project_code):
    """
    Test function for document upload on page 621 and column configuration on page 696.
    Also manages quantity per pallet values on page 22.
    
    Args:
        driver: Selenium WebDriver
        project_code: The project code to test (e.g., "sm_eu")
        
    Returns:
        dict: Test result {'success': bool, 'error': str or None}
    """
    logger.info(f"Starting document upload test for project {project_code}")
    
    # Check if the project is supported for this test
    if project_code not in COMPANY_IDS:
        error_msg = f"Project {project_code} not configured for this test. Add company_id to COMPANY_IDS."
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Check if item ID is configured for this project
    if project_code not in ITEM_IDS:
        error_msg = f"Project {project_code} does not have an item_id configured. Add item_id to ITEM_IDS."
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Get the company_id and item_id for this project
    company_id = COMPANY_IDS[project_code]
    item_id = ITEM_IDS[project_code]
    
    # Variables to store quantity data for reporting
    quantity_values = []
    cleared_count = 0
    
    try:
        # Step 1: Login to the system
        logger.info("Step 1: Logging in to the system")
        login_result = login_as_user(driver, project_code, "ml")
        if not login_result["success"]:
            return {
                "success": False,
                "error": f"Login failed: {login_result['error']}",
                "step": "login"
            }
        
        # Step 2: Navigate to page 22 to update quantity per pallet values
        logger.info("Step 2: Navigating to page 22 to update quantity per pallet values")
        page22_url = get_page_22_url(project_code, item_id)
        logger.info(f"Navigating to: {page22_url}")
        driver.get(page22_url)
        time.sleep(2)  # Short pause to let the page load
        
        # Step 3: Update quantity values on page 22
        logger.info("Step 3: Updating quantity per pallet values")
        update_result = update_quantity_workflow(driver)
        if not update_result["success"]:
            return {
                "success": False,
                "error": f"Quantity update failed: {update_result['error']}",
                "step": f"quantity_update_{update_result.get('step', 'unknown')}"
            }
        
        # Store the input quantity values for reporting
        quantity_values = update_result.get("values", [])
        logger.info(f"Successfully added quantity values: {quantity_values}")
        
        # Step 4: Generate and navigate to the lead URL on page 621
        logger.info("Step 4: Generating lead URL and navigating")
        page_url = get_page_621_url(project_code, company_id)
        logger.info(f"Navigating to: {page_url}")
        driver.get(page_url)
        time.sleep(2)  # Short pause to let the page load
        
        # Step 5: Upload the project-specific document
        logger.info("Step 5: Uploading project document")
        
        # Use specific document directory path
        os.makedirs(DOCUMENTS_DIR, exist_ok=True)  # Create dir if it doesn't exist
        filename = f"{project_code}.xlsx"
        file_path = os.path.join(DOCUMENTS_DIR, filename)
        
        # Check if the file exists at the specified path
        if not os.path.exists(file_path):
            error_msg = f"Document file not found: {file_path}"
            logger.error(error_msg)
            logger.error(f"Please ensure the file {filename} is placed in: {DOCUMENTS_DIR}")
            return {
                "success": False,
                "error": error_msg,
                "step": "document_check"
            }
        
        # Store the file path in the driver for the upload action to use
        driver.custom_file_path = file_path
        logger.info(f"Using document file at: {file_path}")
        
        # Just upload the file (don't process yet)
        upload_result = upload_project_document(driver, project_code)
        if not upload_result["success"]:
            return {
                "success": False,
                "error": f"Document upload failed: {upload_result['error']}",
                "step": "document_upload"
            }
        
        # Step 6: Click the Create button
        logger.info("Step 6: Clicking Create button")
        create_result = click_create_button(driver)
        if not create_result["success"]:
            return {
                "success": False,
                "error": f"Clicking Create button failed: {create_result['error']}",
                "step": "create_button"
            }
        
        # Allow time for the create operation to complete and navigate to the new lead
        time.sleep(3)
        
        # Extract lead_id from the current URL if needed for verification
        current_url = driver.current_url
        logger.info(f"Now on page: {current_url}")
        
        # Step 7: Process the file on the new lead page
        logger.info("Step 7: Processing the uploaded file")
        process_result = process_uploaded_document(driver)
        if not process_result["success"]:
            return {
                "success": False,
                "error": f"File processing failed: {process_result['error']}",
                "step": "file_processing"
            }
        
        # Step 8: Configure columns on page 696 (after processing)
        logger.info("Step 8: Configuring document columns and completing processing")
        config_result = configure_document_columns(driver)
        if not config_result["success"]:
            return {
                "success": False,
                "error": f"Column configuration failed: {config_result['error']}",
                "step": "column_configuration"
            }
        
        # Step 9: Verify pallet quantity data on lead editor page (after returning from page 696)
        logger.info("Step 9: Verifying pallet quantity data in the lead items table")
        verify_result = verify_pallet_quantity_data(driver)
        if not verify_result["success"]:
            return {
                "success": False,
                "error": f"Pallet quantity verification failed: {verify_result['error']}",
                "step": "pallet_verification"
            }
        
        # After verification, we're on the 621 lead page - capture the EXACT URL for later
        lead_url = driver.current_url
        logger.info(f"Captured lead page URL after verification: {lead_url}")
        
        # Make sure we have phase=edit in the URL for later use
        if "phase=edit" not in lead_url:
            lead_url = lead_url + "&phase=edit"
            logger.info(f"Added phase=edit to URL: {lead_url}")
        
        logger.info(f"Pallet quantity data verified on page 621: {verify_result.get('pallet_data')}")
        
        # Get item ID and part number from verification
        item_id = verify_result.get('item_id')
        part_number = verify_result.get('part_number')
        
        # Store data for comparison
        page621_data = verify_result.get('pallet_data')
        page714_data = None
        search_data = None
        
        # Step 10: Check pallet data on page 714 if we got an item ID
        if item_id:
            logger.info(f"Step 10: Checking pallet data on page 714 for item ID: {item_id}")
            pallet_check_result = check_item_pallet_data(driver, project_code, item_id)
            
            if not pallet_check_result["success"]:
                return {
                    "success": False,
                    "error": f"Pallet data check on page 714 failed: {pallet_check_result['error']}",
                    "step": "page_714_pallet_check"
                }
            
            page714_data = pallet_check_result.get('pallet_data')
            logger.info(f"Pallet data on page 714: {page714_data}")
            
            # Compare pallet data from both pages
            if page621_data == page714_data:
                logger.info("Pallet data matches between page 621 and page 714!")
            else:
                logger.warning(f"Pallet data mismatch! Page 621: {page621_data}, Page 714: {page714_data}")
        else:
            logger.warning("Skipping page 714 check as no item ID was extracted")
        
        # Navigate directly back to the exact lead page URL we captured earlier
        logger.info("Navigating back to lead page for item search")
        logger.info(f"Returning to captured lead URL: {lead_url}")
        driver.get(lead_url)
        time.sleep(2)  # Short pause to let the page load
        
        # Step 11: Search for the item by part number and verify pallet data
        if part_number:
            logger.info(f"Step 11: Searching for item by part number: {part_number}")
            
            # First - perform the search operation
            search_result = search_item_by_part_number(driver, part_number)
            if not search_result["success"]:
                return {
                    "success": False,
                    "error": f"Item search by part number failed: {search_result['error']}",
                    "step": "part_number_search"
                }
                
            # Then - verify the search results data
            logger.info("Step 11a: Verifying pallet data in search results")
            verify_result = verify_search_result_data(driver)
            if not verify_result["success"]:
                return {
                    "success": False,
                    "error": f"Verification of search results failed: {verify_result['error']}",
                    "step": "search_result_verification"
                }
            
            search_data = verify_result.get('pallet_data')
            logger.info(f"Pallet data in search results: {search_data}")
            
            # Compare pallet data from all sources
            logger.info(f"Pallet data comparison: Page 621: {page621_data}, Page 714: {page714_data}, Search: {search_data}")
            
            # Check if all sources match
            data_matches = True
            
            if page621_data != search_data:
                logger.warning(f"Pallet data mismatch between Page 621 and Search results")
                data_matches = False
                
            if page714_data and page714_data != search_data:
                logger.warning(f"Pallet data mismatch between Page 714 and Search results")
                data_matches = False
            
            if data_matches:
                logger.info("Pallet data matches across all verifications!")
        else:
            logger.warning("Skipping item search by part number as no part number was extracted")
        
        # Step 12: Return to page 22 to clear quantity values
        logger.info("Step 12: Returning to page 22 to clear quantity values")
        # Regenerate page22_url in case we need a fresh one
        page22_url = get_page_22_url(project_code, item_id)
        logger.info(f"Navigating to: {page22_url}")
        driver.get(page22_url)
        time.sleep(2)  # Short pause to let the page load
        
        # Step 13: Clear all quantity values on page 22
        logger.info("Step 13: Clearing all quantity per pallet values")
        clear_result = clear_and_save_workflow(driver)
        if not clear_result["success"]:
            return {
                "success": False,
                "error": f"Quantity clearing failed: {clear_result['error']}",
                "step": f"quantity_clear_{clear_result.get('step', 'unknown')}"
            }
        
        # Store the number of cleared fields for reporting
        cleared_count = clear_result.get("cleared_count", 0)
        logger.info(f"Successfully cleared {cleared_count} quantity fields")
        
        # Test completed successfully
        logger.info(f"Test completed successfully for project {project_code}")
        return {
            "success": True, 
            "error": None, 
            "filename": upload_result.get("filename"),
            "pallet_data_621": page621_data,
            "pallet_data_714": page714_data,
            "pallet_data_search": search_data,
            "item_id": item_id,
            "part_number": part_number,
            "quantity_values_added": quantity_values,
            "quantity_fields_cleared": cleared_count
        }
        
    except Exception as e:
        error_msg = f"Unexpected error during test: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

if __name__ == "__main__":
    # Explicitly specify projects to test
    projects_to_test = ["sm_eu", "ho_eu", "ra_eu", "et_eu", "ag_eu"]  # Test both projects sequentially
    
    # Variable to track overall success
    all_success = True
    
    # Results for all projects
    results = {}
    
    # Run tests for each project
    for project_to_test in projects_to_test:
        logger.info(f"\n{'='*50}\nStarting test for project: {project_to_test}\n{'='*50}")
        
        # Create a new driver for each project
        driver = setup_chrome_driver(headless=True)  # Set to False for visual inspection
        
        try:
            result = test_document_upload(driver, project_to_test)
            results[project_to_test] = result
            
            if not result["success"]:
                all_success = False
            
            # Print current project result
            if result["success"]:
                pallet_data_621 = result.get('pallet_data_621', 'not found')
                pallet_data_714 = result.get('pallet_data_714', 'not checked')
                pallet_data_search = result.get('pallet_data_search', 'not checked')
                item_id = result.get('item_id', 'not found')
                part_number = result.get('part_number', 'not found')
                quantity_values = result.get('quantity_values_added', [])
                cleared_count = result.get('quantity_fields_cleared', 0)
                
                print(f"\n===== TEST RESULTS FOR {project_to_test} =====")
                print(f"TEST PASSED - Document uploaded and configured: {result.get('filename', 'unknown')}")
                print("\n----- Quantity Management -----")
                print(f"Added quantity values: {quantity_values}")
                print(f"Cleared quantity fields: {cleared_count}")
                print("\n----- Item Details -----")
                print(f"Item ID: {item_id}")
                print(f"Part Number: {part_number}")
                print("\n----- Pallet Data Verification -----")
                print(f"Pallet quantity data on page 621: {pallet_data_621}")
                print(f"Pallet quantity data on page 714: {pallet_data_714}")
                print(f"Pallet quantity data in search results: {pallet_data_search}")
                print("============================")
            else:
                print(f"\n===== TEST RESULTS FOR {project_to_test} =====")
                print(f"TEST FAILED: {result.get('error')} at step: {result.get('step', 'unknown')}")
                print("============================")
                
        except Exception as e:
            all_success = False
            logger.error(f"Unexpected error during {project_to_test} test: {str(e)}")
            print(f"\n===== TEST RESULTS FOR {project_to_test} =====")
            print(f"TEST FAILED due to error: {str(e)}")
            print("============================")
            
        finally:
            # Always release the driver after each project
            release_driver(driver)
    
    # Print overall results
    print("\n\n===== OVERALL TEST RESULTS =====")
    for project, result in results.items():
        status = "PASSED" if result.get("success") else "FAILED"
        print(f"{project}: {status}")
    
    print(f"\nOverall Test Status: {'PASSED' if all_success else 'FAILED'}")
    print("===============================")
    
    # Return success/error code
    sys.exit(0 if all_success else 1)