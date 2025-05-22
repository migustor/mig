# /common/pages/page_830/workflow/check_sales_buying.py(Check balance from page=836)
import logging

# Import action for opening company link from page 836
from common.pages.page_836.actions.open_company_link import open_company_link

# Import action for verifying sales and buying values from page 830
from common.pages.page_830.actions.verify_sales_buying_values import verify_sales_buying_values

def check_company_sales_buying_workflow(driver, timeouts=None):
    """
    Workflow to open a company link and verify its sales and buying values:
    1. Click on company link in page 836 (opens new tab)
    2. Verify sales and buying values on the opened page 830(CAS)
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the workflow with success status and details
    """
    logger = logging.getLogger('test')
    logger.info("Starting workflow: check company sales and buying values")
    
    result = {
        "success": False,
        "steps_completed": [],
        "failed_step": None,
        "error": None,
        "sales_text": None,
        "buying_text": None,
        "original_handle": None
    }
    
    # Step 1: Open company link in new tab
    logger.info("Step 1: Opening company link in new tab")
    link_result = open_company_link(driver, timeouts)
    
    # Store the original handle regardless of success
    result["original_handle"] = link_result.get("original_handle")
    
    if not link_result["success"]:
        result["failed_step"] = "open_company_link"
        result["error"] = f"Failed to open company link: {link_result['error']}"
        return result
    
    result["steps_completed"].append("open_company_link")
    
    # Step 2: Verify sales and buying values
    logger.info("Step 2: Verifying sales and buying values")
    values_result = verify_sales_buying_values(driver, timeouts)
    
    # Store values regardless of success
    result["sales_text"] = values_result.get("sales_text")
    result["buying_text"] = values_result.get("buying_text")
    result["sales_value"] = values_result.get("sales_value")
    result["buying_value"] = values_result.get("buying_value")
    result["sales_float"] = values_result.get("sales_float")
    result["buying_float"] = values_result.get("buying_float")
    
    if not values_result["success"]:
        result["failed_step"] = "verify_sales_buying_values"
        result["error"] = f"Failed to verify sales and buying values: {values_result['error']}"
        
        # Switch back to original tab before returning
        try:
            if result["original_handle"]:
                driver.switch_to.window(result["original_handle"])
        except Exception as e:
            logger.warning(f"Could not switch back to original tab: {str(e)}")
            
        return result
    
    result["steps_completed"].append("verify_sales_buying_values")
    
    # All steps completed successfully
    result["success"] = True
    logger.info("Workflow completed successfully")
    
    return result