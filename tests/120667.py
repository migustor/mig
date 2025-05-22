from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # Добавляем импорт Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
import logging
import sys
import os
import uuid
from datetime import datetime
from typing import Dict, Tuple, Callable, Any, Optional
import functools
import time
# Импортируем функции управления драйвером из driver_setup.py
from common.utils.driver_setup import setup_chrome_driver, release_driver

TEST_ID = f"carrier_message_check_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Настройка директории для скриншотов
screenshot_dir = r"J:\PUB5\E2E_Testing"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Упрощенные таймауты для разных операций
TIMEOUTS = {
    "login": 30,         # Таймаут для элементов логина
    "page_load": 40,     # Таймаут для загрузки страницы
    "dropdown": 25,      # Таймаут для выпадающих списков
    "button": 20,        # Таймаут для кнопок
    "message": 20,       # Таймаут для сообщений
    "carrier": 25        # Таймаут для элементов перевозчика
}

# Функция для создания скриншотов при ошибках
def take_error_screenshot(driver, name, project_id=None):
    """Делает скриншот страницы при ошибке"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if project_id:
        filename = os.path.join(SCREENSHOT_DIR, f"error_{project_id}_{name}_{timestamp}.png")
    else:
        filename = os.path.join(SCREENSHOT_DIR, f"error_{name}_{timestamp}.png")
    
    try:
        driver.save_screenshot(filename)
        logging.info(f"Error screenshot saved to {filename}")
        return filename
    except Exception as e:
        logging.error(f"Failed to take error screenshot: {str(e)}")
        return None

# Add the retry decorator implementation
def retry_on_timeout(max_attempts: int = 3, delay: int = 2) -> Callable:
    """
    Decorator that retries a function on TimeoutException.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds

    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception: Optional[Exception] = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except TimeoutException as e:
                    last_exception = e
                    if attempt < max_attempts - 1:  # Don't log on last attempt
                        logging.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed with timeout. "
                            f"Refreshing page and retrying in {delay} seconds..."
                        )
                        # Assuming first argument is the driver
                        if args and hasattr(args[0], 'refresh'):
                            args[0].refresh()
                            # Делаем скриншот при ошибке таймаута
                            if 'project_id' in kwargs:
                                take_error_screenshot(args[0], f"timeout_retry_{attempt+1}", kwargs['project_id'])
                            else:
                                take_error_screenshot(args[0], f"timeout_retry_{attempt+1}")
                        sleep(delay)
                    continue
                except Exception as e:
                    logging.error(f"Non-timeout error occurred: {str(e)}")
                    if args and hasattr(args[0], 'save_screenshot'):
                        if 'project_id' in kwargs:
                            take_error_screenshot(args[0], "non_timeout_error", kwargs['project_id'])
                        else:
                            take_error_screenshot(args[0], "non_timeout_error")
                    raise

            # If we've exhausted all attempts, log and raise the last exception
            logging.error(
                f"All {max_attempts} attempts failed. "
                f"Last error: {str(last_exception)}"
            )
            # Делаем скриншот при исчерпании всех попыток
            if args and hasattr(args[0], 'save_screenshot'):
                if 'project_id' in kwargs:
                    take_error_screenshot(args[0], "all_attempts_failed", kwargs['project_id'])
                else:
                    take_error_screenshot(args[0], "all_attempts_failed")
            raise last_exception

        return wrapper
    return decorator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' 
)

# Project URLs mapping
PROJECTS = {
    "at_eu": "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&project_id=at_eu&po_id=285&order_type=po",
    "ag_eu": "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&project_id=ag_eu&po_id=4482&order_type=po",
    "ra_eu": "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&project_id=ra_eu&po_id=44489&order_type=po",
    "sm_eu": "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&project_id=sm_eu&po_id=228571&order_type=po",
    "sm_us": "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&project_id=sm_us&po_id=4435&order_type=po",
    "lt_eu": "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&project_id=lt_eu&po_id=41632&order_type=po",
    "dr_eu": "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&project_id=dr_eu&po_id=618&order_type=po",
    "ho_eu": "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&project_id=ho_eu&po_id=618&order_type=po",
    "et_eu": "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&project_id=et_eu&po_id=132584&order_type=po",
    "argon": "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&project_id=argon&po_id=10&order_type=po",
    "aro_eu": "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&project_id=aro_eu&po_id=16&order_type=po"
}

CARRIERS = {
    "carrier1": {
        "url": "https://stage15.office.grafit.md/sage/index.cfm?page_id=24&phase=edit&dummy=&carrier_id=2224",
        "name": "transfreight_ag",
        "expected_message": "Please add for Transfreight 15 euro for customs documents"
    },
    "carrier2": {
        "url": "https://stage15.office.grafit.md/sage/index.cfm?page_id=24&phase=edit&dummy=&carrier_id=2099",
        "name": "instacargo_ltd",
        "expected_message": "If the Instacargo ships with Fedex, then add 15 euro for Aufwendungspauschale"
    }
}

