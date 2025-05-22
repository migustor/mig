# common/pages/page_22/workflow/update_quantity_workflow.py
import logging
from common.pages.page_22.actions.input_multiple_quantities import input_multiple_quantities
from common.pages.page_22.actions.save_form import save_form

def update_quantity_workflow(driver, timeout=10):
    """
    Workflow that updates multiple quantity per pallet fields and saves the form.
    
    Args:
        driver: Selenium WebDriver
        timeout (int): Maximum time to wait for elements
        
    Returns:
        dict: Result of the workflow {'success': bool, 'error': str or None, 'step': str, 'values': list}
    """
    logger = logging.getLogger('test')
    logger.info("Starting workflow to update multiple quantity per pallet values")
    
    # Step 1: Input multiple quantity values
    input_result = input_multiple_quantities(driver, timeout)
    if not input_result["success"]:
        return {
            "success": False, 
            "error": input_result["error"],
            "step": "input_multiple_quantities",
            "values": input_result.get("values", [])
        }
    
    # Step 2: Save the form
    save_result = save_form(driver, timeout)
    if not save_result["success"]:
        return {
            "success": False, 
            "error": save_result["error"],
            "step": "save_form",
            "values": input_result.get("values", [])
        }
    
    # All steps completed successfully
    logger.info("Quantity update workflow completed successfully")
    return {
        "success": True, 
        "error": None,
        "step": "complete",
        "values": input_result.get("values", [])
    }