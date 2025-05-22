# common/pages/page_22/workflow/clear_and_save_workflow.py
import logging
from common.pages.page_22.actions.clear_quantity_fields import clear_quantity_fields
from common.pages.page_22.actions.save_form import save_form

def clear_and_save_workflow(driver, timeout=10):
    """
    Workflow that clears all quantity per pallet fields and saves the form.
    
    Args:
        driver: Selenium WebDriver
        timeout (int): Maximum time to wait for elements
        
    Returns:
        dict: Result of the workflow {'success': bool, 'error': str or None, 'step': str, 'cleared_count': int}
    """
    logger = logging.getLogger('test')
    logger.info("Starting workflow to clear all quantity fields and save")
    
    # Step 1: Clear all quantity fields
    clear_result = clear_quantity_fields(driver, timeout)
    if not clear_result["success"]:
        return {
            "success": False, 
            "error": clear_result["error"],
            "step": "clear_quantity_fields",
            "cleared_count": clear_result.get("cleared_count", 0)
        }
    
    # Step 2: Save the form
    save_result = save_form(driver, timeout)
    if not save_result["success"]:
        return {
            "success": False, 
            "error": save_result["error"],
            "step": "save_form",
            "cleared_count": clear_result.get("cleared_count", 0)
        }
    
    # All steps completed successfully
    logger.info(f"Successfully cleared {clear_result.get('cleared_count', 0)} fields and saved the form")
    return {
        "success": True, 
        "error": None,
        "step": "complete",
        "cleared_count": clear_result.get("cleared_count", 0)
    }