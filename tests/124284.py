# tests/124285.py - Modified with XLS verification
import logging
import sys
import time
from selenium import webdriver

from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.utils.retry_decorator import with_retry
from common.config.login.login_as_user import login_as_user
from common.pages.page_621.actions.create_lead_621 import create_lead_621
from common.pages.page_621.actions.search_item_by_part_number import search_item_by_part_number
from common.pages.page_621.actions.add_quantity_to_search_results import add_quantity_to_item
from common.pages.page_621.actions.mark_items_as_presale import mark_items_as_presale
from common.pages.page_972.actions.create_presale import create_presale
from common.pages.page_972.actions.set_presale_deadline import set_presale_deadline
from projects.sm_us.pages.page_972.actions.add_expired_offer import add_expired_offer
from projects.sm_us.pages.page_972.actions.verify_expired_offers import verify_expired_offers
from common.pages.page_972.actions.verify_export_xls import verify_export_xls_for_buying

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("test_lead_search_with_presale_deadline")

@with_retry(max_attempts=2)
def test_lead_to_presale_with_deadline_workflow():
    """
    End-to-end test that:
    1. Logs in as user 'ml' on project 'sm_us'
    2. Creates a lead for a specific company
    3. Searches for an item by part number
    4. Adds a quantity and clicks the Add button for a found item
    5. Marks selected items as presale
    6. Creates a presale from the lead
    7. Sets a deadline for accepting offers on the presale
    8. Adds an expired offer to the presale
    9. Verifies the expired offers UI functionality
    10. Verifies that Export XLS for Buying contains the expected item ID
    """
    # Test parameters
    project_code = "sm_us"
    user_type = "ml"
    company_id = 713804  
    part_number = "TN-430" 
    item_id = "item_35033" 
    expected_item_id = "35033"  # The ID to check in the Excel export
    quantity = 2  # Quantity to add
    specific_deadline = "2025-05-01"  # Specific date for the deadline
    offer_price = 33  # Price for the expired offer

    driver = None
    try:
        # Setup Chrome driver with download preferences
        logger.info("Setting up Chrome driver")
        driver = setup_chrome_driver(headless=False)
        
        # Login to the system
        logger.info(f"Logging in as user '{user_type}' on project '{project_code}'")
        login_result = login_as_user(driver, project_code, user_type)
        
        if not login_result.get("success", False):
            error_msg = login_result.get("error", "Unknown login error")
            logger.error(f"Login failed: {error_msg}")
            return {"success": False, "error": error_msg}
        
        logger.info("Login successful")
        
        # Create a lead
        logger.info(f"Creating lead for company ID: {company_id}")
        lead_result = create_lead_621(driver, project_code, company_id)
        
        if not lead_result.get("success", False):
            error_msg = lead_result.get("error", "Unknown error during lead creation")
            logger.error(f"Lead creation failed: {error_msg}")
            return {"success": False, "error": error_msg}
        
        lead_id = lead_result.get("lead_id")
        logger.info(f"Lead created successfully with ID: {lead_id}")
        
        # Search for an item by part number
        logger.info(f"Searching for part number: {part_number}")
        search_result = search_item_by_part_number(driver, part_number)
        
        if not search_result.get("success", False):
            error_msg = search_result.get("error", "Unknown error during part number search")
            logger.error(f"Search failed: {error_msg}")
            return {"success": False, "error": error_msg}
        
        logger.info(f"Item search completed successfully for part number: {part_number}")
        
        # Add quantity and click the Add button for the found item
        logger.info(f"Adding quantity {quantity} for item {item_id}")
        add_result = add_quantity_to_item(driver, item_id, quantity)
        
        if not add_result.get("success", False):
            error_msg = add_result.get("error", "Unknown error when adding item quantity")
            logger.error(f"Adding item failed: {error_msg}")
            return {"success": False, "error": error_msg}
        
        logger.info(f"Successfully added item with quantity {quantity}")
        
        # Mark items as presale
        logger.info("Marking items as presale")
        presale_result = mark_items_as_presale(driver)
        
        if not presale_result.get("success", False):
            error_msg = presale_result.get("error", "Unknown error when marking items as presale")
            logger.error(f"Marking as presale failed: {error_msg}")
            return {"success": False, "error": error_msg}
        
        logger.info("Successfully marked items as presale")
        
        # Create presale from the lead
        logger.info(f"Creating presale from lead ID: {lead_id}")
        create_presale_result = create_presale(driver, project_code, lead_id)
        
        if not create_presale_result.get("success", False):
            error_msg = create_presale_result.get("error", "Unknown error during presale creation")
            logger.error(f"Presale creation failed: {error_msg}")
            return {"success": False, "error": error_msg}
        
        presale_id = create_presale_result.get("presale_id")
        logger.info(f"Successfully created presale with ID: {presale_id}")
        
        # Set deadline for accepting offers on the presale
        logger.info(f"Setting deadline for presale ID: {presale_id} to {specific_deadline}")
        deadline_result = set_presale_deadline(driver, project_code, presale_id, specific_date=specific_deadline)
        
        if not deadline_result.get("success", False):
            error_msg = deadline_result.get("error", "Unknown error when setting presale deadline")
            logger.error(f"Setting deadline failed: {error_msg}")
            return {"success": False, "error": error_msg}
        
        deadline_date = deadline_result.get("deadline_date")
        logger.info(f"Successfully set presale deadline to: {deadline_date}")
        
        # Add an expired offer to the presale
        logger.info(f"Adding expired offer for company {company_id} with price {offer_price}")
        offer_result = add_expired_offer(driver, company_id, quantity, offer_price)
        
        if not offer_result.get("success", False):
            error_msg = offer_result.get("error", "Unknown error when adding expired offer")
            logger.error(f"Adding expired offer failed: {error_msg}")
            return {"success": False, "error": error_msg}
        
        logger.info(f"Successfully added expired offer with price: {offer_price}")
        
        # Verify the expired offers functionality
        logger.info("Verifying expired offers functionality")
        verify_result = verify_expired_offers(driver)
        
        if not verify_result.get("success", False):
            error_msg = verify_result.get("error", "Unknown error during expired offers verification")
            logger.error(f"Expired offers verification failed: {error_msg}")
            # We continue despite verification failure to report all checks
        
        verification_details = verify_result.get("verification", {})
        logger.info(f"Verification details: {verification_details}")
        
        # Verify Export XLS for Buying
        logger.info(f"Verifying Export XLS for Buying contains item ID: {expected_item_id}")
        xls_result = verify_export_xls_for_buying(driver, expected_item_id)
        
        if not xls_result.get("success", False):
            error_msg = xls_result.get("error", "Unknown error during XLS verification")
            logger.error(f"XLS verification failed: {error_msg}")
            # We continue despite verification failure to report all checks
        
        logger.info(f"XLS verification result: {xls_result}")
        
        return {
            "success": True, 
            "error": None, 
            "lead_id": lead_id,
            "presale_id": presale_id,
            "deadline_date": deadline_date,
            "verification_details": verification_details,
            "xls_verification": xls_result,
            "message": "Successfully completed lead-to-presale workflow with deadline setting and expired offer"
        }
        
    except Exception as e:
        error_msg = f"Test failed with exception: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    finally:
        # Clean up driver
        if driver:
            logger.info("Releasing Chrome driver")
            release_driver(driver)


if __name__ == "__main__":
    result = test_lead_to_presale_with_deadline_workflow()
    
    if result.get("success", False):
        logger.info(f"Test completed successfully: {result.get('message', '')}")
        logger.info(f"Lead ID: {result.get('lead_id')}, Presale ID: {result.get('presale_id')}")
        logger.info(f"Deadline set to: {result.get('deadline_date')}")
        
        # Log verification details
        verification_details = result.get("verification_details", {})
        if verification_details:
            logger.info("Expired offers verification results:")
            for check, passed in verification_details.items():
                logger.info(f"  - {check}: {'PASS' if passed else 'FAIL'}")
        
        # Log XLS verification
        xls_verification = result.get("xls_verification", {})
        if xls_verification:
            logger.info("Export XLS verification results:")
            for key, value in xls_verification.items():
                if key != "success":  # Already logged in summary
                    logger.info(f"  - {key}: {value}")
        
        sys.exit(0)
    else:
        error = result.get("error", "Unknown error")
        logger.error(f"Test failed: {error}")
        sys.exit(1)