"""
Workflow module to verify leads in the history page
"""
import logging

# Import individual actions
from common.pages.page_714.actions.navigate_to_lead_history import navigate_to_lead_history
from common.pages.page_714.actions.verify_lead_column import verify_lead_column

def verify_leads_workflow(driver, url, timeouts=None):
    """
    Complete workflow to verify leads in history table:
    1. Navigate to lead history
    2. Verify lead column and extract leads
    
    Args:
        driver: Selenium WebDriver
        url: URL of the lead history page
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the workflow with success status and detailed information
    """
    logger = logging.getLogger('test')
    logger.info("Starting workflow: verify leads in history")
    
    result = {
        "success": False,
        "steps_completed": [],
        "leads_found": [],
        "total_leads": 0,
        "valid_leads": 0,
        "failed_step": None,
        "error": None
    }
    
    # Step 1: Navigate to lead history
    logger.info("Step 1: Navigate to lead history")
    navigation_result = navigate_to_lead_history(driver, url, timeouts)
    if not navigation_result["success"]:
        result["failed_step"] = "navigate_to_lead_history"
        result["error"] = navigation_result["error"]
        return result
    
    result["steps_completed"].append("navigate_to_lead_history")
    
    # Step 2: Verify lead column
    logger.info("Step 2: Verify lead column")
    verification_result = verify_lead_column(driver, timeouts)
    
    # Add verification results to overall result
    result["leads_found"] = verification_result.get("leads_found", [])
    result["total_leads"] = verification_result.get("total_leads", 0)
    result["valid_leads"] = verification_result.get("valid_links", 0)
    
    if not verification_result["success"]:
        result["failed_step"] = "verify_lead_column"
        result["error"] = verification_result.get("error", "Lead verification failed")
        return result
    
    result["steps_completed"].append("verify_lead_column")
    
    # All steps completed successfully
    result["success"] = True
    logger.info(f"Workflow completed successfully with {result['valid_leads']} valid leads")
    
    return result