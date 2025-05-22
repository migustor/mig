# /common/pages/page_953/workflow/check_vendor_evolution_workflow.py
import logging
import time
from selenium.common.exceptions import TimeoutException

# Import action functions
from common.pages.page_953.actions.vendor_evolution_actions import (
    navigate_to_vendor_evolution_page,
    input_company_name,
    set_date_range,
    submit_vendor_evolution_form,
    verify_purchase_history_section
)

# Import table verification actions
from common.pages.page_953.actions.verify_purchase_table_actions import (
    verify_purchase_table_headers,
    verify_purchase_table_data
)

# Import export verification actions
from common.pages.page_953.actions.verify_export_actions import (
    export_and_verify_purchase_history
)

def check_vendor_evolution_report(driver, project_name, company_name, from_date="01-Jan-2024", to_date=None, verify_export=True, download_dir=None):
    """
    Complete workflow to test the Vendor Evolution Report functionality
    
    Args:
        driver: Selenium WebDriver
        project_name: Project code (e.g., "ag_eu", "sm_eu")
        company_name: Company name or ID to search for
        from_date: Start date in DD-MMM-YYYY format (e.g., "01-Jan-2024")
        to_date: Not used - kept for backwards compatibility
        verify_export: Whether to verify export functionality (default: True)
        download_dir: Directory for saving downloaded files (if None, will not verify file content)
        
    Returns:
        dict: Result with keys 'success', 'step', 'error', and additional data
    """
    logger = logging.getLogger('test')
    logger.info(f"Starting Vendor Evolution Report test for project {project_name}")
    
    # Step 1: Navigate to Vendor Evolution Report page
    logger.info("Step 1: Navigate to Vendor Evolution Report page")
    nav_result = navigate_to_vendor_evolution_page(driver, project_name)
    
    if not nav_result:
        return {
            "success": False,
            "step": "navigate_to_page",
            "error": f"Failed to navigate to Vendor Evolution Report page for project {project_name}"
        }
    
    # Step 2: Input company name and select from autocomplete
    logger.info(f"Step 2: Input company name: {company_name}")
    company_result = input_company_name(driver, company_name)
    
    if not company_result:
        return {
            "success": False,
            "step": "input_company",
            "error": f"Failed to input company: {company_name}"
        }
    
    # Step 3: Set date - use only from_date in 01-Jan-2024 format
    logger.info(f"Step 3: Set date: {from_date}")
    date_result = set_date_range(driver, from_date)
    
    if not date_result:
        return {
            "success": False,
            "step": "set_date_range",
            "error": "Failed to set date range"
        }
    
    # Step 4: Submit form
    logger.info("Step 4: Submit Vendor Evolution Report form")
    submit_result = submit_vendor_evolution_form(driver)
    
    if not submit_result:
        return {
            "success": False,
            "step": "submit_form",
            "error": "Failed to submit Vendor Evolution Report form"
        }
    
    # Step 5: Verify purchase history section
    logger.info("Step 5: Verify purchase history section")
    verify_result = verify_purchase_history_section(driver)
    
    if not verify_result["success"]:
        return {
            "success": False,
            "step": "verify_purchase_history",
            "error": verify_result.get("message", "Failed to verify purchase history section")
        }
    
    # Step 6: Verify table headers
    logger.info("Step 6: Verify table headers")
    headers_result = verify_purchase_table_headers(driver)
    
    if not headers_result["success"]:
        return {
            "success": False,
            "step": "verify_table_headers",
            "error": headers_result.get("message", "Failed to verify table headers")
        }
    
    # Step 7: Verify table data
    logger.info("Step 7: Verify table data")
    data_result = verify_purchase_table_data(driver)
    
    if not data_result["success"]:
        return {
            "success": False,
            "step": "verify_table_data",
            "error": data_result.get("message", "Failed to verify table data")
        }
    
    # Step 8: Export purchase history and verify file (optional)
    export_result = {"success": True, "message": "Export verification skipped"}
    if verify_export:
        logger.info("Step 8: Export purchase history and verify file")
        export_result = export_and_verify_purchase_history(driver, download_dir=download_dir)
        
        if not export_result["success"]:
            return {
                "success": False,
                "step": "export_and_verify",
                "error": export_result.get("message", "Failed to export and verify purchase history")
            }
    
    # Combine all results
    result = {
        "success": True,
        "step": "all_completed",
        "project": project_name,
        "company": company_name,
        "item_count": verify_result.get("item_count", 0),
        "row_count": data_result.get("row_count", 0),
        "sample_data": data_result.get("sample_data", None),
        "message": f"Vendor Evolution Report test completed successfully. Found {data_result.get('row_count', 0)} items in purchase history."
    }
    
    # Add export verification details if available
    if export_result.get("file_path"):
        result.update({
            "export_file": export_result.get("file_path"),
            "export_file_name": export_result.get("file_name"),
            "export_file_size": export_result.get("file_size"),
            "export_comparison": export_result.get("comparison_result", {})
        })
    
    logger.info(f"Vendor Evolution Report test completed: success={result['success']}")
    return result