# tests/test_925_search_offers.py
import os
import time
import logging
import sys
import uuid
import sys
from datetime import datetime

# Generate a unique test ID for this test run
TEST_ID = f"page_925_offers_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Import functions for working with centralized driver pool
from common.utils.driver_setup import setup_chrome_driver, release_driver

# Import workflow for login
from common.config.login.login_as_user import login_as_user

# Import logout function
from common.config.logout.logout_from_system import logout_from_system

# Import page info to get the URL
from common.pages.page_925.page_info import get_page_925_url, get_si_editor_url

# Import our complete workflows
from common.pages.page_925.workflow.search_yes_offers import search_yes_offers_workflow
from common.pages.page_925.workflow.search_no_offers import search_no_offers_workflow

# Import SI editor verification action
from common.pages.page_925.actions.verify_si_editor import verify_si_editor

# Import error handling decorator
from common.utils.error_handling import jenkins_aware

# Import retry decorator
from common.utils.retry_decorator import with_retry

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

@with_retry(max_attempts=3, retry_delay=5)
def test_project(driver, project_name):
    """
    Run test for a specific project.
    Если хотим, чтобы jenkins_aware() ловил ошибку и делал скриншоты,
    необходимо выбрасывать Exception в случае неудачи.
    """
    logger.info(f"======= Starting test for project: {project_name} =======")
    
    try:
        # 1. Login
        logger.info(f"Starting login process for project {project_name}")
        login_result = login_as_user(driver, user_type="dd", project_name=project_name, timeouts=TIMEOUTS)
        if not login_result["success"]:
            logger.error(f"Login error for {project_name}: {login_result['error']}")
            raise Exception(f"Login error: {login_result['error']}")

        logger.info(f"Login successful for {project_name}")
        
        # 2. Navigate to page 925
        logger.info(f"Navigating to page 925 for {project_name}")
        try:
            page_url = get_page_925_url(project_name)
            if not page_url:
                error_msg = f"Could not get URL for page 925 in project {project_name}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            driver.get(page_url)
            time.sleep(2)  # Give page time to load
            logger.info(f"Successfully navigated to page 925. URL: {driver.current_url}")
            
        except Exception as e:
            error_msg = f"Error during navigation to page 925 for {project_name}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # 3. Run 'Yes' offers workflow
        logger.info(f"Running 'Yes' offers search workflow for {project_name}")
        try:
            yes_workflow_result = search_yes_offers_workflow(driver, timeouts=TIMEOUTS)
            if not yes_workflow_result["success"]:
                failed_step = yes_workflow_result.get("failed_step", "unknown")
                error_message = (
                    f"'Yes' workflow failed for {project_name} at step '{failed_step}': "
                    f"{yes_workflow_result['error']}"
                )
                logger.error(error_message)
                raise Exception(error_message)
            
            # Store the SI ID for verification
            yes_si_id = yes_workflow_result.get("si_id")
            logger.info(f"Found SI ID from 'Yes' workflow: {yes_si_id}")
            
            if yes_si_id:
                # Navigate to the SI editor
                si_editor_url = get_si_editor_url(project_name, yes_si_id)
                logger.info(f"Navigating to SI editor URL: {si_editor_url}")
                driver.get(si_editor_url)
                time.sleep(2)
                
                # Verify SI editor page (expected offers table to be found)
                verify_result = verify_si_editor(driver, yes_si_id, timeouts=TIMEOUTS, check_for_offers='yes')
                if not verify_result["success"]:
                    error_msg = f"SI editor verification failed: {verify_result['error']}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                logger.info(f"Successfully verified SI editor with offers for ID: {yes_si_id}")
            else:
                logger.warning(f"No SI ID found in 'Yes' workflow results for {project_name}")
            
            # Navigate back to the search page
            driver.get(page_url)
            time.sleep(2)
            
        except Exception as e:
            error_msg = f"Error during 'Yes' workflow execution for {project_name}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # 4. Run 'No' offers workflow
        logger.info(f"Running 'No' offers search workflow for {project_name}")
        try:
            no_workflow_result = search_no_offers_workflow(driver, timeouts=TIMEOUTS)
            if not no_workflow_result["success"]:
                failed_step = no_workflow_result.get("failed_step", "unknown")
                error_message = (
                    f"'No' workflow failed for {project_name} at step '{failed_step}': "
                    f"{no_workflow_result['error']}"
                )
                logger.error(error_message)
                raise Exception(error_message)
            
            # Store the SI ID for verification
            no_si_id = no_workflow_result.get("si_id")
            logger.info(f"Found SI ID from 'No' workflow: {no_si_id}")
            
            if no_si_id:
                # Navigate to the SI editor
                si_editor_url = get_si_editor_url(project_name, no_si_id)
                logger.info(f"Navigating to SI editor URL: {si_editor_url}")
                driver.get(si_editor_url)
                time.sleep(2)
                
                # Verify SI editor page (expected NO offers table)
                verify_result = verify_si_editor(driver, no_si_id, timeouts=TIMEOUTS, check_for_offers='no')
                if not verify_result["success"]:
                    error_msg = f"SI editor verification failed: {verify_result['error']}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                logger.info(f"Successfully verified SI editor without offers for ID: {no_si_id}")
            else:
                logger.warning(f"No SI ID found in 'No' workflow results for {project_name}")
            
        except Exception as e:
            error_msg = f"Error during 'No' workflow execution for {project_name}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Если дошли до сюда без исключений, значит всё хорошо
        return {"success": True}

    finally:
        # Обязательно логаут, даже если произошло исключение
        logout_from_system(driver, project_name)

