# /projects/at_eu/pages/page_836/workflow/company_status_check/check_company_balance.py(Check if popup is displayed)
import logging

# Import individual actions
from projects.at_eu.pages.page_836.actions.submit_form import submit_form
from projects.at_eu.pages.page_836.actions.click_company_status import click_company_status
from projects.at_eu.pages.page_836.actions.verify_balance_warning import verify_balance_warning
from projects.at_eu.pages.page_836.actions.close_balance_warning import close_balance_warning

def check_company_balance_workflow(driver, timeouts=None):
    """
    Complete workflow to check company balance warning:
    1. Submit form
    2. Click company status button in table
    3. Verify balance warning popup
    4. Close balance warning popup
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the workflow with success status, details and step information
    """
    logger = logging.getLogger('test')
    logger.info("Starting workflow: check company balance warning")
    
    result = {
        "success": False,
        "steps_completed": [],
        "failed_step": None,
        "error": None,
        "text_matches": False,
        "actual_text": None
    }
    
    # Step 1: Submit form
    logger.info("Step 1: Submit form")
    submit_result = submit_form(driver, timeouts)
    if not submit_result["success"]:
        result["failed_step"] = "submit_form"
        result["error"] = f"Failed to submit form: {submit_result['error']}"
        return result
    
    result["steps_completed"].append("submit_form")
    
    # Step 2: Click company status button
    logger.info("Step 2: Click company status button")
    click_result = click_company_status(driver, timeouts)
    if not click_result["success"]:
        result["failed_step"] = "click_company_status"
        result["error"] = f"Failed to click company status button: {click_result['error']}"
        return result
    
    result["steps_completed"].append("click_company_status")
    
    # Step 3: Verify balance warning
    logger.info("Step 3: Verify balance warning popup")
    verify_result = verify_balance_warning(driver, timeouts)
    
    # Store verification results regardless of next steps
    result["text_matches"] = verify_result.get("matches", False)
    result["actual_text"] = verify_result.get("actual_text")
    
    if not verify_result["success"]:
        result["failed_step"] = "verify_balance_warning"
        result["error"] = f"Failed to verify balance warning: {verify_result['error']}"
        return result
    
    result["steps_completed"].append("verify_balance_warning")
    
    # Step 4: Close balance warning
    logger.info("Step 4: Close balance warning popup")
    close_result = close_balance_warning(driver, timeouts)
    if not close_result["success"]:
        result["failed_step"] = "close_balance_warning"
        result["error"] = f"Failed to close balance warning: {close_result['error']}"
        return result
    
    result["steps_completed"].append("close_balance_warning")
    
    # All steps completed successfully
    result["success"] = True
    logger.info("Workflow completed successfully")
    
    return result