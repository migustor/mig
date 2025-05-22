"""
Gets the first three orders from the search results after loading
"""
import logging
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from common.utils.error_handling import jenkins_aware

from projects.gr_eu.pages.page_907.actions.set_order_status_filters import set_order_status_filters
from projects.gr_eu.pages.page_907.actions.build_report import build_report

@jenkins_aware()
def get_first_three_orders(driver, timeouts=None):
    """
    Waits for loading to complete and returns the IDs of the first three orders from the results.
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts
        
    Returns:
        dict: Execution result with success/error information and order IDs
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info("Waiting for results to load and getting first three orders")
    
    timeouts = timeouts or {}
    max_wait_time = timeouts.get("max_wait", 60)  # Maximum wait time for loading
    
    # Locators 
    loading_spinner = (By.CSS_SELECTOR, 'i.fa-spinner#rotation')
    # Use the correct class for the result container from HTML
    result_container = (By.CSS_SELECTOR, '.logistics-request-auto-open.panel')
    # Use the class result_order_id for the order link
    order_link = (By.CSS_SELECTOR, '.result_order_id')
    
    # Try twice, if first attempt fails, refresh and reapply filters
    for attempt in range(2):  # Two attempts
        # Wait for the loading spinner to disappear
        start_time = time.time()
        spinner_gone = False
        
        while (time.time() - start_time) < max_wait_time:
            try:
                spinner = driver.find_element(*loading_spinner)
                if spinner.is_displayed():
                    logger.info("Loading spinner is visible, waiting...")
                    time.sleep(2)
                else:
                    spinner_gone = True
                    logger.info("Loading spinner is gone")
                    break
            except NoSuchElementException:
                spinner_gone = True
                logger.info("Loading spinner not found, assuming loading complete")
                break
        
        if not spinner_gone:
            if attempt == 0:
                logger.warning(f"Loading spinner still visible after {max_wait_time} seconds. Refreshing page and trying again.")
                driver.refresh()
                time.sleep(5)  # Wait for page to reload
                
                # After refresh, we need to reapply filters and build report again
                logger.info("Reapplying filters after page refresh...")
                filter_res = set_order_status_filters(driver, timeouts)
                if not filter_res["success"]:
                    logger.error("Failed to reapply filters after refresh")
                    return {"success": False, "error": "Failed to reapply filters after refresh", "order_ids": []}
                
                time.sleep(2)
                
                logger.info("Building report again after page refresh...")
                build_res = build_report(driver, timeouts)
                if not build_res["success"]:
                    logger.error("Failed to build report after refresh")
                    return {"success": False, "error": "Failed to build report after refresh", "order_ids": []}
                
                time.sleep(3)
                continue
            else:
                error_msg = f"Loading spinner still visible after {max_wait_time} seconds on second attempt"
                logger.error(error_msg)
                return {"success": False, "error": error_msg, "order_ids": []}
        
        # Allow time for the results to fully render
        time.sleep(2)
        
        # Get the first three result containers
        try:
            result_containers = driver.find_elements(*result_container)
            
            if not result_containers:
                if attempt == 0:
                    logger.warning("No result containers found. Refreshing page and trying again.")
                    driver.refresh()
                    time.sleep(5)  # Wait for page to reload
                    
                    # After refresh, we need to reapply filters and build report again
                    logger.info("Reapplying filters after page refresh...")
                    filter_res = set_order_status_filters(driver, timeouts)
                    if not filter_res["success"]:
                        logger.error("Failed to reapply filters after refresh")
                        return {"success": False, "error": "Failed to reapply filters after refresh", "order_ids": []}
                    
                    time.sleep(2)
                    
                    logger.info("Building report again after page refresh...")
                    build_res = build_report(driver, timeouts)
                    if not build_res["success"]:
                        logger.error("Failed to build report after refresh")
                        return {"success": False, "error": "Failed to build report after refresh", "order_ids": []}
                    
                    time.sleep(3)
                    continue
                else:
                    logger.warning("No result containers found on second attempt")
                    return {"success": True, "order_ids": [], "warning": "No results found after two attempts"}
            
            # Get the order IDs from the first three containers
            order_ids = []
            for i, container in enumerate(result_containers[:3]):
                try:
                    # Get data-order_id from the container or search for the order link inside the container
                    container_order_id = container.get_attribute('data-order_id')
                    
                    if container_order_id:
                        # Use the ID from the container attribute
                        order_id = container_order_id
                        logger.info(f"Found order ID from container attribute: {order_id}")
                    else:
                        # If the ID is not found in the attribute, search for the link with the class result_order_id
                        try:
                            order_link_element = container.find_element(*order_link)
                            order_id = order_link_element.text.strip()
                            logger.info(f"Found order ID from link text: {order_id}")
                        except NoSuchElementException:
                            logger.warning(f"Order link not found in container {i+1}, trying with project data")
                            # Attempt to get the order ID and project from attributes
                            order_id = container.get_attribute('data-order_id')
                            project = container.get_attribute('data-project_uuid')
                            if order_id and project:
                                logger.info(f"Found order ID: {order_id} from project: {project}")
                            else:
                                logger.warning(f"Could not find order ID in container {i+1}")
                                continue
                    
                    order_ids.append(order_id)
                    
                except Exception as e:
                    logger.warning(f"Error getting order ID from container {i+1}: {str(e)}")
                
                if len(order_ids) >= 3:
                    break
            
            # If we have found at least one order ID, return success
            if order_ids:
                return {
                    "success": True, 
                    "order_ids": order_ids,
                    "count": len(order_ids)
                }
            elif attempt == 0:
                logger.warning("No order IDs found. Refreshing page and trying again.")
                driver.refresh()
                time.sleep(5)  # Wait for page to reload
                
                # After refresh, we need to reapply filters and build report again
                logger.info("Reapplying filters after page refresh...")
                filter_res = set_order_status_filters(driver, timeouts)
                if not filter_res["success"]:
                    logger.error("Failed to reapply filters after refresh")
                    return {"success": False, "error": "Failed to reapply filters after refresh", "order_ids": []}
                
                time.sleep(2)
                
                logger.info("Building report again after page refresh...")
                build_res = build_report(driver, timeouts)
                if not build_res["success"]:
                    logger.error("Failed to build report after refresh")
                    return {"success": False, "error": "Failed to build report after refresh", "order_ids": []}
                
                time.sleep(3)
            else:
                logger.warning("No order IDs found on second attempt")
                return {"success": True, "order_ids": [], "warning": "No order IDs found after two attempts"}
                
        except Exception as e:
            if attempt == 0:
                logger.warning(f"Error getting order IDs: {str(e)}. Refreshing page and trying again.")
                driver.refresh()
                time.sleep(5)  # Wait for page to reload
                
                # After refresh, we need to reapply filters and build report again
                logger.info("Reapplying filters after page refresh...")
                filter_res = set_order_status_filters(driver, timeouts)
                if not filter_res["success"]:
                    logger.error("Failed to reapply filters after refresh")
                    return {"success": False, "error": "Failed to reapply filters after refresh", "order_ids": []}
                
                time.sleep(2)
                
                logger.info("Building report again after page refresh...")
                build_res = build_report(driver, timeouts)
                if not build_res["success"]:
                    logger.error("Failed to build report after refresh")
                    return {"success": False, "error": "Failed to build report after refresh", "order_ids": []}
                
                time.sleep(3)
            else:
                error_msg = f"Error getting order IDs on second attempt: {str(e)}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg, "order_ids": []}
    
    # If we reach here, both attempts have failed
    return {"success": False, "error": "Failed to get order IDs after multiple attempts", "order_ids": []}