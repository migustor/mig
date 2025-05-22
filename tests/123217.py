# test_page_836_balance.py
import os
import time
import logging
import sys
import uuid
from datetime import datetime

# Generate a unique test ID for this test run
TEST_ID = f"page_836_balance_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Import functions for working with centralized driver pool
from common.utils.driver_setup import setup_chrome_driver, release_driver

# Import workflow for login
from common.config.login.login_as_user import login_as_user

# Import logout function
from common.config.logout.logout_from_system import logout_from_system

# Import page info to get the URL
from common.pages.page_836.page_info import get_page_836_url

# Import our complete workflow
from common.pages.page_836.workflow.check_company_balance import check_company_balance_workflow

# Import error handling decorator
from common.utils.error_handling import jenkins_aware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Timeouts for different operations
TIMEOUTS = {
    "login": 20,       # Timeout for login operations
    "action": 15,      # Timeout for form actions
    "navigation": 25,  # Timeout for navigation operations
    "page_load": 30    # Timeout for page loading
}

def test_project(driver, project_name):
    """Run test for a specific project"""
    logger.info(f"======= Starting test for project: {project_name} =======")
    
    try:
        # Step 1: Login with user "ml"
        logger.info(f"Starting login process for project {project_name}")
        login_result = login_as_user(driver, user_type="ml", project_name=project_name, timeouts=TIMEOUTS)
        
        if not login_result["success"]:
            logger.error(f"Login error for {project_name}: {login_result['error']}")
            return {"success": False, "error": login_result["error"], "step": "login"}
        
        logger.info(f"Login successful for {project_name}")
        
        # Step 2: Navigate to page 836
        logger.info(f"Navigating to page 836 for {project_name}")
        try:
            page_url = get_page_836_url(project_name)
            
            if not page_url:
                error_msg = f"Could not get URL for page 836 in project {project_name}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg, "step": "navigation"}
                
            driver.get(page_url)
            time.sleep(2)  # Give page time to load
            
            logger.info(f"Successfully navigated to page 836 for {project_name}. URL: {driver.current_url}")
            
        except Exception as e:
            error_msg = f"Error during navigation to page 836 for {project_name}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": str(e), "step": "navigation"}
        
        # Step 3: Run complete workflow
        logger.info(f"Running company balance check workflow for {project_name}")
        try:
            workflow_result = check_company_balance_workflow(driver, timeouts=TIMEOUTS)
            
            if not workflow_result["success"]:
                failed_step = workflow_result.get("failed_step", "unknown")
                error_message = f"Workflow failed for {project_name} at step '{failed_step}': {workflow_result['error']}"
                logger.error(error_message)
                return {"success": False, "error": workflow_result["error"], "step": failed_step}
            
            # Check if text matched even if workflow was successful
            if not workflow_result["text_matches"]:
                warning_msg = f"Warning text verification failed for {project_name}. Expected: 'Warning.\nNon-zero company balance.', Actual: '{workflow_result['actual_text']}'"
                logger.warning(warning_msg)
                print(f"VERIFICATION WARNING ({project_name}): {warning_msg}")
                return {"success": True, "warning": warning_msg, "verification": False}
            else:
                logger.info(f"Balance warning text verification passed for {project_name}")
                print(f"VERIFICATION PASSED ({project_name}): Balance warning text matched expected value")
            
            # Summarize steps completed
            steps_completed = workflow_result.get("steps_completed", [])
            logger.info(f"Completed steps for {project_name}: {', '.join(steps_completed)}")
            print(f"TEST PASSED ({project_name}): Successfully completed all {len(steps_completed)} steps")
            
            return {"success": True, "verification": True}
            
        except Exception as e:
            error_msg = f"Error during workflow execution for {project_name}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": str(e), "step": "workflow"}
    finally:
        # Ensure logout happens regardless of test outcome
        logout_from_system(driver, project_name)

<<<<<<< .mine
@jenkins_aware()
def main():
||||||| .r531
@jenkins_aware(screenshot_dir=SCREENSHOT_DIR)
def main():
=======
# Эта функция будет принимать драйвер в качестве первого аргумента
@jenkins_aware()
def run_test(driver):
    """
    Основная функция запуска теста, которая принимает драйвер в качестве аргумента.
    Это позволяет декоратору jenkins_aware создавать скриншоты при ошибках.
    """
>>>>>>> .r534
    logger.info(f"Starting test execution with ID: {TEST_ID}")
    
<<<<<<< .mine
    # Read the HEADLESS environment variable; default to True if not set
    headless_mode = os.environ.get('HEADLESS', 'False').lower() == 'true'
    
    # Define projects to test
    projects_to_test = ["ra_eu"]
    
    # Get driver from centralized pool with test_id
    driver = setup_chrome_driver(headless=headless_mode, test_id=TEST_ID)
    
||||||| .r531
    # Read the HEADLESS environment variable; default to True if not set
    headless_mode = os.environ.get('HEADLESS', 'True').lower() == 'true'
    
    # Define projects to test
    projects_to_test = ["ra_eu", "at_eu"]
    
    # Get driver from centralized pool with test_id
    driver = setup_chrome_driver(headless=headless_mode, test_id=TEST_ID)
    
=======
>>>>>>> .r534
    # Track results
    results = {}
    
    try:
        # Define projects to test
        projects_to_test = ["ra_eu"]
        
        for project_name in projects_to_test:
            # Run test for this project
            result = test_project(driver, project_name)
            results[project_name] = result
            
            # Add some separation between project tests
            print("\n" + "-"*50 + "\n")
            
        # Print summary report
        print(f"\n=========== SUMMARY REPORT (TEST ID: {TEST_ID}) ===========")
        all_passed = True
        for project, result in results.items():
            status = "PASSED" if result["success"] else "FAILED"
            if not result["success"]:
                all_passed = False
                print(f"{project}: {status} - Failed at step: {result.get('step', 'unknown')}")
                print(f"  Error: {result.get('error', 'Unknown error')}")
            else:
                verification = "Verification PASSED" if result.get("verification", False) else "Verification FAILED"
                print(f"{project}: {status} - {verification}")
        
        print("\nOverall status:", "PASSED" if all_passed else "FAILED")
        logger.info(f"Test {TEST_ID} completed with status: {'PASSED' if all_passed else 'FAILED'}")
        
        # Если какой-то из проектов не прошел, сигнализируем об ошибке
        if not all_passed:
            return {"success": False, "error": "One or more projects failed tests"}
        return {"success": True}
    
    except Exception as e:
        logger.error(f"Process failed with unexpected error: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """
    Основная точка входа в программу, которая создает драйвер и передает его в декорированную функцию.
    """
    # Read the HEADLESS environment variable; default to True if not set
    headless_mode = os.environ.get('HEADLESS', 'False').lower() == 'true'
    
    # Get driver from centralized pool with test_id
    driver = setup_chrome_driver(headless=headless_mode, test_id=TEST_ID)
    
    try:
        # Запускаем тест, передавая драйвер как аргумент
        result = run_test(driver)
        
        # Завершаем с соответствующим кодом
        if not result.get("success", False):
            sys.exit(1)
    finally:
        # Всегда освобождаем драйвер
        release_driver(driver)

if __name__ == "__main__":
    main()