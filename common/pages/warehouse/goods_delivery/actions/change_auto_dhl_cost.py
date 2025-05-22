import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from common.pages.warehouse.locators import WarehouseLocators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def change_auto_dhl_cost(driver, so_id, box_id, new_weight, wait_timeout=30):
    """
    Clicks shipping link for SO, edits box weight in iframe form, verifies cost is recalculated.
    """
    logger = logging.getLogger('test')
    logger.info(f"Starting DHL cost verification for SO {so_id}, box {box_id}, weight: {new_weight}")
    # Get locators from the class
    ORDER_ELEMENTS = WarehouseLocators.ORDER_ELEMENTS
    POPUP_ELEMENTS = WarehouseLocators.POPUP_ELEMENTS
    try:
        # Find link to f_enterShipDetails(...)
        link_locator = ORDER_ELEMENTS["specific_order_link"](so_id)
        link = WebDriverWait(driver, wait_timeout).until(
            EC.element_to_be_clickable(link_locator)
        )
        logger.info(f"Found link for SO {so_id}, clicking...")
        driver.execute_script("arguments[0].click();", link)
        # Wait for iframe to appear
        iframe_locator = POPUP_ELEMENTS["iframe"](so_id)
        WebDriverWait(driver, wait_timeout).until(
            EC.frame_to_be_available_and_switch_to_it(iframe_locator)
        )
        logger.info("Switched to iframe with shipping form")
        # Wait for body (as confirmation of iframe loading)
        WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(POPUP_ELEMENTS["popup_container"])
        )
        # Get weight and cost elements
        weight_input = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(POPUP_ELEMENTS["box_weight_input"](box_id))
        )
        cost_input = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(POPUP_ELEMENTS["cost_input"](box_id))
        )
        original_cost = cost_input.get_attribute("value")
        logger.info(f"Original cost: {original_cost}")
        # Change weight
        weight_input.clear()
        weight_input.send_keys(str(new_weight))
        logger.info(f"Set weight to: {new_weight}")
        # Click outside the field — just on body (usually this is enough)
        ActionChains(driver).move_by_offset(5, 5).click().perform()
        time.sleep(2)  # Wait for Ajax update
        # Get updated cost
        new_cost = cost_input.get_attribute("value")
        logger.info(f"New cost: {new_cost}")
        # Return from iframe
        driver.switch_to.default_content()
        # Compare
        if original_cost != new_cost:
            logger.info("Cost has changed")
            return {
                "success": True,
                "message": "Cost changed after weight modification",
                "original_cost": original_cost,
                "new_cost": new_cost,
                "weight_change": new_weight,
                "order_id": so_id
            }
        else:
            logger.warning("Cost did NOT change")
            return {
                "success": False,
                "message": "Cost did not change after weight modification",
                "original_cost": original_cost,
                "new_cost": new_cost,
                "weight_change": new_weight,
                "order_id": so_id
            }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        try:
            driver.switch_to.default_content()
        except:
            pass
        return {
            "success": False,
            "message": "Error while attempting to change cost",
            "error": str(e),
            "order_id": so_id
        }