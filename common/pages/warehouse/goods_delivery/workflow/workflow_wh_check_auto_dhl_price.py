import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.pages.warehouse.page_info import get_goods_delivery_url
from common.pages.warehouse.goods_delivery.actions.search_so import search_sales_order
from common.pages.warehouse.goods_delivery.actions.change_auto_dhl_cost import change_auto_dhl_cost
from common.pages.warehouse.goods_delivery.actions.add_new_shipping_box import add_new_shipping_box
from common.pages.warehouse.locators import WarehouseLocators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def verify_dhl_cost_calculation(driver, project_name, so_id, box_id=None, new_weight=25):
    """
    Workflow to verify automatic DHL cost calculation when changing box weight
    and adding a new shipping box.
    
    Args:
        driver: Selenium WebDriver
        project_name: Project code (e.g., 'ra_eu')
        so_id: Sales Order ID to search for
        box_id: Box ID to modify (if None, will be extracted from search results)
        new_weight: New weight to set (default 25)
        
    Returns:
        dict: Result with success status and details
    """
    logger = logging.getLogger('test')
    logger.info(f"Starting DHL cost calculation verification workflow for project {project_name}")
    
    try:
        # Navigate to goods delivery page
        goods_delivery_url = get_goods_delivery_url(project_name)
        logger.info(f"Navigating to goods delivery page: {goods_delivery_url}")
        driver.get(goods_delivery_url)
        time.sleep(2)  # Allow page to load
        
        # Step 1: Search for the sales order
        search_result = search_sales_order(driver, so_id)
        if not search_result["success"]:
            logger.error(f"Failed to find sales order: {search_result['message']}")
            return {
                "success": False,
                "step": "search_order",
                "error": search_result["message"]
            }
        
        order_id = search_result["order_id"]
        logger.info(f"Found order ID: {order_id}")
        
        # If box_id not provided, could extract it here based on the page
        if box_id is None:
            # This would require additional implementation to extract box_id from the page
            logger.warning("Box ID not provided, using default value of 1")
            box_id = 1
        
        # Step 2: Change weight and verify cost calculation
        cost_result = change_auto_dhl_cost(driver, order_id, box_id, new_weight)
        if not cost_result["success"]:
            logger.error(f"Failed to verify cost calculation: {cost_result['message']}")
            return {
                "success": False,
                "step": "verify_cost_calculation",
                "error": cost_result["message"]
            }
        
        logger.info(f"Successfully verified DHL cost calculation. Original: {cost_result['original_cost']}, New: {cost_result['new_cost']}")
        
        # Need to click the shipping link again to reopen the popup
        # First try to switch back to default content just in case
        try:
            driver.switch_to.default_content()
        except:
            pass
        
        # Click the link again
        link_locator = WarehouseLocators.ORDER_ELEMENTS["specific_order_link"](order_id)
        link = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(link_locator)
        )
        logger.info(f"Reopening shipping popup for SO {order_id}")
        driver.execute_script("arguments[0].click();", link)
        
        # Wait for iframe and switch to it
        iframe_locator = WarehouseLocators.POPUP_ELEMENTS["iframe"](order_id)
        WebDriverWait(driver, 30).until(
            EC.frame_to_be_available_and_switch_to_it(iframe_locator)
        )
        
        # Step 3: Add new shipping box and verify warning
        box_result = add_new_shipping_box(driver)
        
        # Switch back to default content
        driver.switch_to.default_content()
        
        if not box_result["success"]:
            logger.error(f"Failed to verify shipping box warning: {box_result['message']}")
            return {
                "success": False,
                "step": "verify_shipping_warning",
                "error": box_result["message"]
            }
        
        logger.info(f"Successfully verified shipping box warning: {box_result.get('warning_text', '')}")
        
        return {
            "success": True,
            "step": "complete",
            "original_cost": cost_result["original_cost"],
            "new_cost": cost_result["new_cost"],
            "weight_change": cost_result["weight_change"],
            "warning_verified": True,
            "warning_text": box_result.get("warning_text", "")
        }
        
    except Exception as e:
        logger.error(f"Error in DHL cost calculation workflow: {str(e)}")
        # Make sure we're back to default content
        try:
            driver.switch_to.default_content()
        except:
            pass
        return {
            "success": False,
            "step": "workflow_exception",
            "error": str(e)
        }