"""
Верификация изменения размеров/веса упаковки на странице 905
"""
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from common.pages.page_905.page_info import get_page_905_url
from common.pages.page_905.locators import BLUR_ELEMENT, WEIGHT_INPUT
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def verify_weight_change(driver, project_name, sales_order_id):
    """
    Открывает страницу 905, изменяет значение веса существующего пакета
    и проверяет обновилось ли значение стоимости доставки (freight_cost).

    Args:
        driver: WebDriver
        project_name: Название проекта.
        sales_order_id: ID заказа.

    Returns:
        dict: Результат проверки с информацией об изменении стоимости.
    """
    logger = logging.getLogger("test")
    logger.info(f"Testing weight change effect for sales_order_id={sales_order_id} in {project_name}.")

    page_url = get_page_905_url(project_name, sales_order_id)
    if not page_url:
        return {"success": False, "error": "Не удалось сгенерировать URL"}
    
    driver.get(page_url)
    logger.info("Waiting for page to load...")
    time.sleep(5)

    try:
        # Находим существующий пакет с его данными
        # Ищем поле веса, из которого можно получить ID пакета
        weight_inputs = driver.find_elements(*WEIGHT_INPUT)
        if not weight_inputs:
            logger.error("No shipping package weight inputs found")
            return {"success": False, "error": "No shipping package weight inputs found"}
        
        # Берем первый найденный пакет
        weight_input = weight_inputs[0]
        package_id = weight_input.get_attribute("data-shipping-package-id")
        
        if not package_id:
            # Попробуем получить ID из имени класса или имени
            class_name = weight_input.get_attribute("class")
            for class_part in class_name.split():
                if class_part.startswith("shipping_package_weight_"):
                    package_id = class_part.replace("shipping_package_weight_", "")
                    break
            
            if not package_id:
                name = weight_input.get_attribute("name")
                if name and "shipping_package_weight_" in name:
                    package_id = name.replace("shipping_package_weight_", "")
        
        if not package_id:
            logger.error("Could not determine package ID")
            return {"success": False, "error": "Could not determine package ID"}
        
        logger.info(f"Found package ID: {package_id}")
        
        # Теперь находим поле freight_cost для этого пакета
        freight_cost_locator = (By.CSS_SELECTOR, f"input[name='shipping_package_freight_cost_{package_id}']")
        try:
            freight_cost_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(freight_cost_locator)
            )
            initial_value = freight_cost_input.get_attribute("value")
            logger.info(f"Found freight cost input with initial value: {initial_value}")
        except (TimeoutException, NoSuchElementException):
            logger.warning("Freight cost input not found")
            return {"success": False, "error": "Freight cost input not found"}
        
        # Получаем текущее значение веса
        current_weight = weight_input.get_attribute("value")
        logger.info(f"Current weight value: {current_weight}")
        
        # Меняем вес - увеличиваем на 5
        new_weight = float(current_weight) + 5
        new_weight_str = f"{new_weight:.2f}"
        
        # Метод 1: Стандартный подход с очисткой и вводом
        weight_input.click()  # Фокусировка
        time.sleep(0.5)
        weight_input.clear()
        time.sleep(0.5)
        weight_input.send_keys(new_weight_str)
        time.sleep(0.5)
        
        # Метод 2: Используем JavaScript для установки значения и запуска событий
        js_set_value = """
            arguments[0].value = arguments[1];
            
            var event = new Event('input', { 'bubbles': true });
            arguments[0].dispatchEvent(event);
            
            var changeEvent = new Event('change', { 'bubbles': true });
            arguments[0].dispatchEvent(changeEvent);
            
            if (typeof jQuery !== 'undefined') {
                jQuery(arguments[0]).trigger('change').trigger('input');
            }
        """
        driver.execute_script(js_set_value, weight_input, new_weight_str)
        logger.info(f"Changed weight to {new_weight_str} using JavaScript")
        
        # Кликаем в другое место, чтобы снять фокус и запустить AJAX
        # Используем более надежный способ снятия фокуса
        try:
            # Вариант 1: Клик по body
            driver.find_element(*BLUR_ELEMENT).click()
            logger.info("Clicked on body element to blur the field")
        except:
            # Вариант 2: JavaScript для снятия фокуса
            driver.execute_script("document.activeElement.blur();")
            logger.info("Used JavaScript to blur the active element")
        
        # Ждем, пока индикатор загрузки появится и исчезнет
        loader_locator = (By.CSS_SELECTOR, f"div#freight_cost_loader_{package_id}")
        try:
            # Проверяем, появился ли индикатор загрузки
            WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located(loader_locator)
            )
            logger.info("Loader became visible, waiting for it to disappear")
            
            # Ждем исчезновения индикатора
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located(loader_locator)
            )
        except:
            logger.info("Loader icon not visible or disappeared quickly")
        
        # Дополнительное ожидание для завершения AJAX
        time.sleep(3)
        
        # Проверяем, изменилось ли значение freight_cost
        try:
            # Повторно находим элемент, DOM мог обновиться
            freight_cost_input = driver.find_element(*freight_cost_locator)
            new_value = freight_cost_input.get_attribute("value")
            
            if new_value != initial_value:
                value_changed = True
                logger.info(f"Freight cost changed from {initial_value} to {new_value}")
            else:
                value_changed = False
                logger.info(f"Freight cost did not change, still: {new_value}")
                
            return {
                "success": True,
                "initial_value": initial_value,
                "new_value": new_value,
                "value_changed": value_changed,
                "weight_before": current_weight,
                "weight_after": weight_input.get_attribute("value")
            }
                
        except NoSuchElementException:
            logger.warning("Freight cost input not found after weight change")
            return {"success": False, "error": "Freight cost input disappeared after weight change"}
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}