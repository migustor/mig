import logging
import time
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Генерация ссылки на заказ (page_id=907)
from common.pages.page_907.generate_order_url import generate_order_url
# Логин / логаут в проект gr_eu
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system

def delete_box(driver, new_box_id, wait_timeout=30):
    """
    Пытается удалить коробку с ID new_box_id,
    используя разные способы (f_deleteBox в родителе / iframe / прямой клик).
    Возвращает словарь вида { "success": bool, "message": str }.
    """
    logger = logging.getLogger("test")
    result = {"success": False, "message": None}
    
    try:
        # 1) Проверяем, есть ли f_deleteBox в parent
        func_type = driver.execute_script("return typeof f_deleteBox")
        logger.info(f"typeof f_deleteBox in parent context: {func_type}")
        
        if func_type == "function":
            # Вызываем напрямую
            script = f"f_deleteBox({new_box_id});"
            driver.execute_script(script)
            logger.info(f"Called f_deleteBox({new_box_id}) in parent context")
        else:
            logger.warning("f_deleteBox not found in parent. Will try iframe or direct link click.")
            
            # 2) Переключаемся в iframe (ship_template_) и там пытаемся
            try:
                # На всякий случай выйдем в default_content
                driver.switch_to.default_content()
                
                # Ищем нужный iframe
                WebDriverWait(driver, wait_timeout).until(
                    EC.frame_to_be_available_and_switch_to_it((
                        By.XPATH,
                        "//iframe[contains(@id,'ship_template_') and @class='ship_template']"
                    ))
                )
                logger.info("Switched to shipping iframe for delete_box.")
                
                func_type_iframe = driver.execute_script("return typeof f_deleteBox")
                logger.info(f"typeof f_deleteBox in iframe: {func_type_iframe}")
                
                if func_type_iframe == "function":
                    # Запускаем f_deleteBox(...) в iframe
                    script = f"f_deleteBox({new_box_id});"
                    driver.execute_script(script)
                    logger.info(f"Called f_deleteBox({new_box_id}) in iframe context")
                else:
                    logger.warning("No f_deleteBox in iframe either. Trying direct link click.")
                    
                    # 3) Пробуем найти ссылку <a onclick="f_deleteBox(123)">...
                    selector = f"a[onclick*='f_deleteBox({new_box_id})']"
                    link = driver.find_element(By.CSS_SELECTOR, selector)
                    driver.execute_script("arguments[0].click();", link)
                    logger.info(f"Clicked delete link for box {new_box_id} in iframe via direct link click.")
                
            except Exception as e:
                logger.error(f"Error switching to iframe or clicking link in iframe: {str(e)}")
                result["message"] = f"Failed to delete box in iframe: {str(e)}"
                return result
            finally:
                # Возвращаемся из iframe
                driver.switch_to.default_content()
        
        # 4) Обработка confirm/alert, если есть
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            logger.info("Alert found, accepting it for delete.")
            alert.accept()
        except TimeoutException:
            logger.info("No JS alert found for delete, checking for OK button.")
            try:
                confirm_button = WebDriverWait(driver, wait_timeout).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='OK'] | //input[@value='OK']"))
                )
                driver.execute_script("arguments[0].click();", confirm_button)
                logger.info("Clicked OK button for delete confirm.")
            except TimeoutException:
                logger.info("No separate confirmation dialog found. Possibly not needed.")
        
        # 5) Небольшая пауза, чтобы DOM успел обновиться
        time.sleep(3)
        
        # 6) Проверяем, пропал ли элемент
        script_check = f"return document.querySelector('a[onclick*=\"f_deleteBox({new_box_id})\"]') === null"
        removed = driver.execute_script(script_check)
        if removed:
            logger.info(f"Box {new_box_id} was successfully deleted.")
            result["success"] = True
            result["message"] = f"Box {new_box_id} was successfully deleted."
        else:
            logger.warning(f"Box {new_box_id} may not have been removed from DOM.")
            result["message"] = f"Box {new_box_id} not removed from DOM."
        
        return result
    
    except Exception as e:
        logger.error(f"Error in delete_box: {str(e)}")
        result["message"] = str(e)
        return result


