import os
import time
import logging
import uuid
from datetime import datetime

# Generate unique test ID for this test run
TEST_ID = f"create_company_test_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Импорт функций для работы с централизованным пулом драйверов
from common.utils.driver_setup import with_driver, setup_chrome_driver, release_driver

# Импорт универсальной функции логина
from common.config.login.login_as_user import login_as_user

# Импорт функции выхода из системы
from common.config.logout.logout_from_system import logout_from_system

# Импорт декоратора для обработки ошибок для Jenkins
from common.utils.error_handling import jenkins_aware

# Импорт функции создания компании
from common.pages.page_442.workflow.create_company.create_company_actions import create_company

from common.utils.retry_decorator import with_retry, retry_on_failure

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Простые таймауты для разных операций
TIMEOUTS = {
    "login": 20,       # Таймаут для операций логина
    "company": 25,     # Таймаут для операций создания компании
    "navigation": 25,  # Таймаут для операций навигации
    "page_load": 30    # Таймаут для загрузки страниц
}

@with_retry(max_attempts=3, retry_delay=10)
def test_project(driver, project_name):
    """
    Выполняет тест создания компании для конкретного проекта
    
    Args:
        driver: Selenium WebDriver
        project_name: Название проекта (например, "ra_eu", "at_eu", и т.д.)
    
    Returns:
        dict: Результат теста с информацией об успехе и, при необходимости, об ошибке
    """
    logger.info(f"======= Starting test for project: {project_name} =======")
    
    try:
        # Store the original tab handle
        main_window = driver.current_window_handle
        
        # Шаг 1: Логин
        logger.info(f"Starting login process for project {project_name}")
        login_result = login_as_user(driver, user_type="ar", project_name=project_name, timeouts=TIMEOUTS)
        
        if not login_result["success"]:
            logger.error(f"Login error for {project_name}: {login_result['error']}")
            return {"success": False, "error": login_result["error"], "step": "login"}
        
        logger.info(f"Login successful for {project_name}")
        
        # Шаг 2: Создание компании
        logger.info(f"Starting company creation process for {project_name}")
        try:
            new_company_url = create_company(driver, project_name=project_name, timeouts=TIMEOUTS)
            
            if not new_company_url:
                return {"success": False, "error": "Company URL was not obtained", "step": "company_creation"}
            
            logger.info(f"Company successfully created in {project_name}. URL: {new_company_url}")
            print(f"Company successfully created in {project_name}. URL: {new_company_url}")
            
            # Close all tabs except the main window
            current_handles = driver.window_handles
            for handle in current_handles:
                if handle != main_window:
                    driver.switch_to.window(handle)
                    driver.close()
            
            # Switch back to the main window
            driver.switch_to.window(main_window)
            
            return {"success": True, "company_url": new_company_url}
            
        except Exception as e:
            error_msg = f"Error during company creation for {project_name}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": str(e), "step": "company_creation"}
    
    finally:
        # Make sure we're on the main window before logging out
        try:
            if driver.current_window_handle != main_window:
                driver.switch_to.window(main_window)
        except:
            # If there's any error, try to switch to the first window
            if len(driver.window_handles) > 0:
                driver.switch_to.window(driver.window_handles[0])
                
        # Обеспечиваем выход из системы независимо от результата теста
        logout_from_system(driver, project_name)

@jenkins_aware()
def main():
    logger.info(f"Starting test execution with ID: {TEST_ID}")
    
    # Получение переменной окружения HEADLESS; по умолчанию True, если не задано
    headless_mode = os.environ.get('HEADLESS', 'True').lower() == 'true'
    
    # Список проектов для тестирования - можно менять по необходимости
    projects_to_test = ["at_eu"]
    
    # Получение драйвера из централизованного пула с test_id
    driver = setup_chrome_driver(headless=headless_mode, test_id=TEST_ID)
    
    # Отслеживание результатов
    results = {}
    
    try:
        for project_name in projects_to_test:
            # Запуск теста для этого проекта
            result = test_project(driver, project_name)
            results[project_name] = result
            
            # Добавляем разделение между тестами проектов
            print("\n" + "-"*50 + "\n")
            
    except Exception as e:
        logger.error(f"Process failed with unexpected error: {str(e)}")
        raise  # Повторно вызываем исключение для обработки декоратором jenkins_aware
    finally:
        release_driver(driver, quit=False)
    
    # Вывод итогового отчета
    print(f"\n=========== SUMMARY REPORT (TEST ID: {TEST_ID}) ===========")
    all_passed = True
    for project, result in results.items():
        status = "PASSED" if result["success"] else "FAILED"
        if not result["success"]:
            all_passed = False
            print(f"{project}: {status} - Failed at step: {result.get('step', 'unknown')}")
            print(f"  Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"{project}: {status} - Company URL: {result.get('company_url', 'N/A')}")
    
    print("\nOverall status:", "PASSED" if all_passed else "FAILED")
    logger.info(f"Test {TEST_ID} completed with status: {'PASSED' if all_passed else 'FAILED'}")
    
    # Если какой-то из проектов не прошел, сигнализируем Jenkins об ошибке
    if not all_passed:
        return {"success": False, "error": "One or more projects failed tests"}
    return {"success": True}

if __name__ == "__main__":
    main()