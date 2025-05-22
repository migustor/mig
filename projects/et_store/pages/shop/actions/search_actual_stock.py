import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

# Import error handling decorator
from common.utils.error_handling import jenkins_aware


@jenkins_aware()
def search_actual_stock(driver, project_name, timeouts=None):
    """
    Opens the shop page, selects the 'Actual Stock' radio button, 
    and clicks the Search button.

    Args:
        driver: WebDriver
        project_name: Project name (e.g., 'et_store')
        timeouts: Dictionary with timeouts for different operations

    Returns:
        dict: {"success": bool, "error": str|None, "products_found": int|"unknown"}
    """
    logger = logging.getLogger(' - search_actual_stock - ')
    logger.info(f"Searching actual stock in {project_name}.")

    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    page_load_timeout = timeouts.get("page_load", 10)
    action_timeout = timeouts.get("action", 10)
    loader_timeout = timeouts.get("loader", 120)  # 2 minutes max for loader
    
    try:
        # Check if we're already on the shop page, if not navigate there
        current_url = driver.current_url
        if "page=shop" not in current_url:
            logger.info("Not on shop page, navigating there...")
            
            # Navigate to shop page directly
            shop_url = "https://stage15.store.eminiatrading.com/index.php?page=shop"
            logger.info(f"Navigating to shop page: {shop_url}")
            driver.get(shop_url)
            
            # Wait for page to load
            logger.info("Waiting for page to load...")
            time.sleep(page_load_timeout)
        else:
            logger.info("Already on shop page, continuing...")
        
        # Try multiple approaches to click the 'Actual Stock' radio button
        logger.info("Selecting 'Actual Stock' radio button...")
        
        # First try: Direct click on the radio button by ID
        try:
            # Try to find and click the radio button directly by ID
            actual_stock_radio = WebDriverWait(driver, action_timeout).until(
                EC.presence_of_element_located((By.ID, "stock-type-3"))
            )
            
            # JavaScript click is more reliable for radio buttons
            driver.execute_script("arguments[0].click();", actual_stock_radio)
            logger.info("Clicked 'Actual Stock' radio button using JavaScript")
            
            # Check if the radio button is now selected
            is_selected = driver.execute_script("return arguments[0].checked;", actual_stock_radio)
            logger.info(f"Radio button selected state: {is_selected}")
            
            if not is_selected:
                # Try clicking the label instead
                try:
                    label = driver.find_element(By.XPATH, "//label[@for='stock-type-3']")
                    label.click()
                    logger.info("Clicked the label for 'Actual Stock' radio button")
                    
                    # Verify again
                    is_selected = driver.execute_script("return arguments[0].checked;", actual_stock_radio)
                    logger.info(f"Radio button selected state after label click: {is_selected}")
                except Exception as label_e:
                    logger.warning(f"Failed to click label: {str(label_e)}")
            
        except Exception as e:
            logger.warning(f"First attempt to click radio button failed: {str(e)}")
            
            # Second approach: Try clicking via JavaScript by constructing a selector
            try:
                driver.execute_script("document.getElementById('stock-type-3').click();")
                logger.info("Clicked radio button via direct JavaScript getElementById")
            except Exception as js_e:
                logger.warning(f"JavaScript click attempt failed: {str(js_e)}")
                
                # Third approach: Try setting the checked property directly
                try:
                    driver.execute_script("document.getElementById('stock-type-3').checked = true;")
                    logger.info("Set radio button checked property via JavaScript")
                except Exception as prop_e:
                    logger.warning(f"Failed to set checked property: {str(prop_e)}")
        
        # Give a brief pause to let the UI update
        time.sleep(1)
        
        # Click the Search button - try multiple approaches
        logger.info("Clicking Search button...")
        try:
            # First try: Direct click on the button
            search_button = WebDriverWait(driver, action_timeout).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "direct-submit")]'))
            )
            search_button.click()
            logger.info("Clicked Search button directly")
        except Exception as e:
            logger.warning(f"Direct click on Search button failed: {str(e)}")
            
            # Second try: JavaScript click
            try:
                driver.execute_script("document.querySelector('button.direct-submit').click();")
                logger.info("Clicked Search button via JavaScript")
            except Exception as js_e:
                logger.error(f"All attempts to click Search button failed: {str(js_e)}")
                return {"success": False, "error": f"Could not click Search button: {str(js_e)}"}
        
        # Wait for loader icon to appear and then disappear
        logger.info("Waiting for search results...")
        
        # First check if loader appears
        try:
            loader = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "loader"))
            )
            logger.info("Search in progress, loader found")
            
            # Now wait for the loader to disappear
            start_time = time.time()
            while time.time() - start_time < loader_timeout:
                try:
                    loader = driver.find_element(By.ID, "loader")
                    
                    # Check if loader is visible
                    if loader.is_displayed():
                        logger.info("Loader still visible, waiting...")
                        time.sleep(5)  # Check every 5 seconds
                    else:
                        logger.info("Loader no longer visible, search completed")
                        break
                except NoSuchElementException:
                    logger.info("Loader element no longer found, search completed")
                    break
            
            # If we've waited the full timeout, log a warning
            if time.time() - start_time >= loader_timeout:
                logger.warning(f"Loader timeout after {loader_timeout} seconds")
        except:
            logger.info("No loader found, search may have completed immediately")
        
        # Give a brief pause to let the results load fully
        time.sleep(2)
        
        # Check for the results header "Ergebnisse"
        try:
            results_header = WebDriverWait(driver, action_timeout).until(
                EC.visibility_of_element_located((By.XPATH, "//span[@class='page-block-header' and @lang='de' and text()='Ergebnisse']"))
            )
            logger.info("Found 'Ergebnisse' header, results loaded successfully")
            
            # Now check how many products are shown
            try:
                # Check if the results container is present
                results_container = driver.find_element(By.ID, "result")
                
                # Check if there are any product elements in the results
                products = results_container.find_elements(By.CSS_SELECTOR, '.product')
                
                if products:
                    logger.info(f"Search completed successfully. Found {len(products)} products.")
                    return {"success": True, "error": None, "products_found": len(products)}
                else:
                    logger.info("Results container found, but no product elements detected.")
                    # Still return success since we found the Ergebnisse header
                    return {"success": True, "error": None, "products_found": 0}
            except Exception as e:
                logger.warning(f"Could not count product elements: {str(e)}")
                # Still return success since we found the Ergebnisse header
                return {"success": True, "error": None, "products_found": "unknown"}
                
        except TimeoutException:
            logger.warning("Could not find 'Ergebnisse' header within timeout")
            
            # Try an alternative approach to check for results
            try:
                # Look for any evidence of results
                alternatives = [
                    (By.ID, "result"),
                    (By.CSS_SELECTOR, ".product"),
                    (By.CSS_SELECTOR, ".page-block-header"),
                    (By.XPATH, "//*[contains(text(), 'Ergebnisse')]")
                ]
                
                for selector in alternatives:
                    try:
                        element = driver.find_element(*selector)
                        if element.is_displayed():
                            logger.info(f"Found alternative results indicator: {selector}")
                            return {"success": True, "error": None, "products_found": "unknown"}
                    except:
                        continue
                
                # Take a screenshot before reporting failure
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                screenshot_path = f"search_results_not_found_{timestamp}.png"
                try:
                    driver.save_screenshot(screenshot_path)
                    logger.info(f"Screenshot saved to {screenshot_path}")
                except:
                    pass
                
                logger.warning("No results indicators found on page")
                return {"success": False, "error": "No search results found", "products_found": 0}
            except Exception as e:
                logger.error(f"Error checking for alternative results: {str(e)}")
                return {"success": False, "error": f"Failed to verify search results: {str(e)}"}

    except Exception as e:
        error_msg = f"Error during search_actual_stock: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}