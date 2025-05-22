"""
Тестирование добавления новой упаковки на странице 905
"""
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.pages.page_905.page_info import get_page_905_url
from common.pages.page_905.locators import (
    ADD_PACKAGE_BUTTON, LENGTH_INPUT, WIDTH_INPUT, 
    HEIGHT_INPUT, WEIGHT_INPUT_NEW, BLUR_ELEMENT, ERROR_BLOCK
)
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def add_shipping_package(driver, project_name, sales_order_id):
    """
    Открывает страницу 905, нажимает кнопку "Add Shipping Package", 
    вводит размеры и вес, затем проверяет появление сообщения об ошибке.

    Args:
        driver: WebDriver
        project_name: Название проекта.
        sales_order_id: ID заказа.

    Returns:
        dict: Результат выполнения с информацией о сообщении об ошибке.
    """
    logger = logging.getLogger("test")
    logger.info(f"Testing Add Shipping Package for sales_order_id={sales_order_id} in {project_name}.")

    page_url = get_page_905_url(project_name, sales_order_id)
    if not page_url:
        return {"success": False, "error": "Не удалось сгенерировать URL"}
    
    driver.get(page_url)
    logger.info("Waiting for page to load...")
    time.sleep(5)

    try:
        # Ищем и нажимаем кнопку "Add Shipping Package"
        add_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(ADD_PACKAGE_BUTTON)
        )
        add_button.click()
        logger.info("Clicked 'Add Shipping Package' button")
        time.sleep(2)  # Ждем появления формы
        
        # Заполняем поля размеров нового пакета
        driver.find_element(*LENGTH_INPUT).send_keys("12")
        driver.find_element(*WIDTH_INPUT).send_keys("12")
        driver.find_element(*HEIGHT_INPUT).send_keys("12")
        logger.info("Entered package dimensions: 12x12x12")
        
        # Вводим вес
        weight_input = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(WEIGHT_INPUT_NEW)
        )
        weight_input.clear()
        weight_input.send_keys("12.00")
        logger.info("Entered weight: 12.00")
        
        # Кликаем в пустое место для запуска AJAX
        try:
            # Вариант 1: Клик по body
            driver.find_element(*BLUR_ELEMENT).click()
            logger.info("Clicked on body element to blur the field")
        except:
            # Вариант 2: JavaScript для снятия фокуса
            driver.execute_script("document.activeElement.blur();")
            logger.info("Used JavaScript to blur the active element")
        
        # Ждем, чтобы AJAX успел выполниться
        time.sleep(3)
        
        # Проверяем наличие сообщения об ошибке
        expected_error = "Please contact Logistics to get shipping cost!"
        error_found = False
        error_text = ""
        
        try:
            error_block = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(ERROR_BLOCK)
            )
            
            if error_block.is_displayed() and error_block.text.strip():
                error_text = error_block.text.strip()
                error_found = True
                logger.info(f"Found error message: {error_text}")
                
        except:
            logger.info("No error message found")
        
        expected_error_found = expected_error in error_text if error_text else False
        
        return {
            "success": True,
            "error_found": error_found,
            "error_message": error_text,
            "expected_error_found": expected_error_found,
            "expected_error": expected_error
        }
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}