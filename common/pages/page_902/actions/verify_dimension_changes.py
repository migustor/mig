import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from common.pages.page_902.page_info import get_page_902_url
from common.pages.page_902.locators import NewBoxLocators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def verify_dimension_change(driver, project_name, sales_order_id):
    """
    Открывает страницу доставки, изменяет значение веса и проверяет
    обновилось ли значение стоимости доставки (freight_cost).

    Args:
        driver: WebDriver
        project_name: Название проекта.
        sales_order_id: ID заказа.

    Returns:
        dict: Результат проверки с информацией об изменении стоимости.
    """
    logger = logging.getLogger("test")
    logger.info(f"Testing weight change effect for sales_order_id={sales_order_id} in {project_name}.")

    page_url = get_page_902_url(project_name, sales_order_id)
    if not page_url:
        return {"success": False, "error": "Could not generate URL for the page."}
    
    driver.get(page_url)
    logger.info("Waiting for page to load...")
    time.sleep(5)

    try:
        # Находим поле freight_cost и запоминаем начальное значение
        try:
            freight_cost_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(NewBoxLocators.FREIGHT_COST_INPUT)
            )
            initial_value = freight_cost_input.get_attribute("value")
            package_id = freight_cost_input.get_attribute("name").split("_")[-1]
            logger.info(f"Found freight cost input with initial value: {initial_value} for package ID: {package_id}")
        except (TimeoutException, NoSuchElementException):
            logger.warning("Freight cost input not found initially")
            initial_value = "not_found"
            package_id = None
            return {"success": False, "error": "Freight cost input not found"}
        
        # Для существующей коробки, находим элемент ввода веса с правильным ID
        if package_id:
            # Локатор для поля веса с указанным package_id
            weight_input_locator = (By.CSS_SELECTOR, NewBoxLocators.EXISTING_WEIGHT_INPUT.format(package_id))
            
            try:
                # Ожидаем и находим элемент
                weight_input = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(weight_input_locator)
                )
                
                # Получаем текущее значение
                current_weight = weight_input.get_attribute("value")
                logger.info(f"Current weight value: {current_weight}")
                
                # Метод 1: Стандартный подход с очисткой и вводом - попробуем медленный ввод с фокусировкой
                weight_input.click()  # Фокусировка на элементе
                time.sleep(0.5)
                weight_input.clear()
                time.sleep(0.5)
                weight_input.send_keys("25.00")
                time.sleep(0.5)
                
                # Метод 2: Если первый не сработал, используем JavaScript для установки значения 
                # и явного запуска событий, которые запускают AJAX
                js_set_value = """
                    // Устанавливаем значение
                    arguments[0].value = '25.00';
                    
                    // Запускаем последовательно события, которые могут триггерить AJAX
                    var event = new Event('input', { 'bubbles': true });
                    arguments[0].dispatchEvent(event);
                    
                    var changeEvent = new Event('change', { 'bubbles': true });
                    arguments[0].dispatchEvent(changeEvent);
                    
                    // Если поле использует jQuery
                    if (typeof jQuery !== 'undefined') {
                        jQuery(arguments[0]).trigger('change').trigger('input');
                    }
                """
                driver.execute_script(js_set_value, weight_input)
                logger.info("Changed weight using JavaScript with events")
                
                # Метод 3: Прямой вызов AJAX события (если есть специальная функция в коде страницы)
                try:
                    js_trigger_ajax = f"""
                        // Если есть специальный метод обновления стоимости доставки
                        if (typeof updateShippingCost !== 'undefined') {{
                            updateShippingCost({package_id}, '25.00');
                            return true;
                        }}
                        // Или если на странице есть другие известные функции обновления
                        if (typeof calculateFreightCost !== 'undefined') {{
                            calculateFreightCost({package_id});
                            return true;
                        }}
                        return false;
                    """
                    ajax_triggered = driver.execute_script(js_trigger_ajax)
                    if ajax_triggered:
                        logger.info("Triggered AJAX update using page function")
                except:
                    logger.info("Could not trigger page AJAX function directly")
                
                # Кликаем где-нибудь, чтобы снять фокус и инициировать обновление
                driver.find_element(*NewBoxLocators.PAGE_TITLE).click()
                logger.info("Clicked elsewhere to blur the field")
                
                # Ждем некоторое время, чтобы AJAX-запрос успел выполниться
                time.sleep(5)
                
                # Проверяем состояние загрузки
                try:
                    loader_selector = (By.ID, f"freight_cost_loader_{package_id}")
                    WebDriverWait(driver, 2).until(
                        EC.visibility_of_element_located(loader_selector)
                    )
                    logger.info("Loader icon became visible, waiting for it to disappear")
                    WebDriverWait(driver, 10).until(
                        EC.invisibility_of_element_located(loader_selector)
                    )
                except:
                    logger.info("Loader icon not found or not visible")
                
                # Дополнительное время ожидания для завершения AJAX
                time.sleep(2)
                
                # Проверяем, изменилось ли значение freight_cost
                try:
                    # Повторно находим элемент freight_cost, так как DOM мог измениться
                    freight_cost_locator = (By.CSS_SELECTOR, NewBoxLocators.EXISTING_FREIGHT_COST.format(package_id))
                    freight_cost_input = driver.find_element(*freight_cost_locator)
                    new_value = freight_cost_input.get_attribute("value")
                    
                    # Проверяем, изменилось ли значение
                    if new_value != initial_value:
                        freight_cost_value_changed = True
                        logger.info(f"Freight cost value changed from {initial_value} to {new_value}")
                    else:
                        freight_cost_value_changed = False
                        logger.info(f"Freight cost value did not change, still: {new_value}")
                    
                    # Получаем текущее значение веса для проверки
                    final_weight = weight_input.get_attribute("value")
                    logger.info(f"Final weight value: {final_weight}")
                    
                except NoSuchElementException:
                    logger.warning("Freight cost input not found after weight change")
                    new_value = "not_found"
                    freight_cost_value_changed = False
                    final_weight = "unknown"
                
                return {
                    "success": True,
                    "initial_value": initial_value,
                    "new_value": new_value,
                    "value_changed": freight_cost_value_changed,
                    "weight_before": current_weight,
                    "weight_after": final_weight
                }
                
            except (TimeoutException, NoSuchElementException) as e:
                error_msg = f"Could not find weight input for package_id={package_id}: {str(e)}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
        else:
            error_msg = "Could not determine package_id from freight_cost input"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}