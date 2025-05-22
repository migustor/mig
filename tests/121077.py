# /tests/test_vendor_evolution_report.py
import logging
import os
import sys
import time
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test')

# Import utilities
from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.utils.error_handling import jenkins_aware
from common.utils.retry_decorator import with_retry
from common.config.login.login_as_user import login_as_user

# Import workflow functions
from common.pages.page_953.workflow.check_vendor_evolution_workflow import check_vendor_evolution_report

# Define project configurations
PROJECT_CONFIGS = {
    "ag_eu": {"company_id": "41297"},
    "ra_eu": {"company_id": "249865"},
    "et_eu": {"company_id": "58007"},
    "sm_us": {"company_id": "566691"},
    "sm_eu": {"company_id": "313834"},
    "lt_eu": {"company_id": "97841"},
    "ho_eu": {"company_id": "22362"},
    "dr_eu": {"company_id": "2557"},
    "at_eu": {"company_id": "126"}
}

@jenkins_aware()
@with_retry(max_attempts=2)
def test_vendor_evolution_report(project_code="ag_eu", user_type="ml", company_name=None, from_date="01-Jan-2024", verify_export=True):
    """
    Test the Vendor Evolution Report functionality including table verification and export
    
    Args:
        project_code: Project code (default: "ag_eu")
        user_type: User type from credential.py (default: "ml")
        company_name: Company name or ID to search (default: None, will use from PROJECT_CONFIGS)
        from_date: Start date in format "01-Jan-2024"
        verify_export: Whether to verify export functionality (default: True)
        
    Returns:
        dict: Test result
    """
    # Use company ID from PROJECT_CONFIGS if not explicitly provided
    if company_name is None:
        if project_code in PROJECT_CONFIGS:
            company_name = PROJECT_CONFIGS[project_code]["company_id"]
        else:
            logger.warning(f"Project code {project_code} not found in PROJECT_CONFIGS, using default company ID 41297")
            company_name = "41297"
    
    logger.info(f"Starting Vendor Evolution Report test for project {project_code} with company ID {company_name}")
    
    # Initialize WebDriver
    driver = None
    
    try:
        # Setup download directory if verifying export
        download_dir = None
        if verify_export:
            # Create download directory in temp or in the script directory
            download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
            os.makedirs(download_dir, exist_ok=True)
            logger.info(f"Downloads will be saved to: {download_dir}")
        
        # Setup Chrome driver with download directory
        driver = setup_chrome_driver(headless=False, download_dir=download_dir)
        
        # Step 1: Login to the system
        logger.info(f"Step 1: Login to {project_code} as {user_type}")
        login_result = login_as_user(driver, project_code, user_type)
        
        if not login_result["success"]:
            return {
                "success": False,
                "step": "login",
                "error": login_result.get("error", f"Failed to login to {project_code} as {user_type}")
            }
        
        # Step 2: Run the Vendor Evolution Report workflow with table verification and export
        logger.info(f"Step 2: Testing Vendor Evolution Report with company {company_name}")
        logger.info(f"Using date: {from_date}")
        
        report_result = check_vendor_evolution_report(
            driver, 
            project_code, 
            company_name, 
            from_date=from_date,
            verify_export=verify_export,
            download_dir=download_dir
        )
        
        # Return result
        return report_result
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        return {
            "success": False,
            "step": "unknown",
            "error": f"Unexpected error: {str(e)}"
        }
    finally:
        # Release driver
        if driver:
            release_driver(driver)
            logger.info("WebDriver released")

def test_all_projects(user_type="ml", from_date="01-Jan-2024", verify_export=True):
    """
    Run vendor evolution report test for all configured projects
    
    Args:
        user_type: User type from credential.py (default: "ml")
        from_date: Start date in format "01-Jan-2024"
        verify_export: Whether to verify export functionality (default: True)
        
    Returns:
        dict: Test results for all projects
    """
    results = {}
    overall_success = True
    
    for project_code in PROJECT_CONFIGS:
        logger.info(f"=== Testing project: {project_code} ===")
        
        result = test_vendor_evolution_report(
            project_code=project_code,
            user_type=user_type,
            from_date=from_date,
            verify_export=verify_export
        )
        
        results[project_code] = result
        
        # Update overall success
        if not result.get("success", False):
            overall_success = False
            
        print_verification_results(result, project_code)
        logger.info(f"=== Completed testing project: {project_code} ===\n")
    
    return {
        "success": overall_success,
        "results": results
    }

def print_verification_results(result, project_code=None):
    """
    Prints test verification results in a simple format
    
    Args:
        result: Test result dictionary
        project_code: Project code (optional)
    """
    project_info = f"[{project_code}] " if project_code else ""
    
    if result["success"]:
        print(f"{project_info}TEST PASSED: {result.get('message', '')}")
        print(f"Found {result.get('row_count', 0)} items in purchase history")
    else:
        print(f"{project_info}TEST FAILED at step '{result.get('step', 'unknown')}': {result.get('error', 'Unknown error')}")
    
    # Print export verification result if available
    if result.get("export_file"):
        print(f"\n{project_info}EXPORT VERIFICATION:")
        print(f"   File: {result.get('export_file_name')}")
        print(f"   Size: {result.get('export_file_size')} bytes")
        
        # Print comparison details
        export_comparison = result.get("export_comparison", {})
        if export_comparison:
            matching = export_comparison.get("matching_rows", 0)
            total = len(export_comparison.get("details", []))
            print(f"   Results: {matching}/{total} rows match")
            print(f"   {export_comparison.get('message', '')}")
            
            # Print comparison details for first few rows
            if export_comparison.get("details"):
                print("\n   Row comparisons:")
                for detail in export_comparison.get("details"):
                    match_status = "MATCH" if detail.get("match") else "MISMATCH"
                    print(f"   Row {detail.get('row')}: {match_status}")
                    print(f"      Web PO_ID: {detail.get('page_po_id', '')}")
                    print(f"      Excel PO_ID: {detail.get('excel_po_id', '')}")

if __name__ == "__main__":
    # Standard parameters for all projects
    user_type = "ml"             # Default user
    from_date = "01-Jan-2024"    # Date in format DD-MMM-YYYY
    verify_export = True         # Export verification
    
    # Run tests for all projects
    results = test_all_projects(
        user_type=user_type,
        from_date=from_date,
        verify_export=verify_export
    )
    
    # Print overall results
    print("\n=== OVERALL TEST RESULTS ===")
    print(f"Overall success: {'PASSED' if results['success'] else 'FAILED'}")
    print(f"Projects tested: {len(results['results'])}")
    successful = sum(1 for r in results['results'].values() if r.get('success', False))
    print(f"Successful projects: {successful}/{len(results['results'])}")
    
    # Code exit for Jenkins
    sys.exit(0 if results["success"] else 1)