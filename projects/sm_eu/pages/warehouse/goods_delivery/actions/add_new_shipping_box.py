import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    NoSuchFrameException, StaleElementReferenceException
)
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from common.pages.warehouse.locators import WarehouseLocators
from common.pages.page_907.actions.verify_shipping_costs import verify_shipping_costs
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def add_new_shipping_box(
    driver, 
    project_name, 
    sales_order_id, 
    dimensions=None, 
    carrier_name="DHL", 
    wait_timeout=30
):
    """
    Extended sm_eu specific function that:
    1. Adds a new shipping box
    2. Clicks the Add button after a pause
    3. Opens a new tab to verify logistics data
    4. Returns to delete the newly created box
    
    Args:
        driver: Selenium WebDriver
        project_name: Project code (e.g. "sm_eu")
        sales_order_id: Order ID to verify in logistics
        dimensions: Dictionary with width, length, height, weight values
        carrier_name: Name of the carrier to select
        wait_timeout: Maximum wait time in seconds
        
    Returns:
        dict: Result with success status and details
    """
    logger = logging.getLogger('test')
    logger.info(f"Starting specialized sm_eu shipping box test for order {sales_order_id}")
    
    # Get locators from the class
    NEW_BOX_ELEMENTS = WarehouseLocators.NEW_BOX_ELEMENTS
    
    # Store the original window handle
    original_window = driver.current_window_handle
    
    # Default dimensions if not provided
    if dimensions is None:
        dimensions = {
            "width": "15",
            "length": "15",
            "height": "15",
            "weight": "15"
        }
    
    # Box ID for tracking the created box (will be updated after creation)
    new_box_id = None
    
    result = {
        "success": False,
        "add_box_result": {},
        "logistics_result": {},
        "delete_box_result": {},
        "error": None
    }
    
    try:
        # 1) Дожидаемся полной загрузки страницы
        WebDriverWait(driver, wait_timeout).until(
            lambda d: d.execute_script("return document.readyState === 'complete'")
        )
        
        # 2) Пытаемся переключиться в iframe для работы с формой коробки
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        logger.info(f"Found {len(frames)} iframes on page")
        
        try:
            logger.info("Trying to switch to shipping iframe")
            WebDriverWait(driver, wait_timeout).until(
                EC.frame_to_be_available_and_switch_to_it((
                    By.XPATH, 
                    "//iframe[contains(@id,'ship_template_') and @class='ship_template']"
                ))
            )
            logger.info("Successfully switched to shipping iframe")
            
            # Заполняем поля для габаритов и веса
            width_input = WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located((By.NAME, "shipping_package_width"))
            )
            width_input.clear()
            width_input.send_keys(dimensions["width"])
            logger.info(f"Entered width: {dimensions['width']}")

            length_input = WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located((By.NAME, "shipping_package_length"))
            )
            length_input.clear()
            length_input.send_keys(dimensions["length"])
            logger.info(f"Entered length: {dimensions['length']}")

            height_input = WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located((By.NAME, "shipping_package_height"))
            )
            height_input.clear()
            height_input.send_keys(dimensions["height"])
            logger.info(f"Entered height: {dimensions['height']}")
            
            weight_input = WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located((By.NAME, "shipping_package_weight_new"))
            )
            weight_input.clear()
            weight_input.send_keys(dimensions["weight"])
            logger.info(f"Entered weight: {dimensions['weight']}")
            
            # Пытаемся выбрать перевозчика (carrier_name) если он есть
            try:
                carrier_selects = driver.find_elements(By.TAG_NAME, "select")
                carrier_select_found = False
                for select_elem in carrier_selects:
                    try:
                        select = Select(select_elem)
                        options = select.options
                        if any(carrier_name in opt.text for opt in options):
                            logger.info(f"Found carrier select with {carrier_name} option")
                            select.select_by_visible_text(carrier_name)
                            carrier_select_found = True
                            break
                    except Exception:
                        continue
                
                if not carrier_select_found:
                    logger.warning(f"Could not find carrier select with {carrier_name} option")
            except Exception as e:
                logger.warning(f"Error selecting carrier: {str(e)}")
            if project_name in ["et_eu", "ho_eu"]:
                logger.info(f"Special handling for {project_name}: selecting warehouse sector")
                try:
                    # Find the warehouse sector dropdown
                    sector_select_element = WebDriverWait(driver, wait_timeout).until(
                        EC.presence_of_element_located((By.NAME, "whse_sector_new"))
                    )
                    
                    # Create a Select object
                    sector_select = Select(sector_select_element)
                    
                    # Get all options
                    options = sector_select.options
                    
                    # Select the first non-empty value
                    for option in options:
                        value = option.get_attribute("value")
                        if value:  # Skip empty value ""
                            logger.info(f"Selecting warehouse sector with value: {value}")
                            sector_select.select_by_value(value)
                            break
                            
                    logger.info("Successfully selected warehouse sector")
                    
                except Exception as e:
                    logger.warning(f"Error selecting warehouse sector for {project_name}: {str(e)}")
            # 3) Клик по кнопке "Add"
            # Пробуем несколько локаторов
            try:
                add_button = WebDriverWait(driver, wait_timeout).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='button' and @value='Add']"))
                )
                logger.info("Found Add button by primary selector")
            except TimeoutException:
                try:
                    add_button = WebDriverWait(driver, wait_timeout).until(
                        EC.element_to_be_clickable((By.XPATH, "//tr[contains(@id,'box_row_')]/td[last()]//input[@value='Add']"))
                    )
                    logger.info("Found Add button by secondary selector")
                except TimeoutException:
                    add_button = WebDriverWait(driver, wait_timeout).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Add') and (self::button or self::input)]"))
                    )
                    logger.info("Found Add button by generic selector")
            
            logger.info("Waiting 2 seconds before clicking Add button...")
            time.sleep(2)
            driver.execute_script("arguments[0].click();", add_button)
            logger.info("Clicked Add button in iframe")
            
            time.sleep(5)  # Ждём, чтобы бокс отобразился (AJAX)
            
            # Считаем добавление коробки успешным
            result["add_box_result"] = {
                "success": True,
                "message": "Completed box addition procedure"
            }
            
            # 4) Пытаемся получить ID созданной коробки (new_box_id)
            try:
                delete_buttons_iframe = driver.find_elements(
                    By.XPATH, 
                    "//a[contains(@id,'delete_box_') and contains(@class,'delete')] | "
                    "//a[contains(@onclick,'f_deleteBox')]"
                )
                logger.info(f"Found {len(delete_buttons_iframe)} delete buttons in iframe")
                
                if delete_buttons_iframe:
                    last_delete_id = delete_buttons_iframe[-1].get_attribute('id')
                    if last_delete_id and 'delete_box_' in last_delete_id:
                        new_box_id = last_delete_id.replace('delete_box_', '')
                        logger.info(f"Identified newly created box ID from iframe: {new_box_id}")
                    else:
                        # Проверим onclick на случай, если id не подошёл
                        last_onclick = delete_buttons_iframe[-1].get_attribute('onclick')
                        if last_onclick and 'f_deleteBox(' in last_onclick:
                            new_box_id = last_onclick.split('f_deleteBox(')[1].split(')')[0]
                            logger.info(f"Identified newly created box ID from onclick in iframe: {new_box_id}")
            except Exception as e:
                logger.warning(f"Error finding delete buttons in iframe: {str(e)}")
            
            # 5) Открываем новую вкладку для проверки логистики
            logger.info("Opening new tab for logistics verification")
            driver.execute_script("window.open('');")
            
            new_window = [window for window in driver.window_handles if window != original_window][0]
            driver.switch_to.window(new_window)
            
            logger.info("Verifying shipping costs in logistics")
            logistics_result = verify_shipping_costs(
                driver=driver,
                target_project=project_name,
                order_id=sales_order_id,
                box_ids=[new_box_id] if new_box_id else None,
                carrier_name=carrier_name
            )
            result["logistics_result"] = logistics_result
            
            # 6) Возвращаемся в оригинальную вкладку
            # After switching back to the original window
            logger.info("Switching back to original tab")
            driver.close()
            driver.switch_to.window(original_window)
            
            # Switch back to the same iframe used for adding the box
            if new_box_id:
                logger.info(f"Attempting to delete box with ID {new_box_id}")
                
                try:
                    # First, switch back to the shipping iframe
                    logger.info("Switching back to shipping iframe for deletion")
                    WebDriverWait(driver, wait_timeout).until(
                        EC.frame_to_be_available_and_switch_to_it((
                            By.XPATH, 
                            "//iframe[contains(@id,'ship_template_') and @class='ship_template']"
                        ))
                    )
                    
                    # Now check if f_deleteBox exists in this context
                    func_type = driver.execute_script("return typeof f_deleteBox")
                    logger.info(f"typeof f_deleteBox in iframe context: {func_type}")
                    
                    if func_type == "function":
                        # Call f_deleteBox within the iframe
                        delete_script = f"f_deleteBox({new_box_id});"
                        driver.execute_script(delete_script)
                        logger.info(f"Called f_deleteBox({new_box_id}) in iframe context")
                    else:
                        logger.warning("Function f_deleteBox not found in iframe context either.")
                        result["delete_box_result"] = {
                            "success": False,
                            "message": "f_deleteBox not found in iframe context"
                        }
                        # Switch back to default content before returning
                        driver.switch_to.default_content()
                        return result
                    
                    # Пробуем поймать диалог/alert
                    try:
                        WebDriverWait(driver, 5).until(EC.alert_is_present())
                        alert = driver.switch_to.alert
                        logger.info("Alert found, accepting it")
                        alert.accept()
                    except TimeoutException:
                        logger.info("No alert found, checking for a confirmation dialog (OK button)")
                        try:
                            confirm_button = WebDriverWait(driver, wait_timeout).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[text()='OK'] | //input[@value='OK']"))
                            )
                            driver.execute_script("arguments[0].click();", confirm_button)
                            logger.info("Clicked OK button on confirmation dialog")
                        except TimeoutException:
                            logger.info("No confirmation dialog found. Possibly no extra confirmation needed.")
                    
                    # Небольшая пауза, чтобы удаление успело отработать
                    time.sleep(5)
                    
                    # Проверяем, удалился ли элемент
                    check_script = f"return document.querySelector('a[onclick*=\"f_deleteBox({new_box_id})\"]') === null"
                    element_removed = driver.execute_script(check_script)
                    
                    if element_removed:
                        logger.info(f"Box {new_box_id} was successfully deleted")
                        result["delete_box_result"] = {
                            "success": True,
                            "message": f"Box {new_box_id} was successfully deleted"
                        }
                    else:
                        logger.warning(f"Box {new_box_id} may not have been deleted")
                        result["delete_box_result"] = {
                            "success": False,
                            "message": f"Box {new_box_id} may not have been deleted"
                        }
                    
                except Exception as e:
                    logger.warning(f"Error during deletion: {str(e)}")
                    result["delete_box_result"] = {
                        "success": False,
                        "message": f"Error during deletion: {str(e)}"
                    }
            else:
                logger.warning("Could not identify the newly created box ID for deletion")
                result["delete_box_result"] = {
                    "success": False,
                    "message": "Could not identify the newly created box ID for deletion"
                }
            
        except (TimeoutException, NoSuchFrameException, StaleElementReferenceException) as frame_exception:
            logger.error(f"Error working with iframe: {str(frame_exception)}")
            driver.switch_to.default_content()
            logger.info("Switched back to main content after iframe error")
            raise
        
        # Финальная проверка успеха
        # Логика: если добавление, логистика и удаление = success, тогда всё ок
        result["success"] = (
            result["add_box_result"].get("success", False) and
            result["logistics_result"].get("success", False) and
            result["delete_box_result"].get("success", False)
        )
        
        return result
        
    except Exception as e:
        error_msg = f"Error during sm_eu specialized shipping box test: {str(e)}"
        logger.error(error_msg)
        result["error"] = error_msg
        return result
    finally:
        # Закрываем лишние вкладки, если остались
        try:
            driver.switch_to.default_content()
            current_window = driver.current_window_handle
            if current_window != original_window:
                driver.close()
                driver.switch_to.window(original_window)
        except Exception as e:
            logger.warning(f"Error during tab cleanup: {str(e)}")
