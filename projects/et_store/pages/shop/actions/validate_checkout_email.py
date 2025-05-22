import logging
import time
import random
import string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import error handling decorator
from common.utils.error_handling import jenkins_aware


@jenkins_aware()
def validate_checkout_email(driver, project_name, timeouts=None):
    """
    Validates email field on checkout page by:
    1. Navigating to checkout page
    2. Testing various invalid email formats
    3. Restoring the original email and completing the checkout
    4. Verifying successful checkout

    Args:
        driver: WebDriver
        project_name: Project name (e.g., 'et_store')
        timeouts: Dictionary with timeouts for different operations

    Returns:
        dict: {"success": bool, "error": str|None, "validation_results": list}
    """
    logger = logging.getLogger(' - validate_checkout_email - ')
    logger.info(f"Starting checkout email validation in {project_name}.")

    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    page_load_timeout = timeouts.get("page_load", 10)
    action_timeout = timeouts.get("action", 10)
    loader_timeout = timeouts.get("loader", 60)  # 1 minute max for loader
    
    # List to store validation test results
    validation_results = []
    
    try:
        # Generate checkout URL from page_info
        try:
            from projects.et_store.pages.shop.page_info import get_page_url
            checkout_url = get_page_url("checkout")
            logger.info(f"Generated checkout URL: {checkout_url}")
        except ImportError:
            # Fallback URL if import fails
            checkout_url = "https://stage15.store.eminiatrading.com/index.php?page=checkout"
            logger.info(f"Using fallback checkout URL: {checkout_url}")

        # Navigate to checkout page
        logger.info(f"Navigating to checkout page: {checkout_url}")
        driver.get(checkout_url)
        
        # Wait for page to load
        time.sleep(page_load_timeout)
        
        # Find email field and get the original value
        try:
            email_field = WebDriverWait(driver, action_timeout).until(
                EC.presence_of_element_located((By.ID, "customer_email"))
            )
            original_email = email_field.get_attribute("value")
            logger.info(f"Found email field with original value: {original_email}")
        except TimeoutException:
            # Take screenshot before failing
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_path = f"checkout_email_field_not_found_{timestamp}.png"
            try:
                driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved to {screenshot_path}")
            except:
                pass
                
            error_msg = "Could not find email field"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
            
        # Find submit button
        try:
            submit_button = WebDriverWait(driver, action_timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'].btn-success"))
            )
            logger.info("Found submit button")
        except TimeoutException:
            error_msg = "Could not find submit button"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
            
        # Generate invalid email formats to test
        invalid_emails = [
            "abc123",                           # No (at) symbol
            "TEST(at)EXAMPLE.COM",                 # All caps
            "test(at)" + "".join(random.choices(string.ascii_lowercase, k=20)),  # Random domain without TLD
            "!#$%^&*()(at)example.com",            # Special chars in local part
            "test(at)example." + "".join(random.choices(string.ascii_lowercase, k=1)),  # Invalid TLD
            "a(at)b.c",                            # Too short
            " test(at)example.com ",               # Extra spaces
            "test..test(at)example.com"            # Double dots in local part
        ]
        
        # Test each invalid email
        for invalid_email in invalid_emails:
            logger.info(f"Testing invalid email: {invalid_email}")
            
            # Clear field and input invalid email - use JavaScript for reliability
            try:
                driver.execute_script("arguments[0].value = '';", email_field)
                time.sleep(0.5)
                email_field.send_keys(invalid_email)
                logger.info(f"Entered invalid email: {invalid_email}")
            except Exception as e:
                logger.warning(f"Error entering email via standard method: {str(e)}")
                try:
                    # Fallback to JavaScript
                    driver.execute_script(f"arguments[0].value = '{invalid_email}';", email_field)
                    logger.info(f"Entered invalid email via JavaScript: {invalid_email}")
                except Exception as js_e:
                    logger.error(f"Failed to enter email: {str(js_e)}")
                    continue
            
            # Click submit button using JavaScript directly to avoid intercepted clicks
            try:
                logger.info("Clicking submit button via JavaScript...")
                driver.execute_script("arguments[0].click();", submit_button)
                logger.info("Submit button clicked via JavaScript")
            except Exception as js_e:
                logger.error(f"JavaScript click failed: {str(js_e)}")
                continue
            
            # Check for error message
            try:
                error_message = WebDriverWait(driver, action_timeout).until(
                    EC.visibility_of_element_located((By.ID, "customer_email-error"))
                )
                error_text = error_message.text.strip()
                logger.info(f"Error message found: '{error_text}'")
                validation_results.append({
                    "email": invalid_email,
                    "error_found": True,
                    "error_message": error_text
                })
            except TimeoutException:
                logger.warning(f"No error message found for invalid email: {invalid_email}")
                validation_results.append({
                    "email": invalid_email,
                    "error_found": False,
                    "error_message": None
                })
                
            # Small pause between tests
            time.sleep(1)
        
        # Restore original email and submit final form
        logger.info(f"Restoring original email: {original_email}")
        try:
            driver.execute_script("arguments[0].value = '';", email_field)
            time.sleep(0.5)
            email_field.send_keys(original_email)
        except Exception as e:
            logger.warning(f"Standard method failed: {str(e)}, trying JavaScript...")
            try:
                driver.execute_script(f"arguments[0].value = '{original_email}';", email_field)
            except Exception as js_e:
                error_msg = f"Failed to restore original email: {str(js_e)}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg, "validation_results": validation_results}
        
        # Click submit button for final checkout - use JavaScript directly
        logger.info("Clicking submit button for final checkout via JavaScript")
        try:
            driver.execute_script("arguments[0].click();", submit_button)
            logger.info("Submit button clicked via JavaScript for final checkout")
        except Exception as js_e:
            error_msg = f"Failed to click submit button for final checkout: {str(js_e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "validation_results": validation_results}
        
        # Check for loader and wait if present
        logger.info("Checking for loader...")
        
        loader_present = False
        try:
            # Check if loader appears
            loader = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "loader"))
            )
            logger.info("Loader found, waiting for it to disappear...")
            loader_present = True
        except TimeoutException:
            logger.info("No loader appeared, operation may have completed immediately")
        
        # If loader was present, wait for it to disappear
        if loader_present:
            try:
                WebDriverWait(driver, loader_timeout).until(
                    EC.invisibility_of_element_located((By.ID, "loader"))
                )
                logger.info("Loader disappeared, checkout completed")
            except TimeoutException:
                logger.warning(f"Loader still present after {loader_timeout} seconds")
                # We'll continue to check for success indicator anyway
        
        # Wait for success indicator with increased timeout
        try:
            success_indicator = WebDriverWait(driver, action_timeout * 2).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.sa-icon.sa-success"))
            )
            logger.info("Success indicator found, checkout completed successfully")
            checkout_success = True
        except TimeoutException:
            # Try alternative success indicators
            success_found = False
            alternative_selectors = [
                (By.CSS_SELECTOR, ".alert-success"),
                (By.XPATH, "//div[contains(@class, 'success')]"),
                (By.XPATH, "//div[contains(text(), 'success') or contains(text(), 'Success')]"),
                (By.XPATH, "//h1[contains(text(), 'Thank you') or contains(text(), 'Order Complete')]")
            ]
            
            for selector in alternative_selectors:
                try:
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located(selector)
                    )
                    if element:
                        logger.info(f"Alternative success indicator found: {element.text}")
                        success_found = True
                        break
                except:
                    continue
            
            if success_found:
                checkout_success = True
            else:
                # Take screenshot before failing
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                screenshot_path = f"checkout_success_not_found_{timestamp}.png"
                try:
                    driver.save_screenshot(screenshot_path)
                    logger.info(f"Screenshot saved to {screenshot_path}")
                except:
                    pass
                    
                error_msg = "Success indicator not found after checkout"
                logger.error(error_msg)
                checkout_success = False
            
        return {
            "success": checkout_success,
            "error": None if checkout_success else "Success indicator not found after checkout",
            "validation_results": validation_results
        }
            
    except Exception as e:
        error_msg = f"Error during validate_checkout_email: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "validation_results": validation_results}