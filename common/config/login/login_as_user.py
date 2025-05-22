import logging
import importlib
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def is_logged_in(driver, timeout=5):
    """
    Проверяет, залогинен ли пользователь в систему.
    
    Args:
        driver: Selenium WebDriver
        timeout: Время ожидания в секундах
        
    Returns:
        bool: True если пользователь уже залогинен, False в противном случае
    """
    logger = logging.getLogger('test')
    try:
        # Проверяем наличие элемента, который доступен только залогиненным пользователям
        # Например, меню пользователя или кнопка выхода
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'logout') or contains(text(), 'Logout')]"))
        )
        logger.info("User is already logged in")
        return True
    except:
        logger.info("User is not logged in")
        return False
@jenkins_aware()
def login_as_user(driver, project_name, user_type, timeouts=None, force_login=False):
    """
    Универсальная функция входа в систему, работающая с разными проектами и их файлами учетных данных.
    
    Args:
        driver: Selenium WebDriver
        project_name: Название проекта (например, "ra_eu", "sm_us", и т.д.)
        user_type: Тип пользователя из соответствующего файла credential.py
        timeouts: Словарь с таймаутами для различных операций
        force_login: Принудительный вход даже если пользователь уже залогинен
        
    Returns:
        dict: Результат логина {'success': bool, 'error': str или None, 'already_logged_in': bool}
    """
    logger = logging.getLogger('test')
    logger.info(f"Attempting to login to project {project_name} as user type: {user_type}")
    
    try:
        # Импортируем base_urls и получаем URL логина для указанного проекта
        try:
            from common.config.base_urls import PROJECT_BASE_URLS
            if project_name not in PROJECT_BASE_URLS:
                error_msg = f"Неизвестный проект: {project_name}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg, "already_logged_in": False}
            
            login_url = PROJECT_BASE_URLS[project_name]
        except (ImportError, AttributeError) as e:
            error_msg = f"Failed to get login URL for project {project_name}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "already_logged_in": False}
        
        # Предварительная проверка: загружаем страницу и проверяем, залогинены ли мы уже
        current_url = driver.current_url
        
        # Проверяем, не на странице ли мы уже логина (или нужного проекта)
        if not (project_name in current_url and login_url in current_url):
            driver.get(login_url)
            logger.info(f"Navigated to {login_url}")
        
        # Проверяем, залогинены ли мы уже
        if not force_login and is_logged_in(driver):
            logger.info(f"User is already logged in to {project_name}")
            return {"success": True, "error": None, "already_logged_in": True, "project": project_name}
        
        # Продолжаем с обычным процессом логина, если не залогинены
        # Динамически импортируем модуль с учетными данными для указанного проекта
        try:
            credentials_module = importlib.import_module(f"projects.{project_name}.config.credential")
            CREDENTIALS = getattr(credentials_module, "CREDENTIALS")
        except (ImportError, AttributeError) as e:
            error_msg = f"Failed to import credentials for project {project_name}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "already_logged_in": False}
        
        # Проверка наличия учётных данных
        if user_type not in CREDENTIALS:
            error_msg = f"Нет такого пользователя {user_type} в проекте {project_name}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "already_logged_in": False}
        
        user_creds = CREDENTIALS[user_type]
        
        # Импортируем функцию логина
        try:
            from common.config.login.login_to_system import login_to_system
        except ImportError as e:
            error_msg = f"Failed to import login_to_system: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "already_logged_in": False}
        
        # Вызываем действие логина
        login_success = login_to_system(
            driver,
            user_creds["username"],
            user_creds["password"],
            login_url,
            timeouts=timeouts if timeouts else {}
        )
        
        if login_success:
            logger.info(f"Login successful to {project_name} as user type: {user_type}")
            return {"success": True, "error": None, "already_logged_in": False, "project": project_name}
        else:
            error_msg = f"Логин не удался для проекта {project_name} с пользователем {user_type}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "already_logged_in": False}
            
    except Exception as e:
        error_msg = f"Error during login to {project_name} as {user_type}: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "already_logged_in": False}