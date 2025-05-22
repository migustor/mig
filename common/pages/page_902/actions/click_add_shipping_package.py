import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.pages.page_902.page_info import get_page_902_url
from common.pages.page_902.locators import NewBoxLocators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def click_add_shipping_package(driver, project_name, sales_order_id):
    """
    Открывает страницу пакетов доставки, нажимает кнопку "Add Shipping Package", 
    вводит значения и проверяет появление сообщения об ошибке.

    Args:
        driver: WebDriver
        project_name: Название проекта.
        sales_order_id: ID заказа.

    Returns:
        dict: Результат выполнения с информацией о сообщении об ошибке.
    """
    logger = logging.getLogger("test")
    logger.info(f"Testing Add Shipping Package for sales_order_id={sales_order_id} in {project_name}.")

    page_url = get_page_902_url(project_name, sales_order_id)
    if not page_url:
        return {"success": False, "error": "Could not generate URL for the page."}
    
    driver.get(page_url)
    logger.info("Waiting for page to load...")
    time.sleep(5)

    try:
        # Находим и нажимаем кнопку "Add Shipping Package" с указанным sales_order_id
        add_package_button = (By.CSS_SELECTOR, f"button.add_shipping_package[data-so-id='{sales_order_id}']")
        
        # Ожидаем кнопку и кликаем
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(add_package_button)
        ).click()
        
        logger.info(f"Clicked 'Add Shipping Package' button for order {sales_order_id}")
        time.sleep(2)  # Даем время для появления формы
        
        # Ввод данных размеров
        driver.find_element(*NewBoxLocators.LENGTH_INPUT).send_keys("12")
        driver.find_element(*NewBoxLocators.WIDTH_INPUT).send_keys("12")
        driver.find_element(*NewBoxLocators.HEIGHT_INPUT).send_keys("12")
        
        # Вводим вес в поле для нового бокса
        try:
            # Попробуем найти поле веса для нового бокса
            weight_input = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(NewBoxLocators.WEIGHT_INPUT_NEW)
            )
            weight_input.clear()
            weight_input.send_keys("12.00")  # Ввод с правильным форматированием
            logger.info("Used WEIGHT_INPUT_NEW field")
        except:
            # Если не нашли, используем стандартное поле
            driver.find_element(*NewBoxLocators.WEIGHT_INPUT).send_keys("12.00")
            logger.info("Used standard WEIGHT_INPUT field")
        
        # Кликаем где-нибудь, чтобы снять фокус и инициировать AJAX-запрос
        driver.find_element(*NewBoxLocators.PAGE_TITLE).click()
        logger.info("Entered dimensions and weight data")
        
        # Ждем, чтобы AJAX-запрос успел выполниться
        time.sleep(3)
        
        # Проверяем наличие сообщения об ошибке в блоке error_block_list
        error_found = False
        error_text = ""
        
        try:
            error_block = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(NewBoxLocators.ERROR_BLOCK)
            )
            
            # Проверяем, есть ли текст об ошибке
            if error_block.is_displayed() and error_block.text.strip():
                error_text = error_block.text.strip()
                error_found = True
                logger.info(f"Found error message in error_block_list: {error_text}")
            
        except:
            logger.info("No error message found in error_block_list")
            
        # Проверяем наличие ожидаемого сообщения об ошибке
        expected_error = "Please contact Logistics to get shipping cost!"
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