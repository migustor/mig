import logging
import time
from common.pages.page_905.page_info import get_page_905_url
from common.pages.page_905.locators import (
    DELETE_ROW_BUTTON,
    CONFIRM_DELETE_BUTTON
)
from common.utils.error_handling import jenkins_aware

# ВАЖНО: импортируем By, чтобы использовать его в find_element(...)
from selenium.webdriver.common.by import By


@jenkins_aware()
def delete_package(driver, project_name, sales_order_id, timeouts):
    """
    Открывает страницу заказа (905), нажимает кнопку удаления пакета и подтверждает удаление.

    Args:
        driver: WebDriver (передается из другого файла).
        project_name: Название проекта (например, "ra_eu").
        sales_order_id: ID заказа.
        timeouts: Словарь с таймаутами.

    Returns:
        dict: Результат выполнения действия.
              { "success": bool, "error": str | None }
    """
    logger = logging.getLogger('test')
    logger.info(f"Deleting package for sales_order_id={sales_order_id} in {project_name}.")

    # Генерируем URL для 905-й страницы
    page_url = get_page_905_url(project_name, sales_order_id)
    if not page_url:
        return {"success": False, "error": "Could not generate URL for 905"}

    driver.get(page_url)

    # Ждем загрузку страницы
    logger.info("Waiting for page to load...")
    time.sleep(5)  # Простая пауза, чтобы страница успела прогрузиться

    action_timeout = timeouts.get("action", 10)  # Пример таймаута

    try:
        # Нажимаем кнопку удаления
        logger.info("Clicking delete button...")
        # Т.к. DELETE_ROW_BUTTON — строка XPATH,
        # используем driver.find_element(By.XPATH, DELETE_ROW_BUTTON).
        driver.find_element(By.XPATH, DELETE_ROW_BUTTON).click()
        logger.info("Delete button clicked. Waiting for confirmation popup...")

        time.sleep(2)  # Ждем появления pop-up

        # Нажимаем кнопку подтверждения удаления
        driver.find_element(By.XPATH, CONFIRM_DELETE_BUTTON).click()
        logger.info("Package deletion confirmed.")

        return {"success": True, "error": None}

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
