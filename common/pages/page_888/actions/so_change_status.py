import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, JavascriptException
from common.pages.page_888.page_info import get_page_888_url
from common.pages.page_888.locators import Page888Locators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def change_status_and_save(driver, project_name, sales_order_id, timeouts=None):
    """
    Генерирует ссылку, ждет загрузку страницы, меняет статус через JS "хардово" и сохраняет изменения.
    
    Args:
        driver: Selenium WebDriver
        project_name: Название проекта (например, "ra_eu").
        sales_order_id: ID заказа продаж.
        timeouts: Словарь с таймаутами.

    Returns:
        dict: Результат выполнения действия.
    """
    logger = logging.getLogger('test')
    logger.info(f"Changing status for sales_order_id={sales_order_id} in {project_name} to 'WHSE Packing' (244).")

    # Генерация URL
    order_url = get_page_888_url(project_name, sales_order_id)
    if not order_url:
        return {"success": False, "error": "Could not generate URL"}

    driver.get(order_url)

    # Ждем загрузку страницы
    logger.info("Waiting for page to load...")
    time.sleep(5)  # Ожидание полной загрузки страницы

    try:
        # Выполнение JavaScript для смены статуса "хардово"
        js_script = """
        (function() {
            let selectElement = document.getElementById('status_id');
            if (selectElement) {
                selectElement.value = "244"; // Устанавливаем значение WHSE Packing жестко
                let hiddenInput = document.getElementById('so_status_id');
                if (hiddenInput) {
                    hiddenInput.value = "244"; // Меняем скрытый input тоже
                }
                selectElement.dispatchEvent(new Event('change', { bubbles: true })); // Генерируем событие изменения
                console.log("Статус успешно изменен на WHSE Packing.");
            } else {
                console.error("Элемент <select> с ID 'status_id' не найден.");
            }
        })();
        """

        driver.execute_script(js_script)
        time.sleep(3)  # Ждем, пока статус применится

        # Ожидание кнопки сохранения
        logger.info("Waiting for save button...")
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(Page888Locators.SAVE_BUTTON)
        )

        logger.info("Clicking save button...")
        save_button.click()
        time.sleep(3)  # Ожидание обработки

        logger.info("Status changed and saved successfully.")
        return {"success": True, "error": None}

    except TimeoutException as te:
        error_msg = f"Timeout waiting for save button: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except JavascriptException as je:
        error_msg = f"JavaScript error: {str(je)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except Exception as e:
        error_msg = f"Error changing status: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
