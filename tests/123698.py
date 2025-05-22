"""
Запуск:  python -m tests.123698
"""
import logging, uuid, time, os, sys
from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system

from projects.gr_eu.pages.page_57.workflow.quick_position_search import (
    run_quick_position_search
)

TIMEOUTS = {"login": 20, "action": 15}

def run_test(driver):
    logging.info("=== quick-position-search test started ===")

    # 1) логин
    res = login_as_user(driver, project_name="gr_eu", user_type="dd", timeouts=TIMEOUTS)
    if not res["success"]:
        raise RuntimeError(res["error"])

    # 2) страница 57
    driver.get("https://stage15.office.grafit.md/sage/index.cfm?page_id=57")
    time.sleep(2)

    # 3) сценарий быстрого поиска
    run_quick_position_search(driver, timeout=TIMEOUTS["action"])

    logging.info("=== test finished successfully ===")

def main():
    test_id = f"quick_pos_{uuid.uuid4().hex[:8]}"
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    driver = setup_chrome_driver(headless=False, test_id=test_id)
    try:
        run_test(driver)
    finally:
        logout_from_system(driver, project_name="gr_eu")
        release_driver(driver)

if __name__ == "__main__":
    main()
