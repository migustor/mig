# common/pages/page_621/actions/click_create_button.py
"""
Модуль для действия нажатия на кнопку "Create".
"""
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Импортируем локаторы
from common.pages.page_621.locators import Page621Locators

def click_create_button(driver, timeout=10):
    """
    Нажимает на кнопку "Create".
    
    Args:
        driver: Selenium WebDriver
        timeout: Время ожидания доступности кнопки в секундах
        
    Returns:
        dict: Результат действия {'success': bool, 'error': str или None}
    """
    logger = logging.getLogger('test')
    logger.info("Attempting to click on Create button")
    
    try:
        # Ожидаем доступности кнопки
        create_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(Page621Locators.CREATE_BUTTON)
        )
        
        # Прокручиваем страницу до кнопки, чтобы она была видна
        driver.execute_script("arguments[0].scrollIntoView(true);", create_button)
        
        # Небольшая пауза перед кликом для стабильности
        time.sleep(0.5)
        
        # Нажимаем на кнопку
        logger.info("Clicking on Create button")
        create_button.click()
        
        # Даем время на обработку нажатия
        time.sleep(1)
        
        logger.info("Successfully clicked on Create button")
        return {"success": True, "error": None}
            
    except TimeoutException as te:
        error_msg = f"Timeout occurred waiting for Create button: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except NoSuchElementException as nse:
        error_msg = f"Create button not found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Unexpected error when clicking Create button: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}