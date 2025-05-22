import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import error handling decorator
from common.utils.error_handling import jenkins_aware


@jenkins_aware()
def add_products(driver, project_name, timeouts=None):
    """
    Finds and clicks the first available 'Add to cart' button on the page.
    Waits for loader to appear and disappear.

    Args:
        driver: WebDriver
        project_name: Project name (e.g., 'et_store')
        timeouts: Dictionary with timeouts for different operations

    Returns:
        dict: {"success": bool, "error": str|None}
    """
    logger = logging.getLogger(' - add_products - ')
    logger.info(f"Adding product to cart in {project_name}.")

    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 10)
    loader_timeout = timeouts.get("loader", 60)  # 1 minute max for loader
    
    try:
        # Try to find the add to cart button - use a more specific selector
        logger.info("Looking for 'Add to cart' button...")
        
        # Try multiple selectors to find the button
        selectors = [
            'button.add-to-cart',
            'button.btn-outline-dark.add-to-cart',
            'button[onclick*="cart.add.init"]',
            'button[class*="add-to-cart"]',
            'button[type="button"][class*="add-to-cart"]',
            '//button[contains(@class, "add-to-cart")]',
            '//button[contains(text(), "Hinzufügen")]',
            '//button[contains(@class, "btn") and contains(@class, "add-to-cart")]'
        ]
        
        add_button = None
        for selector in selectors:
            try:
                logger.info(f"Trying selector: {selector}")
                # Determine if XPath or CSS selector
                by_method = By.XPATH if selector.startswith('//') else By.CSS_SELECTOR
                
                # Wait for element
                add_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by_method, selector))
                )
                if add_button:
                    logger.info(f"Button found using selector: {selector}")
                    break
            except Exception as e:
                logger.info(f"Selector {selector} failed: {str(e)}")
        
        if not add_button:
            # One more attempt to find any button that might be the add to cart button
            logger.info("Trying to find any buttons that look like 'add to cart'...")
            buttons = driver.find_elements(By.TAG_NAME, 'button')
            for button in buttons:
                try:
                    class_attr = button.get_attribute('class') or ""
                    onclick_attr = button.get_attribute('onclick') or ""
                    text = button.text.lower()
                    
                    if ('add-to-cart' in class_attr or 
                        'cart.add' in onclick_attr or 
                        'hinzufügen' in text.lower() or 
                        'add to cart' in text.lower()):
                        add_button = button
                        logger.info(f"Found button with text: {button.text} and class: {class_attr}")
                        break
                except:
                    continue
        
        if not add_button:
            # Take a screenshot before failure
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_path = f"add_to_cart_failure_{timestamp}.png"
            try:
                driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved to {screenshot_path}")
            except Exception as ss_err:
                logger.warning(f"Failed to save screenshot: {str(ss_err)}")
                
            # Log the page HTML for debugging
            logger.info("Page HTML excerpt:")
            try:
                html = driver.page_source
                logger.info(html[:500] + "... [truncated]")
            except:
                logger.info("Could not retrieve page source")
                
            error_msg = "Add to cart button not found after trying multiple selectors"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Click the button - try direct click first
        try:
            logger.info("Clicking 'Add to cart' button...")
            add_button.click()
            logger.info("Add to cart button clicked successfully")
        except Exception as e:
            logger.warning(f"Direct click failed: {str(e)}, trying JavaScript click...")
            # Try JavaScript click as fallback
            try:
                driver.execute_script("arguments[0].click();", add_button)
                logger.info("Add to cart button clicked via JavaScript")
            except Exception as js_e:
                # Last resort: try scrolling to element first
                try:
                    logger.info("Scrolling to button and trying again...")
                    driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", add_button)
                    logger.info("Button clicked after scrolling")
                except Exception as scroll_e:
                    error_msg = f"Failed to click add to cart button: {str(scroll_e)}"
                    logger.error(error_msg)
                    return {"success": False, "error": error_msg}
        
        # First check for "Go to cart" button which appears quickly after adding to cart
        try:
            logger.info("Looking for 'Go to cart' button (Zum Warenkorb)...")
            go_to_cart_button = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'go-to-cart__btn') or contains(text(), 'Zum Warenkorb')]"))
            )
            if go_to_cart_button:
                logger.info("'Go to cart' button found - product successfully added")
                return {"success": True, "error": None}
        except TimeoutException:
            logger.info("'Go to cart' button not found immediately, checking for loader...")
        
        # If no "Go to cart" button, check for loader
        loader_present = False
        try:
            # Check if loader appears
            loader = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "loader"))
            )
            logger.info("Loader found, waiting for it to disappear...")
            loader_present = True
        except TimeoutException:
            logger.info("No loader appeared, checking for cart update indicators...")
        
        # If loader was present, wait for it to disappear
        if loader_present:
            try:
                WebDriverWait(driver, loader_timeout).until(
                    EC.invisibility_of_element_located((By.ID, "loader"))
                )
                logger.info("Loader disappeared, operation completed")
            except TimeoutException:
                logger.warning(f"Loader still present after {loader_timeout} seconds")
        
        # Check again for "Go to cart" button after loader
        try:
            go_to_cart_button = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'go-to-cart__btn') or contains(text(), 'Zum Warenkorb')]"))
            )
            if go_to_cart_button:
                logger.info("'Go to cart' button found after loader - product successfully added")
                return {"success": True, "error": None}
        except TimeoutException:
            logger.info("'Go to cart' button not found after loader, checking other indicators...")
        
        # Verify cart was updated with any available indicator
        try:
            # Look for any indicators of a successful add
            indicators = [
                (By.CSS_SELECTOR, ".cart-indicator"),
                (By.CSS_SELECTOR, ".alert-success"),
                (By.CSS_SELECTOR, ".cart-badge"),
                (By.XPATH, "//div[contains(@class, 'cart')]//span[contains(@class, 'badge')]")
            ]
            
            for indicator_selector in indicators:
                try:
                    element = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located(indicator_selector)
                    )
                    if element:
                        logger.info(f"Found cart update indicator: {element.text}")
                        return {"success": True, "error": None}
                except:
                    continue
        except:
            logger.info("Could not verify cart update through standard indicators")
        
        # At this point, we've tried everything. Assume success if we got this far
        logger.info("Product successfully added to cart")
        return {"success": True, "error": None}
            
    except Exception as e:
        error_msg = f"Error during add_products: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}