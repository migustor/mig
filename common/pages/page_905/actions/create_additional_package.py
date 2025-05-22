import logging
import time
from selenium.webdriver.common.by import By

# Импорт локаторов (строковые XPATH)
from common.pages.page_905.locators import (
    DELETE_ROW_BUTTON,
    CONFIRM_DELETE_BUTTON,
    ADD_SHIPPING_PACKAGE_BUTTON,
    NEW_BOX_INPUTS,
    SAVE_PACKAGE_BUTTON
)
# Если общий URL-генератор для 905 лежит в common
from common.pages.page_905.page_info import get_page_905_url

# Декоратор для Jenkins (опционально, можно убрать если нет в проекте)
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def create_additional_package(driver, project_name, sales_order_id, timeouts):
    """
    Открывает страницу 905 для Argon, создает новую коробку (все поля = "10"),
    нажимает кнопку Save.

    Args:
        driver: Selenium WebDriver.
        project_name: Название проекта, напр. "argon".
        sales_order_id: ID заказа (int).
        timeouts: словарь таймаутов.

    Returns:
        dict: {"success": bool, "error": str|None}
    """
    logger = logging.getLogger('test')
    logger.info(f"Creating package for sales_order_id={sales_order_id} in {project_name}.")

    # Формируем URL
    page_url = get_page_905_url(project_name, sales_order_id)
    if not page_url:
        return {"success": False, "error": "Could not generate URL (page_905)"}

    driver.get(page_url)
    logger.info("Waiting for page to load...")
    time.sleep(5)  # Небольшая пауза, чтобы страница прогрузилась

    try:
        # Нажимаем "Add Shipping Package"
        logger.info("Clicking add package button...")
        driver.find_element(By.XPATH, ADD_SHIPPING_PACKAGE_BUTTON).click()
        time.sleep(1)

        # Заполняем поля значением "10"
        logger.info("Filling package details with '10'...")
        for field_name, xpath_locator in NEW_BOX_INPUTS.items():
            field_el = driver.find_element(By.XPATH, xpath_locator)
            field_el.clear()
            field_el.send_keys("10")
            time.sleep(1)

        # Если нужно выбрать склад-сектор, можно добавить JS или Select(...) здесь

        # Сохраняем
        logger.info("Clicking save package button...")
        driver.find_element(By.XPATH, SAVE_PACKAGE_BUTTON).click()
        time.sleep(2)

        logger.info("Package created successfully.")
        return {"success": True, "error": None}

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
