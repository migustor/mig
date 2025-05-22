# common/pages/page_621/actions/mark_items_as_presale.py
"""
Module for marking selected items as presale on page 621.
"""
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By

from common.pages.page_621.locators import Page621Locators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def mark_items_as_presale(driver, timeout=10):
    """
    Selects the first checkbox, clicks the 'Mark Selected Items As Presale' button,
    and confirms the presale in the popup dialog.
    
    Args:
        driver: Selenium WebDriver
        timeout: Element wait timeout in seconds
        
    Returns:
        dict: Result of the operation {'success': bool, 'error': str or None}
    """
    logger = logging.getLogger('test')
    logger.info("Marking items as presale")
    
    try:
        # 1. Найти все чекбоксы
        logger.info("Finding checkboxes in item list")
        checkboxes = driver.find_elements(*Page621Locators.ALL_ITEM_CHECKBOXES)
        
        if not checkboxes:
            error_msg = "No checkboxes found on the page"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
            
        logger.info(f"Found {len(checkboxes)} checkboxes on the page")
        
        # Выбираем первый чекбокс с помощью JavaScript, чтобы обойти проблему перехвата клика
        first_checkbox = checkboxes[0]
        logger.info(f"Selecting first checkbox with value: {first_checkbox.get_attribute('value')}")
        
        # Используем JavaScript для установки checked=true и генерации события change
        driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", first_checkbox)
        
        # Проверим, что чекбокс действительно выбран
        if not first_checkbox.is_selected():
            error_msg = "Failed to select checkbox using JavaScript"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        logger.info("Checkbox selected successfully")
        
        # 2. Сделаем прокрутку к кнопке "Mark Selected Items As Presale" перед попыткой клика
        try:
            presale_buttons = driver.find_elements(*Page621Locators.MARK_AS_PRESALE_BUTTON)
            
            if not presale_buttons:
                error_msg = "No 'Mark Selected Items As Presale' button found"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
            presale_button = presale_buttons[0]
            logger.info("Found 'Mark Selected Items As Presale' button")
            
            # Прокрутка к кнопке для обеспечения видимости
            driver.execute_script("arguments[0].scrollIntoView(true);", presale_button)
            time.sleep(0.5)  # Даем время на прокрутку
            
            # Используем JavaScript для клика, чтобы обойти возможные проблемы с перехватом
            logger.info("Clicking 'Mark Selected Items As Presale' button using JavaScript")
            driver.execute_script("arguments[0].click();", presale_button)
            
        except Exception as e:
            logger.error(f"Error clicking presale button: {str(e)}")
            return {"success": False, "error": f"Error clicking presale button: {str(e)}"}
        
        # 3. Нажимаем на кнопку подтверждения в попапе
        logger.info("Waiting for popup and clicking confirmation button")
        # Даем время для появления попапа
        time.sleep(1.5)
        
        # Ищем кнопку подтверждения
        try:
            confirm_buttons = driver.find_elements(*Page621Locators.PRESALE_CONFIRM_BUTTON)
            
            if not confirm_buttons:
                error_msg = "No confirmation button found in popup"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
            confirm_button = confirm_buttons[0]
            logger.info("Found confirmation button in popup")
            
            # Используем JavaScript для клика
            driver.execute_script("arguments[0].click();", confirm_button)
            
        except Exception as e:
            logger.error(f"Error clicking confirmation button: {str(e)}")
            return {"success": False, "error": f"Error clicking confirmation button: {str(e)}"}
        
        # Добавляем задержку для обработки запроса
        time.sleep(2)
        
        logger.info("Successfully marked items as presale")
        return {"success": True, "error": None}
        
    except TimeoutException as te:
        error_msg = f"Timeout occurred while marking items as presale: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except NoSuchElementException as nse:
        error_msg = f"Element not found while marking items as presale: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Unexpected error when marking items as presale: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}