def login_to_system(driver, username, password, url):
    """Login to the system with provided credentials."""
    logging.info(f"Logging in as {username}")
    try:
        driver.get(url)
        username_input = WebDriverWait(driver, TIMEOUTS["login"]).until(
            EC.presence_of_element_located((By.ID, "login_name"))
        )
        password_input = WebDriverWait(driver, TIMEOUTS["login"]).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()
        sleep(3)
        logging.info("Login successful")
        return True
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        screenshot_path = take_error_screenshot(driver, "login_failed")
        logging.error(f"Error screenshot: {screenshot_path}")
        return False

def get_active_projects_for_carrier(driver, carrier_url):
    """Get list of active projects for specific carrier."""
    try:
        driver.get(carrier_url)
        sleep(3)

        active_projects = {}
        # Find all status dropdowns
        status_dropdowns = driver.find_elements(By.CSS_SELECTOR,
            'select.form-control.form-select-sm.xmb10.carrier_status_system_name.details')

        for dropdown in status_dropdowns:
            try:
                project_uuid = dropdown.get_attribute("project_uuid")
                select = Select(dropdown)
                selected_option = select.first_selected_option
                status = selected_option.text.strip()

                active_projects[project_uuid] = (status == "Active")
                logging.info(f"Project {project_uuid} status: {status}")

            except Exception as e:
                logging.error(f"Error processing project status: {str(e)}")
                take_error_screenshot(driver, f"project_status_{project_uuid}")
                continue

        return active_projects
    except Exception as e:
        logging.error(f"Error checking active projects: {str(e)}")
        take_error_screenshot(driver, "active_projects_error")
        return {}

def click_success_button(driver):
    """Clicks on the success button using the new selector."""
    try:
        # Using the new selector that looks for buttons within div[id^="offer_btn_"]
        success_button = WebDriverWait(driver, TIMEOUTS["button"]).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[id^="offer_btn_"] .btn-success'))
        )
        success_button.click()
        logging.info("Successfully clicked on success button")
        return True
    except Exception as e:
        logging.error(f"Could not click success button: {str(e)}")
        take_error_screenshot(driver, "success_button_error")
        return False

def check_carrier_message(driver, carrier_value, expected_message, project_id=None):
    """Check carrier message after selection."""
    try:
        dropdown = WebDriverWait(driver, TIMEOUTS["dropdown"]).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select.form-control.offer_carrier_id'))
        )
        select = Select(dropdown)

        options = [option.get_attribute('value') for option in select.options]
        if carrier_value not in options:
            take_error_screenshot(driver, "carrier_not_found", project_id)
            return False, f"Carrier option '{carrier_value}' not found in dropdown"

        carrier_option = next(opt for opt in select.options if opt.get_attribute('value') == carrier_value)
        if carrier_option.get_attribute('disabled'):
            take_error_screenshot(driver, "carrier_disabled", project_id)
            return False, f"Carrier option '{carrier_value}' is disabled"

        try:
            select.select_by_value(carrier_value)
        except Exception:
            take_error_screenshot(driver, "carrier_select_error", project_id)
            return False, "Could not select carrier (element might be not visible or interactive)"

        logging.info(f"Selected carrier: {carrier_value}")
        sleep(1)

        try:
            message_element = WebDriverWait(driver, TIMEOUTS["message"]).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#add_offer_form > div.additional_cost > span'))
            )
            actual_message = message_element.text.strip()

            if actual_message == expected_message:
                logging.info(f"Message verification successful for {carrier_value}")
                return True, actual_message
            else:
                logging.error(f"Message mismatch for {carrier_value}")
                take_error_screenshot(driver, "message_mismatch", project_id)
                return False, f"Message does not match expected text"

        except TimeoutException:
            take_error_screenshot(driver, "message_not_found", project_id)
            return False, "Warning message element not found"

    except Exception as e:
        take_error_screenshot(driver, "carrier_check_error", project_id)
        if "not visible" in str(e):
            return False, "Element not visible or interactive"
        return False, "Failed to complete carrier check"

@retry_on_timeout(max_attempts=3, delay=2)
def wait_for_page_load(driver, project_id=None) -> bool:
    """Wait for page to load completely with retry logic."""
    WebDriverWait(driver, TIMEOUTS["page_load"]).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    return True

@retry_on_timeout(max_attempts=3, delay=2)
def wait_and_click_success_button(driver, project_id=None) -> bool:
    """Wait for and click success button with retry logic."""
    success_button = WebDriverWait(driver, TIMEOUTS["button"]).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[id^="offer_btn_"] .btn-success'))
    )
    success_button.click()
    return True

@retry_on_timeout(max_attempts=3, delay=2)
def wait_and_check_carrier(driver, carrier_value: str, expected_message: str, project_id=None) -> Tuple[bool, str]:
    """Wait for carrier dropdown and check message with retry logic."""
    dropdown = WebDriverWait(driver, TIMEOUTS["dropdown"]).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'select.form-control.offer_carrier_id'))
    )
    select = Select(dropdown)

    options = [option.get_attribute('value') for option in select.options]
    if carrier_value not in options:
        take_error_screenshot(driver, "carrier_not_found_wait", project_id)
        return False, f"Carrier option '{carrier_value}' not found in dropdown"

    select.select_by_value(carrier_value)
    sleep(1)

    message_element = WebDriverWait(driver, TIMEOUTS["message"]).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#add_offer_form > div.additional_cost > span'))
    )
    actual_message = message_element.text.strip()

    if actual_message != expected_message:
        take_error_screenshot(driver, "message_mismatch_wait", project_id)
        
    return actual_message == expected_message, actual_message

