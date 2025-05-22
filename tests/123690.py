import os
import sys
import time
import logging
import uuid

# Импорт драйвера
from common.utils.driver_setup import setup_chrome_driver, release_driver

# Импорт логина, логаута
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system

# Импорт декоратора Jenkins (если нужно)
from common.utils.error_handling import jenkins_aware

# Из workflow для страницы 730 (romanian и проекты)
from projects.gr_eu.pages.page_730.workflow.romanian_search_flow import run_all_romanian_levels_test
from projects.gr_eu.pages.page_730.workflow.project_flow import test_projects_flow
from projects.gr_eu.pages.page_730.workflow.after_test_flow import run_after_test_flow

logger = logging.getLogger(__name__)

TIMEOUTS = {
    "login": 20,
    "action": 15,
    "navigation": 25,
    "page_load": 30
}

#@jenkins_aware()  # При необходимости
def run_test(driver):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    TIMEOUTS["download_dir"] = script_dir


    script_dir = os.path.dirname(os.path.abspath(__file__))
    """
    Основная функция теста. Использует driver для:
      1) Логина в систему
      2) Прохождения всех уровней Romanian (A1, A2, B1, ...)
      3) Проверки нескольких проектов (Agava, Argon, MTEAM)
    Возвращает словарь со статусом.
    """
    logger.info("=== Start of test (123690) ===")

    # 1) Логин
    login_result = login_as_user(driver, project_name="gr_eu", user_type="dd", timeouts=TIMEOUTS)
    if not login_result["success"]:
        error_msg = f"Login failed: {login_result['error']}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    logger.info("Login successful.")

    # 2) Проверка Romanian уровней
    romanian_result = run_all_romanian_levels_test(driver, TIMEOUTS)
    if not romanian_result["success"]:
        err_msg = f"Romanian levels test failed: {romanian_result['error']}"
        logger.error(err_msg)
        return {"success": False, "error": err_msg}
    logger.info("All Romanian-level subtests completed successfully.")

    # 3) Проверка проектов (Agava, Argon, MTEAM)
    #    Если вашему тесту нужно сохранять в текущую папку XLS, укажите download_dir.

    projects_result = test_projects_flow(driver, script_dir, TIMEOUTS)
    if not projects_result["success"]:
        err_msg = f"Projects flow test failed: {projects_result['error']}"
        logger.error(err_msg)
        return {"success": False, "error": err_msg}
        
        
    after_res = run_after_test_flow(driver, TIMEOUTS, stored_link=None)
    if not after_res["success"]:
        return {"success": False, "error": after_res["error"]}

  
    logger.info("All projects flow tests completed successfully.")

    #logger.info("=== Тест 123690 завершён успешно. ===")
    return {"success": True}

def main():
    """
    Точка входа в скрипт 123690: создаём драйвер, запускаем тест run_test(driver),
    завершаем выполнение с кодом 0/1.
    """
    test_id = f"romanian_default_{str(uuid.uuid4())[:8]}"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info(f"Test ID: {test_id}")

    # Настройки драйвера (headless и т.д.)
    driver = setup_chrome_driver(
        headless=False,
        test_id=test_id,
        download_dir=os.path.dirname(__file__)
    )

    try:
        result = run_test(driver)
        if not result["success"]:
            logger.error(f"Test failed: {result['error']}")
            sys.exit(1)
        logger.info("Test completed successfully.")
    finally:
        # Логично также сделать логаут здесь или внутри run_test (по желанию)
        logout_from_system(driver, project_name="gr_eu")
        release_driver(driver)

if __name__ == "__main__":
    main()
