# /common/pages/page_925/workflow/search_no_offers.py
import logging

# Import individual actions
from common.pages.page_925.actions.select_no_offers import select_no_offers
from common.pages.page_925.actions.submit_form import submit_form
from common.pages.page_925.actions.extract_si_id import extract_si_id
from common.utils.error_handling import jenkins_aware
@jenkins_aware()
def search_no_offers_workflow(driver, timeouts=None):
    """
    Complete workflow to search for offers with 'No' condition:
    1. Select 'No' radio button
    2. Submit form
    3. Extract SI ID from results
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the workflow with success status, details and step information
    """
    logger = logging.getLogger('test')
    logger.info("Starting workflow: search for offers with 'No' condition")
    
    result = {
        "success": False,
        "steps_completed": [],
        "failed_step": None,
        "error": None,
        "si_id": None
    }
    
    # Step 1: Select 'No' radio button
    logger.info("Step 1: Select 'No' radio button")
    select_result = select_no_offers(driver, timeouts)
    if not select_result["success"]:
        result["failed_step"] = "select_no_offers"
        result["error"] = f"Failed to select 'No' radio button: {select_result['error']}"
        return result
    
    result["steps_completed"].append("select_no_offers")
    
    # Step 2: Submit form
    logger.info("Step 2: Submit form")
    submit_result = submit_form(driver, timeouts)
    if not submit_result["success"]:
        result["failed_step"] = "submit_form"
        result["error"] = f"Failed to submit form: {submit_result['error']}"
        return result
    
    result["steps_completed"].append("submit_form")
    
    # Step 3: Extract SI ID
    logger.info("Step 3: Extract SI ID from results")
    extract_result = extract_si_id(driver, timeouts)
    
    # Store SI ID regardless of success (it might be None if no results)
    result["si_id"] = extract_result.get("si_id")
    
    if not extract_result["success"]:
        result["failed_step"] = "extract_si_id"
        result["error"] = f"Failed to extract SI ID: {extract_result['error']}"
        return result
    
    result["steps_completed"].append("extract_si_id")
    
    # All steps completed successfully
    result["success"] = True
    logger.info(f"Workflow completed successfully, SI ID: {result['si_id']}")
    
    return result