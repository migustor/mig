"""
Test for checking company balance warning.
Ticket number: 123217
"""
import logging
import time

from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.utils.error_handling import jenkins_aware
from common.utils.retry_decorator import with_retry
from common.config.login.login_as_user import login_as_user
from common.config.base_urls import PROJECT_BASE_URLS
from common.pages.page_830.workflow.check_balance_warning import check_balance_warning

# List of projects for testing and their companies with non-zero balance
TEST_DATA = {
    "ra_eu": ["517820"],
    "lt_eu": ["161428"],
    "ag_eu": ["206666"],
    "sm_us": ["713804"],
    "sm_eu": ["830813"],
    "et_eu": ["410753"],
    "dr_eu": ["114624"],
    "ho_eu": ["107247"],
    "at_eu": ["183262"],
    "aro_eu": ["431370"],
    "argon": ["36705"],
    "roc": ["15901"]
}

@jenkins_aware()
@with_retry(max_attempts=2)
def test_company_balance_warning(company_id=None):
    """
    Test for checking company balance warning.
    
    Args:
        company_id: ID of the company to check (if None, taken from TEST_DATA)
    
    Returns:
        dict: Test results for each project
    """
    logger = logging.getLogger('test')
    
    # Logging setup
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    print("Starting test for company balance warning")
    
    # Test results for each project
    results = {}
    
    # Use only projects defined in TEST_DATA
    for project_code, company_ids in TEST_DATA.items():
        print(f"Testing project: {project_code}")
        
        # Create driver
        driver = setup_chrome_driver(headless=False)
        
        try:
            # Select company ID for the test
            test_company_id = company_id if company_id else company_ids[0]
            
            print(f"Company for testing: {test_company_id}")
            
            # Login to the system
            user_type = "ml"  # Default user type
            login_result = login_as_user(driver, project_code, user_type)
            
            if not login_result["success"]:
                print(f"Failed to log in: {login_result.get('error')}")
                results[project_code] = {
                    "success": False,
                    "error": f"Login error: {login_result.get('error')}",
                    "step": "login"
                }
                continue
            
            # Navigate to company page
            company_url = f"{PROJECT_BASE_URLS[project_code]}index.cfm?page_id=830&company_id={test_company_id}"
            print(f"Navigating to company page: {company_url}")
            
            driver.get(company_url)
            time.sleep(2)  # Allow page to load
            
            # Perform check for non-zero balance warning
            check_result = check_balance_warning(driver)
            
            results[project_code] = check_result
            
            if check_result["success"]:
                print(f"TEST PASSED for project {project_code}, company {test_company_id}")
            else:
                print(f"TEST FAILED for project {project_code}, company {test_company_id}: {check_result.get('error')}")
                
        except Exception as e:
            error_msg = f"Unexpected error while testing project {project_code}: {str(e)}"
            print(error_msg)
            import traceback
            print(traceback.format_exc())
            
            results[project_code] = {
                "success": False,
                "error": error_msg,
                "step": "unexpected_error"
            }
            
        finally:
            # Release driver
            release_driver(driver)
    
    # Summarize results
    success_count = sum(1 for r in results.values() if r.get("success", False))
    total_count = len(results)
    
    print(f"Results: {success_count} out of {total_count} passed")
    
    return results


def main():
    """
    Main function to run the test.
    """
    # Run test for all projects defined in TEST_DATA
    results = test_company_balance_warning()
    
    # Print results
    for project, result in results.items():
        print(f"{project}: PASSED" if result.get("success", False) else f"{project}: FAILED")
        if not result.get("success", False):
            print(f"  Error: {result.get('error')}")
            print(f"  Step: {result.get('step', 'unknown')}")


if __name__ == "__main__":
    main()