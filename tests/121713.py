"""
Test for extracting company email addresses and checking orders on the logistics page
Extraction of company email addresses and order verification
"""
import logging
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.utils.error_handling import jenkins_aware
from common.utils.retry_decorator import with_retry
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system
from common.pages.page_830.page_info import get_page_830_url
from common.pages.page_830.locators import Page830Locators
from common.pages.page_830.actions.verify_email_addresses import verify_email_addresses
# Import for generating a link to the logistics page
from common.pages.page_907.generate_order_url import generate_order_url
# Import of new function for checking email in the template
from common.pages.page_907.actions.verify_email_in_template import click_generate_template_and_verify_email

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger('test')

# Test configuration - added all projects and their company IDs
COMPANY_IDS = {
    "ra_eu": "517820",     # https://stage15.office.ratrading.eu/sage/
    "lt_eu": "161428",     # https://stage15.office.laniustoys.com/sage/
    "ag_eu": "206666",     # https://stage15.office.agavasystem.com/sage/
    "sm_eu": "830813",     # https://stage15.office.sovasystem.com/sage/
    "et_eu": "410753",     # https://stage15.office.eminiasystem.com/sage/
    "dr_eu": "101037",     # https://stage15.office.dbreactor.com/sage/
    "ho_eu": "107247",    # https://stage15.office.horustrading.eu/sage/
    "at_eu": "183262",     # https://stage15.office.atlastradingworld.com/sage/
    "aro_eu": "431370",    # https://stage15.office.arotrading.eu/sage/
    "argon": "36705",      # https://stage15.office.argontrading.de/sage/
    "roc": "15901"         # https://stage15.office.roctrading.de/sage/
}

