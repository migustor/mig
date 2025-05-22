"""
Simple and optimized login script for ET Store system
"""
import logging
import time
import importlib
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def et_store_login(driver, project_name, user_type, timeouts=None):
    """
    Performs fast login to ET Store system using credentials from project's config.
    
    Args:
        driver: Selenium WebDriver
        project_name: Project name (e.g., "et_store")
        user_type: User type from credentials file (e.g., "e2e")
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Login result {'success': bool, 'error': str or None}
    """
    logger = logging.getLogger(' - ET STORE LOGIN - ')
    logger.info(f"Attempting to login to ET Store as user type: {user_type}")
    
    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    login_timeout = timeouts.get("login", 10)  # Reduced from 15 to 10
    
    try:
        # Import base_urls and get login URL for the specified project
        try:
            from common.config.base_urls import PROJECT_BASE_URLS
            if project_name not in PROJECT_BASE_URLS:
                error_msg = f"Unknown project: {project_name}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            login_url = PROJECT_BASE_URLS[project_name]
        except (ImportError, AttributeError) as e:
            error_msg = f"Failed to get login URL for project {project_name}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Navigate to login page
        logger.info(f"Navigating to login page: {login_url}")
        driver.get(login_url)
        
        # Fast check if already logged in by looking for logout link
        try:
            logout_link = driver.find_element(By.XPATH, "//a[contains(@href, 'logout') or contains(text(), 'Logout') or contains(@class, 'logout')]")
            if logout_link:
                logger.info("User is already logged in")
                return {"success": True, "error": None, "already_logged_in": True}
        except:
            logger.info("Not logged in, continuing with login process")
        
        # Import credentials quickly
        try:
            credentials_module = importlib.import_module(f"projects.{project_name}.config.credential")
            CREDENTIALS = getattr(credentials_module, "CREDENTIALS")
            
            if user_type not in CREDENTIALS:
                error_msg = f"No such user {user_type} in project {project_name}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Get user credentials
            user_creds = CREDENTIALS[user_type]
        except (ImportError, AttributeError) as e:
            error_msg = f"Failed to import credentials: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Fast element location and interaction
        try:
            # Find all form elements at once to speed up the process
            username_input = driver.find_element(By.NAME, "login")
            password_input = driver.find_element(By.NAME, "pass")
            submit_button = driver.find_element(By.XPATH, '//button[@type="submit" and contains(@class, "btn")]')
            
            # Fill in credentials and submit quickly
            username_input.clear()
            username_input.send_keys(user_creds["username"])
            password_input.clear()
            password_input.send_keys(user_creds["password"])
            submit_button.click()
            
            logger.info("Login form submitted, checking for redirect...")
            
            # Fast check for URL change or logout link appearance
            start_time = time.time()
            original_url = driver.current_url
            success = False
            
            # Poll for changes every 0.5 seconds instead of a long wait
            while time.time() - start_time < login_timeout:
                current_url = driver.current_url
                
                # Check for URL change
                if current_url != original_url:
                    logger.info(f"URL changed to {current_url}, login successful")
                    success = True
                    break
                
                # Check for logout link
                try:
                    logout_link = driver.find_element(By.XPATH, "//a[contains(@href, 'logout') or contains(text(), 'Logout') or contains(@class, 'logout')]")
                    if logout_link:
                        logger.info("Found logout link, login successful")
                        success = True
                        break
                except:
                    pass
                
                # Check if login form is gone
                try:
                    username_input = driver.find_element(By.NAME, "login")
                except:
                    logger.info("Login form disappeared, login successful")
                    success = True
                    break
                
                # Brief pause before next check
                time.sleep(0.5)
            
            if success:
                logger.info("Login successful")
                return {"success": True, "error": None}
            else:
                # Check for error messages as a last resort
                try:
                    login_error = driver.find_element(By.ID, "login-authorization-error")
                    if login_error.text.strip():
                        logger.error(f"Login error: {login_error.text}")
                        return {"success": False, "error": login_error.text}
                except:
                    pass
                
                logger.warning("Login timeout or unclear result")
                return {"success": False, "error": "Login timeout or unclear result"}
            
        except Exception as e:
            error_msg = f"Error during login form interaction: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Unexpected error during login: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}