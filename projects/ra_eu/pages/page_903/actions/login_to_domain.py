# common/pages/page_903/actions/login_to_domain.py
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def login_to_domain(driver, domain, username, password, timeouts=None):
    """
    Logs in to the specified domain
    
    Args:
        driver: Selenium WebDriver
        domain: Domain to log in to
        username: Username for login
        password: Password for login
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status and error message if any
    """
    logger = logging.getLogger('test')
    login_url = f"https://{domain}/sage/?logout"
    logger.info(f"Logging in to {domain} with user {username}")
    
    timeouts = timeouts or {}
    login_timeout = timeouts.get("login", 10)
    
    try:
        # Navigate to login page
        driver.get(login_url)
        
        # Wait for login form elements
        login_field = WebDriverWait(driver, login_timeout).until(
            EC.presence_of_element_located((By.ID, "login_name"))
        )
        login_field.clear()
        login_field.send_keys(username)
        
        pass_field = WebDriverWait(driver, login_timeout).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        pass_field.clear()
        pass_field.send_keys(password)
        
        # Click submit button
        submit_btn = WebDriverWait(driver, login_timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'].btn.btn-info.btn-lg"))
        )
        submit_btn.click()
        
        # Wait for login to complete
        time.sleep(1)
        
        logger.info(f"Successfully logged in to {domain}")
        return {"success": True, "error": None}
        
    except TimeoutException as te:
        error_msg = f"Timeout during login to {domain}: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error during login to {domain}: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}