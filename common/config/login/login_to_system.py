"""
Действия для входа в систему с использованием локаторов из файла.
"""
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Импортируем локаторы
from common.config.login.locators import LOGIN_FORM

def login_to_system(driver, username: str, password: str, url: str, timeouts=None):
    """
    Выполняет вход в систему с указанными учетными данными
    
    Args:
        driver: Selenium WebDriver
        username: Имя пользователя
        password: Пароль
        url: URL страницы логина
        timeouts: Словарь с таймаутами для различных операций
        
    Returns:
        bool: True если вход успешен, False в противном случае
    """
    logger = logging.getLogger('test')
    logger.info(f"Navigating to login page: {url}")
    
    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    login_timeout = timeouts.get("login", 15)  # Default to 15 if not specified
    
    try:
        # Переходим на страницу логина
        driver.get(url)
        time.sleep(2)  # Даем странице время загрузиться
        
        # Ожидаем загрузки страницы и находим элементы
        logger.info("Waiting for login form elements...")
        username_input = WebDriverWait(driver, login_timeout).until(
            EC.presence_of_element_located(LOGIN_FORM["username_field"])
        )
        password_input = WebDriverWait(driver, login_timeout).until(
            EC.presence_of_element_located(LOGIN_FORM["password_field"])
        )
        
        # Вводим учетные данные
        logger.info("Entering credentials...")
        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)
        
        # Нажимаем кнопку входа
        logger.info("Clicking submit button...")
        submit_button = WebDriverWait(driver, login_timeout).until(
            EC.element_to_be_clickable(LOGIN_FORM["submit_button"])
        )
        submit_button.click()
        
        # Ждем исчезновения формы логина (признак успешного входа)
        WebDriverWait(driver, login_timeout).until(
            EC.invisibility_of_element_located(LOGIN_FORM["username_field"])
        )
        
        logger.info("Login successful")
        return True
            
    except TimeoutException as te:
        logger.error(f"Timeout occurred during login: {str(te)}")
        return False
        
    except NoSuchElementException as nse:
        logger.error(f"Element not found during login: {str(nse)}")
        return False
        
    except Exception as e:
        logger.error(f"Login failed with unexpected error: {str(e)}")
        return False