def check_project(driver, project_id: str, project_url: str, carrier_info: dict) -> Dict:
    """Check specific project for carrier message with enhanced error handling."""
    project_results = {
        "success": False,
        "navigation_steps": {
            "Page Load": False,
            "Success Button": False
        },
        "carrier_check": {
            "success": False,
            "expected_message": carrier_info["expected_message"],
            "actual_message": ""
        }
    }

    try:
        logging.info(f"Checking project: {project_id}")
        driver.get(project_url)

        # Wait for page load with retry
        if not wait_for_page_load(driver, project_id=project_id):
            project_results["carrier_check"]["actual_message"] = "Page failed to load completely"
            take_error_screenshot(driver, "page_load_failed", project_id)
            return project_results

        project_results["navigation_steps"]["Page Load"] = True

        # Click success button with retry
        if not wait_and_click_success_button(driver, project_id=project_id):
            project_results["carrier_check"]["actual_message"] = "Could not proceed: Success button not clickable"
            take_error_screenshot(driver, "success_button_failed", project_id)
            return project_results

        project_results["navigation_steps"]["Success Button"] = True

        # Check carrier message with retry
        success, actual_message = wait_and_check_carrier(
            driver,
            carrier_info["name"],
            carrier_info["expected_message"],
            project_id=project_id
        )

        project_results["carrier_check"]["success"] = success
        project_results["carrier_check"]["actual_message"] = actual_message

        project_results["success"] = all([
            all(project_results["navigation_steps"].values()),
            project_results["carrier_check"]["success"]
        ])

        if not project_results["success"]:
            take_error_screenshot(driver, "project_check_failed", project_id)

    except Exception as e:
        logging.error(f"Error checking project {project_id}: {str(e)}")
        take_error_screenshot(driver, "project_check_exception", project_id)
        project_results["carrier_check"]["actual_message"] = f"Failed to complete check: {str(e)}"

    return project_results

def main():
    try:
        USERNAME = "maxim.lupan@mteam.md"
        PASSWORD = "12"
        LOGIN_URL = "https://stage15.office.grafit.md/"

        # Создаем драйвер через Driver Manager
        driver = setup_chrome_driver(headless=True, test_id=TEST_ID)

        try:
            logger.info(f"Starting test execution with ID: {TEST_ID}")
            # First login for checking statuses
            if not login_to_system(driver, USERNAME, PASSWORD, LOGIN_URL):
                logging.error("Login failed")
                sys.exit(1)

            # Check active projects for each carrier separately
            carrier_active_projects = {}
            for carrier_id, carrier_info in CARRIERS.items():
                carrier_projects = get_active_projects_for_carrier(driver, carrier_info["url"])
                if not carrier_projects:
                    error_message = f"Failed to get active projects for carrier {carrier_id}"
                    logging.error(error_message)
                    take_error_screenshot(driver, f"no_active_projects_{carrier_id}")
                    sys.exit(1)
                carrier_active_projects[carrier_id] = carrier_projects

            # Test each carrier's active projects separately
            results = {}
            for carrier_id, carrier_info in CARRIERS.items():
                results[carrier_id] = {"projects": {}}
                active_projects = carrier_active_projects[carrier_id]

                for project_id, project_url in PROJECTS.items():
                    if project_id in active_projects and active_projects[project_id]:
                        project_result = check_project(
                            driver,
                            project_id,
                            project_url,
                            carrier_info
                        )

                        if not project_result["success"]:
                            error_message = f"Project check failed for {project_id}"
                            logging.error(error_message)
                            take_error_screenshot(driver, f"project_check_failed_{project_id}")
                            sys.exit(1)

                        results[carrier_id]["projects"][project_id] = project_result
                        sleep(2)

            # Print results
            print("\n=== TEST RESULTS ===")
            for carrier_id, carrier_results in results.items():
                print(f"\nCarrier: {CARRIERS[carrier_id]['name']}")
                print("-" * 40)

                if not carrier_results["projects"]:
                    print("No active projects found for this carrier")
                    continue

                for project_id, result in carrier_results["projects"].items():
                    print(f"\nProject: {project_id}")
                    print(f"Success: {'Yes' if result['success'] else 'No'}")

                    if not result['success']:
                        print("Details:")
                        if not result['navigation_steps']['Success Button']:
                            print("Could not click success button")
                        print(f"Message: {result['carrier_check']['actual_message']}")

        except Exception as e:
            logging.error(f"Script execution failed: {str(e)}")
            take_error_screenshot(driver, "script_execution_failed")
            sys.exit(1)
        finally:
            release_driver(driver)
            logging.info("Script execution completed")

    except Exception as e:
        logging.error(f"Critical error in main execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()