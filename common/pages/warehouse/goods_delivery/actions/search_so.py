import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from common.pages.warehouse.locators import WarehouseLocators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def search_sales_order(driver, so_id, wait_timeout=30):
    logger = logging.getLogger('test')
    logger.info(f"Searching for sales order ID: {so_id}")
    
    # Get locators from the class
    MAIN_PAGE_ELEMENTS = WarehouseLocators.MAIN_PAGE_ELEMENTS
    
    try:
        # Вводим SO ID
        so_input = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(MAIN_PAGE_ELEMENTS["so_id_input"])
        )
        so_input.clear()
        so_input.send_keys(so_id)
        logger.info(f"Entered SO ID: {so_id}")
        
        # Нажимаем View
        view_button = WebDriverWait(driver, wait_timeout).until(
            EC.element_to_be_clickable(MAIN_PAGE_ELEMENTS["view_button"])
        )
        view_button.click()
        logger.info("Clicked View button")
        
        # Ожидаем исчезновение индикатора загрузки (если есть)
        try:
            WebDriverWait(driver, wait_timeout).until_not(
                EC.visibility_of_element_located(MAIN_PAGE_ELEMENTS["loading_indicator"])
            )
            logger.info("Loading indicator disappeared")
        except TimeoutException:
            logger.warning("Loading indicator not found or did not disappear")

        # Ожидаем таблицу заказов
        logger.info("Waiting for orders table to appear")
        WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(MAIN_PAGE_ELEMENTS["orders_table"])
        )
        logger.info("Orders table found")

        return {
            "success": True,
            "message": f"Successfully searched for SO ID: {so_id}",
            "order_id": so_id  # Важно вернуть!
        }

    except Exception as e:
        logger.error(f"Error during sales order search: {str(e)}")
        return {
            "success": False,
            "message": "Error during search operation",
            "error": str(e)
        }