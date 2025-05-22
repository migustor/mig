import logging
import time
from selenium.webdriver.common.by import By

# Локаторы (строковые XPath)
from projects.et_eu.pages.page_905.locators import (
    ADD_SHIPPING_PACKAGE_BUTTON,
    NEW_BOX_INPUTS,
    SAVE_PACKAGE_BUTTON,
    WHSE_SECTOR_SELECT
)
# Если у вас есть специальный page_info для et_eu
from projects.et_eu.pages.page_905.page_info import get_page_905_url

# Если нужен декоратор (не обязательно)
from common.utils.error_handling import jenkins_aware


@jenkins_aware()
def create_additional_package(driver, project_name, sales_order_id, timeouts):
    """
    Открывает страницу 905, создаёт новую коробку (заполняет поля числом 10),
    выбирает WHSE 1-Sector 1 и нажимает Save.

    Args:
        driver: WebDriver
        project_name: 'et_eu'
        sales_order_id: ID заказа
        timeouts: словарь с таймаутами

    Returns:
        dict: {"success": bool, "error": str|None}
    """
    logger = logging.getLogger('test')
    logger.info(f"Creating package for sales_order_id={sales_order_id} in {project_name}.")

    page_url = get_page_905_url(project_name, sales_order_id)
    if not page_url:
        return {"success": False, "error": "Could not generate URL for the page."}

    driver.get(page_url)
    logger.info("Waiting for page to load...")
    time.sleep(5)

    try:
        # Нажимаем кнопку "Add Shipping Package"
        logger.info("Clicking add package button...")
        add_btn = driver.find_element(By.XPATH, ADD_SHIPPING_PACKAGE_BUTTON)
        add_btn.click()
        time.sleep(1)

        # Заполняем поля значением "10"
        logger.info("Filling package details with '10'...")
        for field_name, xpath_locator in NEW_BOX_INPUTS.items():
            field_el = driver.find_element(By.XPATH, xpath_locator)
            field_el.clear()
            field_el.send_keys("10")
            time.sleep(1)

        # Выбираем WHSE 1-Sector 1 через JavaScript
        logger.info("Selecting WHSE sector via JS for et_eu...")
        driver.execute_script(
            "document.querySelector('select[name=\"whse_sector_new\"]').value = '1|1';"
        )
        time.sleep(1)

        # Или через find_element + Select:
        # from selenium.webdriver.support.ui import Select
        # sector_sel = driver.find_element(By.XPATH, WHSE_SECTOR_SELECT)
        # Select(sector_sel).select_by_value("1|1")
        # time.sleep(1)

        # Нажимаем "Save"
        logger.info("Clicking save package button...")
        save_btn = driver.find_element(By.XPATH, SAVE_PACKAGE_BUTTON)
        save_btn.click()
        time.sleep(2)

        logger.info("Package created successfully.")
        return {"success": True, "error": None}

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