@jenkins_aware()
@with_retry(max_attempts=2, retry_delay=3)
def test_company_emails_and_order(driver, project_code, user_type="ml"):
    """
    Extracts company email addresses on page 830 and checks the order on the logistics page
    
    Args:
        driver: Already initialized Selenium driver
        project_code: Project code (e.g., "ra_eu")
        user_type: User type for login (default "ml")
        
    Returns:
        dict: Test result {'success': bool, 'error': str or None, 'emails': list, 'order_id': str}
    """
    logger.info(f"Starting email extraction and order verification for project {project_code}")
    
    # Инициализируем результат со статусом успеха по умолчанию
    result = {
        "success": True,
        "error": None,
        "emails": None,
        "order_check": None,
        "project_code": project_code,
        "company_id": COMPANY_IDS.get(project_code, "Unknown")
    }
    
    try:
        # Open a new tab for this project
        logger.info(f"Opening a new tab for project {project_code}")
        # Use JavaScript to create a new tab
        driver.execute_script("window.open('about:blank', '_blank');")
        
        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])
        
        # Login to the system
        login_result = login_as_user(driver, project_code, user_type)
        if not login_result['success']:
            result["success"] = False
            result["error"] = f"Login error: {login_result['error']}"
            return result
        
        # Get company ID for the project
        company_id = COMPANY_IDS.get(project_code)
        if not company_id:
            result["success"] = False
            result["error"] = f"Company ID not configured for project {project_code}"
            return result
        
        # Navigate to page 830
        page_url = get_page_830_url(project_code, company_id)
        if not page_url:
            result["success"] = False
            result["error"] = "Failed to get page URL"
            return result
        
        driver.get(page_url)
        time.sleep(2)  # Give the page time to load
        
        # Click on the "Show not shipped orders" checkbox before extracting email addresses
        checkbox_clicked = False
        try:
            logger.info("Clicking on 'Show not shipped orders' checkbox")
            checkbox = driver.find_element(By.ID, "show_not_shipped_orders")
            
            # Use JavaScript to click on the checkbox, as a regular click might not work
            driver.execute_script("arguments[0].click();", checkbox)
            
            # Wait for the page to update after clicking the checkbox
            time.sleep(2)
            
            logger.info("'Show not shipped orders' checkbox successfully activated")
            checkbox_clicked = True
        except Exception as e:
            logger.warning(f"Failed to click on 'Show not shipped orders' checkbox: {str(e)}")
            # Добавляем предупреждение в результат, но не помечаем тест как неудачный,
            # так как это не критичная проблема (чекбокс может быть опциональным)
            result["checkbox_warning"] = f"Failed to click on checkbox: {str(e)}"
        
        # Extract email addresses
        email_info = verify_email_addresses(driver)
        result["emails"] = email_info
        
        if not email_info:
            logger.warning("No email addresses found")
            result["success"] = False
            result["error"] = "No email addresses found"
            # Продолжаем выполнение, чтобы попытаться выполнить другие шаги теста
        else:
            logger.info(f"Successfully extracted {len(email_info)} email addresses")
        
        # Check for locator presence
        try:
            logger.info(f"Checking SALES_ORDER_NUMBER_CELL locator: {Page830Locators.SALES_ORDER_NUMBER_CELL}")
        except AttributeError:
            logger.error("SALES_ORDER_NUMBER_CELL locator is not defined in Page830Locators class")
            result["success"] = False
            result["error"] = "SALES_ORDER_NUMBER_CELL locator is not defined"
            return result
        except Exception as e:
            logger.error(f"Error when checking locator: {str(e)}")
            result["success"] = False
            result["error"] = f"Error with locator: {str(e)}"
            return result

        # Extract order number from the table
        order_id = None
        try:
            logger.info("STARTING order number extraction from the table")
            # Use locator from the locators file
            order_cell = driver.find_element(*Page830Locators.SALES_ORDER_NUMBER_CELL)
            order_id = order_cell.text.strip()
            logger.info(f"Extracted order number: {order_id}")
    
            if not order_id:
                logger.warning("Order number is empty")
                result["success"] = False
                result["error"] = "Order number is empty"
        
        except Exception as e:
            logger.error(f"Error when extracting order number: {str(e)}")
            result["success"] = False
            result["error"] = f"Failed to extract order number: {str(e)}"
            # Присваиваем order_id = None, чтобы следующий блок был пропущен
            order_id = None
        
        order_check_result = None
        if order_id:
            # Generate a direct link to the logistics page with the order
            tracking_url = generate_order_url(project_code, order_id)
            logger.info(f"Generated link to order: {tracking_url}")
            
            # Open another new tab to check the order on the logistics page
            driver.execute_script("window.open('about:blank', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            
            # Navigate to the logistics page
            logger.info(f"Navigating to the logistics page for order {order_id}")
            driver.get(tracking_url)
            time.sleep(2)  # Give the page time to load
            
            # Check login to gr_eu (using improved login_as_user function)
            login_result = login_as_user(driver, "gr_eu", user_type)
            # If already logged in, the function will return {'success': True, 'already_logged_in': True}
            # If had to login again, {'success': True, 'already_logged_in': False}
            if not login_result['success']:
                logger.error(f"Error logging into gr_eu: {login_result['error']}")
                order_check_result = {"success": False, "error": f"Login error: {login_result['error']}"}
                result["success"] = False
                result["error"] = f"Failed to login to gr_eu: {login_result['error']}"
            else:
                already_logged = login_result.get('already_logged_in', False)
                state_msg = "Using existing session" if already_logged else "Performed new login"
                logger.info(f"Successfully logged into gr_eu. {state_msg}")
                
                # Navigate to the logistics page using the direct link again
                driver.get(tracking_url)
                time.sleep(5)  # Give more time for the page and results to load
                
                # Results should load automatically since we are using a direct link
                logger.info("Order page loaded")
                
                # Find the business email from the list of found email addresses
                business_email = None
                if email_info:
                    for email_item in email_info:
                        if email_item.get("type", "").lower() == "business":
                            business_email = email_item.get("email")
                            break
                
                # If we found a business email, check it in the template
                template_check_result = None
                if business_email:
                    logger.info(f"Business email found: {business_email}")
                    # Click on the template generation button and check the email
                    template_check_result = click_generate_template_and_verify_email(driver, business_email)
                    logger.info(f"Email verification result in template: {template_check_result}")
                    
                    # Обновляем статус теста на основе проверки шаблона
                    if not template_check_result.get("success", False) or not template_check_result.get("matches", False):
                        result["success"] = False
                        result["error"] = "Email in template doesn't match the found business email"
                else:
                    logger.warning("Business email not found in the address list")
                    if result["success"]:  # Только если пока тест был успешен
                        result["success"] = False
                        result["error"] = "Business email not found for template verification"
                
                order_check_result = {
                    "success": True, 
                    "order_id": order_id, 
                    "url": tracking_url,
                    "template_check": template_check_result
                }
            
            # Close the gr_eu tab and switch back
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
        else:
            # Если order_id не был найден, устанавливаем success = False
            # только если статус еще не был изменен на False ранее
            if result["success"]:
                result["success"] = False
                result["error"] = "No order ID found"
        
        # Записываем результат проверки заказа в общий результат
        result["order_check"] = order_check_result
        
        # Logout from the system for the current project (NOT for gr_eu)
        # Skip logout for gr_eu to preserve the session for subsequent tests
        logout_from_system(driver, project_code, skip_for_projects=["gr_eu"])
            
        # Close the current tab and switch to the first tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
        return result
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        
        # В случае исключения, устанавливаем success = False
        result["success"] = False
        result["error"] = str(e)
        
        # In case of error, close all tabs except the first one
        try:
            current_handle = driver.current_window_handle
            for handle in driver.window_handles[1:]:
                driver.switch_to.window(handle)
                driver.close()
            
            # Switch to the first tab
            driver.switch_to.window(driver.window_handles[0])
        except:
            # If unable to close tabs, continue execution
            pass
            
        return result

def run_tests_for_all_projects():
    """
    Runs tests for all projects defined in COMPANY_IDS,
    using one browser and opening new tabs for each project
    
    Returns:
        dict: Test results for all projects
    """
    results = {}
    driver = None
    
    try:
        # Set up the driver once for all tests
        driver = setup_chrome_driver(headless=False, test_id="test_830_907_all_projects")
        
        # Load an empty page in the first tab
        driver.get("about:blank")
        
        # Go through all projects
        for project_code in COMPANY_IDS.keys():
            logger.info(f"Starting test for project: {project_code}")
            
            # Обернем вызов в try-except, чтобы гарантировать, что все проекты будут обработаны
            try:
                result = test_company_emails_and_order(driver, project_code)
            except Exception as e:
                logger.error(f"Unhandled exception in test for {project_code}: {str(e)}")
                result = {
                    "success": False, 
                    "error": f"Unhandled exception: {str(e)}", 
                    "project_code": project_code,
                    "company_id": COMPANY_IDS.get(project_code, "Unknown")
                }
                
            results[project_code] = result
            
            # Small pause between projects
            time.sleep(2)
        
        return results
    
    finally:
        # Close the browser after running all tests
        if driver:
            release_driver(driver)

if __name__ == "__main__":
    # Run tests for all projects
    all_results = run_tests_for_all_projects()
    
    # Output summary of results
    logger.info("\n\n== RESULTS SUMMARY ==")
    successful_projects = 0
    failed_projects = []
    
    for project, result in all_results.items():
        status = "SUCCESS" if result.get("success", False) else "ERROR"
        company_id = COMPANY_IDS.get(project, "Unknown")
        
        if result.get("success", False):
            successful_projects += 1
        else:
            failed_projects.append(project)
            
        logger.info(f"Project: {project} (ID: {company_id}) - {status}")
        if not result.get("success", False):
            error_msg = result.get("error", "Unknown error")
            logger.info(f"  Error: {error_msg}")
            
        # Information about found email addresses
        if "emails" in result and result["emails"]:
            logger.info(f"  Found {len(result['emails'])} email addresses")
        elif "emails" in result:
            logger.info("  No email addresses found")
            
        # Information about order verification
        if "order_check" in result and result["order_check"]:
            order_check = result["order_check"]
            logger.info(f"  Verified order: {order_check.get('order_id', 'Unknown')}")
            
            # Email template check result
            if "template_check" in order_check and order_check["template_check"]:
                template_check = order_check["template_check"]
                if template_check.get("matches", False):
                    logger.info("  Email in template matches the company's business email")
                else:
                    logger.warning(f"  Email in template DOES NOT match the company's business email: {template_check.get('email_found')}")
        elif "error" in result and "order" in result.get("error", "").lower():
            logger.info("  Order verification failed")
                    
    # Final statistics
    logger.info(f"\nTotal: {successful_projects} out of {len(all_results)} projects successful")
    
    # If any project failed, exit with code 1
    if failed_projects:
        logger.error(f"Failed projects: {', '.join(failed_projects)}")
        logger.error("Exiting with error code 1")
        sys.exit(1)