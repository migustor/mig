"""
Действие для проверки наличия предупреждения о ненулевом балансе.
"""
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By

from common.pages.page_830.locators import Page830Locators

def verify_balance_warning(driver, timeouts=None):
    """
    Проверяет наличие предупреждения о ненулевом балансе компании
    после нажатия на кнопку редактирования статуса.
    
    Args:
        driver: Selenium WebDriver
        timeouts: Словарь с таймаутами для различных операций
        
    Returns:
        dict: Результат проверки {'success': True/False, 'error': None/str, 'warning_text': str}
    """
    logger = logging.getLogger('test')
    print("Checking for the presence of a non-zero balance warning")
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    
    try:
        # Пробуем стандартный селектор
        try:
            warning_element = WebDriverWait(driver, action_timeout).until(
                EC.visibility_of_element_located(Page830Locators.BALANCE_WARNING)
            )
        except TimeoutException:
            # Если стандартный селектор не сработал, пробуем поиск по тексту
            warning_element = WebDriverWait(driver, action_timeout).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Warning. Non-zero company balance.')]"))
            )
        
        # Получаем текст предупреждения
        warning_text = warning_element.text.strip()
        print(f"Found warning text: '{warning_text}'")
        
        # Проверяем, содержит ли текст предупреждения ожидаемую фразу
        expected_text = "Warning. Non-zero company balance."
        if expected_text in warning_text:
            print("Balance warning contains the expected text")
            return {
                "success": True,
                "error": None,
                "warning_text": warning_text
            }
        else:
            error_msg = f"Warning text does not match the expected text. Expected: '{expected_text}', Received: '{warning_text}'"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "warning_text": warning_text
            }
            
    except TimeoutException as te:
        error_msg = f"Timeout while waiting for the balance warning: {str(te)}"
        print(error_msg)
        return {"success": False, "error": error_msg}
        
    except NoSuchElementException as nse:
        error_msg = f"Balance warning element not found: {str(nse)}"
        print(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error while checking the balance warning: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}