@jenkins_aware()
def run_test(driver):
    """
    Main test execution function that accepts a driver as an argument.
    This allows the jenkins_aware decorator to create screenshots on errors.
    """
    logger.info(f"Starting test execution with ID: {TEST_ID}")
    results = {}
    
    try:
        projects_to_test = ["ra_eu", "at_eu", "ag_eu", "sm_us", "ho_eu", "lt_eu", "dr_eu", "argon", "aro_eu", "roc"]
        
        for project_name in projects_to_test:
            print(f"\n=== Project: {project_name} ===\n")
            try:
                result = test_project(driver, project_name)
                results[project_name] = result
            except Exception as e:
                # Если проект упал, сохраним инфу и пойдём к следующему
                results[project_name] = {"success": False, "error": str(e)}
            
            print("-" * 50)
        
        # Сформируем общий отчёт
        print(f"\n======= SUMMARY REPORT (TEST ID: {TEST_ID}) =======")
        all_passed = True
        failed_projects = []
        
        for project, result in results.items():
            status = "PASSED" if result.get("success") else "FAILED"
            if not result.get("success"):
                all_passed = False
                failed_projects.append(project)
                print(f"{project}: {status} - Error: {result.get('error')}")
            else:
                print(f"{project}: {status}")
        
        print("\nOverall status:", "PASSED" if all_passed else "FAILED")
        logger.info(f"Test {TEST_ID} completed with status: {'PASSED' if all_passed else 'FAILED'}")
        
        # Если есть неуспешные проекты, выходим с кодом ошибки
        if not all_passed:
            error_msg = f"Failed projects: {', '.join(failed_projects)}"
            logger.error(error_msg)
            logger.error("Exiting with error code 1")
            sys.exit(1)
        
        return {"success": True}
    
    except Exception as e:
        logger.error(f"Process failed with unexpected error: {str(e)}")
        # Выходим с кодом ошибки
        sys.exit(1)

def main():
    """
    Main entry point that creates the driver and passes it to the decorated function.
    """
    headless_mode = os.environ.get('HEADLESS', 'False').lower() == 'true'
    driver = setup_chrome_driver(headless=headless_mode, test_id=TEST_ID)
    
    try:
        run_test(driver)
        # Если всё прошло, код возврата 0
        sys.exit(0)
    except Exception as e:
        # Код возврата 1, сигнализируя об ошибке
        sys.exit(1)
    finally:
        release_driver(driver)

if __name__ == "__main__":
    main()
