"""
Действие для нажатия на кнопку редактирования статуса компании.
"""
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from common.pages.page_830.locators import Page830Locators

def click_company_status(driver, timeouts=None):
    """
    Нажимает на кнопку редактирования статуса компании (карандаш).
    
    Args:
        driver: Selenium WebDriver
        timeouts: Словарь с таймаутами для различных операций
        
    Returns:
        dict: Результат операции {'success': True/False, 'error': None/str}
    """
    logger = logging.getLogger('test')
    print("Clicking the company status edit button")
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    
    try:
        # Проверяем наличие контейнера статуса компании
        status_container = WebDriverWait(driver, action_timeout).until(
            EC.presence_of_element_located(Page830Locators.COMPANY_STATUS_CONTAINER)
        )
        
        # Находим кнопку редактирования
        try:
            # Используем основной селектор
            edit_button = WebDriverWait(driver, action_timeout).until(
                EC.element_to_be_clickable(Page830Locators.STATUS_EDIT_BUTTON)
            )
        except TimeoutException:
            # Если основной селектор не сработал, пробуем альтернативный
            edit_button = WebDriverWait(driver, action_timeout).until(
                EC.element_to_be_clickable(Page830Locators.STATUS_EDIT_BUTTON_ALT)
            )
        
        # Пробуем кликнуть на кнопку
        try:
            # Обычный клик
            edit_button.click()
        except Exception:
            # Если обычный клик не сработал, используем JavaScript
            driver.execute_script("arguments[0].click();", edit_button)
        
        # Даём время для анимации и появления предупреждения
        time.sleep(2)
        
        print("Edit button clicked successfully")
        return {"success": True, "error": None}
            
    except TimeoutException as te:
        error_msg = f"Timeout while waiting for the edit button: {str(te)}"
        print(error_msg)
        return {"success": False, "error": error_msg}
        
    except NoSuchElementException as nse:
        error_msg = f"Edit button not found: {str(nse)}"
        print(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error while clicking the edit button: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}