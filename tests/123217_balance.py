# test_page_836_sales_buying.py
import os
import time
import logging
import uuid
from datetime import datetime

# Генерация уникального ID для теста
TEST_ID = f"page_836_sales_buying_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Import functions for working with centralized driver pool
from common.utils.driver_setup import setup_chrome_driver, release_driver

# Import workflow for login
from common.config.login.login_as_user import login_as_user

# Import logout function
from common.config.logout.logout_from_system import logout_from_system

# Import page info to get the URL
from projects.ra_eu.pages.page_836.page_info import get_page_836_url

# Import submit_form action
from common.pages.page_836.actions.submit_form import submit_form

# Import our workflow
from common.pages.page_830.workflow.check_sales_buying_balance import check_company_sales_buying_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configure directory for screenshots
SCREENSHOT_DIR = r"C:\Users\maxim.lupan\Desktop\E2E_Testing"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Timeouts for different operations
TIMEOUTS = {
    "login": 20,       # Timeout for login operations
    "action": 15,      # Timeout for form actions
    "navigation": 25,  # Timeout for navigation operations
    "page_load": 30    # Timeout for page loading
}

def take_error_screenshot(driver, name, project_name=None):
    """Take screenshot on error"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if project_name:
        filename = os.path.join(SCREENSHOT_DIR, f"{TEST_ID}_{project_name}_{name}_{timestamp}.png")
    else:
        filename = os.path.join(SCREENSHOT_DIR, f"{TEST_ID}_{name}_{timestamp}.png")
    
    try:
        driver.save_screenshot(filename)
        logger.info(f"Error screenshot saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"Failed to take error screenshot: {str(e)}")
        return None

def test_project(driver, project_name):
    """Run test for a specific project"""
    logger.info(f"======= Starting test for project: {project_name} =======")
    
    # Сохраняем оригинальную вкладку
    original_handle = driver.current_window_handle
    
    try:
        # Step 1: Login with user "ml"
        logger.info(f"Starting login process for project {project_name}")
        login_result = login_as_user(driver, project_name=project_name, user_type="ml", timeouts=TIMEOUTS)
        
        if not login_result["success"]:
            error_screenshot = take_error_screenshot(driver, "login", project_name)
            logger.error(f"Login error for {project_name}: {login_result['error']}")
            return {"success": False, "error": login_result["error"], "step": "login", "screenshot": error_screenshot}
        
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
            error_screenshot = take_error_screenshot(driver, "navigation", project_name)
            error_msg = f"Error during navigation to page 836 for {project_name}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": str(e), "step": "navigation", "screenshot": error_screenshot}
        
        # Step 2.5: Submit form
        logger.info(f"Submitting form on page 836 for {project_name}")
        try:
            submit_result = submit_form(driver, timeouts=TIMEOUTS)
            
            if not submit_result["success"]:
                error_screenshot = take_error_screenshot(driver, "form_submission", project_name)
                logger.error(f"Form submission error for {project_name}: {submit_result['error']}")
                return {"success": False, "error": submit_result["error"], "step": "form_submission", "screenshot": error_screenshot}
                
            logger.info(f"Form submitted successfully for {project_name}")
            
        except Exception as e:
            error_screenshot = take_error_screenshot(driver, "form_submission_error", project_name)
            logger.error(f"Error during form submission for {project_name}: {str(e)}")
            return {"success": False, "error": str(e), "step": "form_submission", "screenshot": error_screenshot}
        
        # Проверяем, появились ли новые вкладки после отправки формы
        current_handles = driver.window_handles
        new_tab = None
        
        if len(current_handles) > 1:
            # Переключаемся на новую вкладку (если открылась)
            for handle in current_handles:
                if handle != original_handle:
                    new_tab = handle
                    driver.switch_to.window(new_tab)
                    logger.info(f"Switched to new tab for {project_name}. URL: {driver.current_url}")
                    break
        
        # Step 3: Run workflow to check company sales and buying values
        logger.info(f"Running company sales and buying check workflow for {project_name}")
        try:
            workflow_result = check_company_sales_buying_workflow(driver, timeouts=TIMEOUTS)
            
            if not workflow_result["success"]:
                failed_step = workflow_result.get("failed_step", "unknown")
                error_screenshot = take_error_screenshot(driver, f"workflow_{failed_step}", project_name)
                
                error_message = f"Workflow failed for {project_name} at step '{failed_step}': {workflow_result['error']}"
                logger.error(error_message)
                return {"success": False, "error": workflow_result["error"], "step": failed_step, "screenshot": error_screenshot}
            
            # Собираем данные результатов для отчета
            result = {
                "success": True, 
                "steps_completed": workflow_result.get("steps_completed", [])
            }
            
            # Добавляем данные о sales/buying если они есть
            if "sales_text" in workflow_result:
                result["sales_text"] = workflow_result["sales_text"]
            if "buying_text" in workflow_result:
                result["buying_text"] = workflow_result["buying_text"]
                
            logger.info(f"Workflow completed successfully for {project_name}")
            return result
            
        except Exception as e:
            error_screenshot = take_error_screenshot(driver, "workflow_error", project_name)
            logger.error(f"Error during workflow execution for {project_name}: {str(e)}")
            return {"success": False, "error": str(e), "step": "workflow", "screenshot": error_screenshot}
    
    finally:
        # Закрываем все вкладки кроме оригинальной
        try:
            current_handles = driver.window_handles
            for handle in current_handles:
                if handle != original_handle:
                    driver.switch_to.window(handle)
                    logger.info(f"Closing tab: {driver.current_url}")
                    driver.close()
            
            # Возвращаемся на основную вкладку
            driver.switch_to.window(original_handle)
            logger.info(f"Switched back to original tab for {project_name}")
            
            # Выполняем logout
            logout_from_system(driver, project_name)
            logger.info(f"Logged out from {project_name}")
        except Exception as e:
            logger.warning(f"Error during cleanup for {project_name}: {str(e)}")

def main():
    logger.info(f"Starting test execution with ID: {TEST_ID}")
    
    # Read the HEADLESS environment variable; default to False if not set
    headless_mode = os.environ.get('HEADLESS', 'False').lower() == 'true'
    
    # Define projects to test - можно добавлять или удалять проекты по необходимости
    projects_to_test = ["ra_eu", "at_eu"]
    
    # Get driver from centralized pool with test_id
    driver = setup_chrome_driver(headless=headless_mode, test_id=TEST_ID)
    
    # Track results
    results = {}
    
    try:
        # Начинаем с чистой страницы
        driver.get("about:blank")
        
        for project_name in projects_to_test:
            # Run test for this project
            result = test_project(driver, project_name)
            results[project_name] = result
            
            # Add some separation between project tests
            print("\n" + "-"*50 + "\n")
            
            # Очищаем куки и снова открываем пустую страницу для следующего проекта
            driver.delete_all_cookies()
            driver.get("about:blank")
            
    except Exception as e:
        logger.error(f"Process failed with unexpected error: {str(e)}")
        take_error_screenshot(driver, "unexpected_error")
        raise  # Re-raise for error handling
    finally:
        release_driver(driver)
    
    # Print summary report
    print(f"\n=========== SUMMARY REPORT (TEST ID: {TEST_ID}) ===========")
    all_passed = True
    for project, result in results.items():
        status = "PASSED" if result.get("success", False) else "FAILED"
        if not result.get("success", False):
            all_passed = False
            print(f"{project}: {status} - Failed at step: {result.get('step', 'unknown')}")
            print(f"  Error: {result.get('error', 'Unknown error')}")
            if "screenshot" in result:
                print(f"  Screenshot: {result['screenshot']}")
        else:
            print(f"{project}: {status}")
            if "sales_text" in result:
                print(f"  SALES: {result['sales_text']}")
            if "buying_text" in result:
                print(f"  BUYING: {result['buying_text']}")
            
            steps_completed = result.get("steps_completed", [])
            print(f"  Completed steps: {len(steps_completed)}")
    
    print("\nOverall status:", "PASSED" if all_passed else "FAILED")
    logger.info(f"Test {TEST_ID} completed with status: {'PASSED' if all_passed else 'FAILED'}")
    
    # Return status for potential Jenkins integration
    if not all_passed:
        raise Exception("One or more projects failed tests")

if __name__ == "__main__":
    main()