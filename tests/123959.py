# tests/124560_page714_performance.py
import os, sys, uuid, logging
from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system
from common.pages.page_714.workflow.performance_test import run_load_performance_test

URL = "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=714&item_id=18274162"
TIMEOUTS = {"login": 20, "page_load": 30}

logger = logging.getLogger(__name__)

def run_test(driver):
    # 1) Логин (при необходимости – если страница под защитой)
    login_res = login_as_user(driver, project_name="et_eu", user_type="dd", timeouts=TIMEOUTS)
    if not login_res["success"]:
        return {"success": False, "error": "Login failed"}

    # 2) Проверка производительности
    perf_res = run_load_performance_test(
        driver,
        url=URL,
        expected_ms=20000,      # целевой SLA
        timeout=TIMEOUTS["page_load"],
        iterations=5           # сколько раз меряем
    )
    return perf_res

def main():
    test_id = f"page714_perf_{uuid.uuid4().hex[:8]}"
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    driver = setup_chrome_driver(headless=False, test_id=test_id)
    try:
        result = run_test(driver)
        if not result["success"]:
            logger.error(f"TEST FAILED: {result['error']}")
            sys.exit(1)
        logger.info("Performance test PASSED: "
                    f"avg={result['avg_ms']} ms worst={result['worst_ms']} ms")
    finally:
        logout_from_system(driver, project_name="et_eu")
        release_driver(driver)

if __name__ == "__main__":
    main()