def verify_shipping_costs(
    driver,
    target_project,
    order_id,
    box_ids=None,   # Аргумент box_ids добавлен
    carrier_name="DHL",
    timeouts=None
):
    """
    1) Логин в gr_eu
    2) Переход к 907 (tracking_url) для указанного заказа
    3) Переключаем перевозчик у ВТОРОЙ коробки:
       - c carrier_name (DHL) на другой
       - и обратно на carrier_name
    4) Если передан box_ids, проверяем freight cost > 0
       для каждого box_id (a.shipping_package_cost[data-pk=...])
    5) logout из gr_eu
    
    Returns:
        {
            "success": bool,
            "error": str|None
        }
    """
    logger = logging.getLogger('test')
    timeouts = timeouts or {"navigation": 25, "action": 15, "page_load": 30}
    result = {
        "success": False,
        "error": None
    }
    
    try:
        # 1) Логин
        login_result = login_as_user(driver, "gr_eu", "ml", timeouts)
        if not login_result.get("success"):
            result["error"] = f"Failed to login to gr_eu: {login_result.get('error')}"
            return result
        
        # 2) Переход на страницу
        tracking_url = generate_order_url(target_project, order_id, "so")
        logger.info(f"Navigating to tracking URL: {tracking_url}")
        driver.get(tracking_url)
        time.sleep(2)
        
        # Ищем селекты
        carrier_selects = driver.find_elements(By.CSS_SELECTOR, "select.form-control.dimension_carrier")
        logger.info(f"Found {len(carrier_selects)} carrier selects on the page")
        
        if len(carrier_selects) < 2:
            msg = "There is no second carrier select on the page."
            logger.warning(msg)
            result["error"] = msg
            return result
        
        second_select_elem = carrier_selects[1]
        second_select = Select(second_select_elem)
        package_id = second_select_elem.get_attribute("data-shipping-package-id")
        logger.info(f"Second box shipping_package_id = {package_id}")
        
        # Переключаем DHL -> другой -> DHL
        all_opts = second_select.options
        alt_carrier = None
        for opt in all_opts:
            t = opt.text.strip()
            if t.lower() != carrier_name.lower():
                alt_carrier = t
                break
        
        if alt_carrier:
            logger.info(f"Selecting a different carrier first: {alt_carrier}")
            second_select.select_by_visible_text(alt_carrier)
            time.sleep(1)
            
            logger.info(f"Re-selecting carrier: {carrier_name}")
            second_select.select_by_visible_text(carrier_name)
            time.sleep(2)
        else:
            logger.warning(f"No alternative carrier found besides '{carrier_name}'.")
        
        # Если box_ids передан — проверяем freight cost
        if box_ids:
            for box_id in box_ids:
                logger.info(f"Checking freight cost for box_id={box_id}")
                cost_sel = f"a.shipping_package_cost[data-pk='{box_id}']"
                try:
                    cost_elem = WebDriverWait(driver, timeouts["action"]).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, cost_sel))
                    )
                except TimeoutException:
                    msg = f"Timeout: cost element not found for box_id={box_id}"
                    logger.error(msg)
                    result["error"] = msg
                    return result
                
                cost_val = 0.0
                max_tries = 5
                for i in range(max_tries):
                    raw_text = cost_elem.text.strip()
                    logger.info(f"Box {box_id}, attempt {i+1}/{max_tries}, raw_text='{raw_text}'")
                    try:
                        cost_val = float(raw_text.replace(',', '.'))
                    except ValueError:
                        cost_val = 0.0
                    
                    if cost_val > 0.0:
                        logger.info(f"Box {box_id} cost is now {cost_val}, which is > 0 => OK")
                        break
                    
                    time.sleep(2)
                
                if cost_val <= 0.0:
                    msg = f"Freight cost for box {box_id} remains 0 after toggling carrier."
                    logger.error(msg)
                    result["error"] = msg
                    return result
        
        # Успех
        result["success"] = True
        return result
    
    except Exception as e:
        logger.error(f"Error in verify_shipping_costs: {e}")
        result["error"] = str(e)
        return result
    
    finally:
        # logout
        try:
            logout_from_system(driver, "gr_eu")
        except Exception as e:
            logger.warning(f"Error during logout: {str(e)}")
