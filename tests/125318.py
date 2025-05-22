import os
import sys
import logging
import uuid

from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system

from projects.et_eu.pages.page_830.workflow.generate_sales_order_flow import run_generate_sales_order_flow

logger = logging.getLogger(__name__)

TIMEOUTS = {
    "login": 20,
    "action": 15,
    "page_load": 60
}

def run_test(driver):
    # 1) Логин
    login_result = login_as_user(driver, project_name="et_eu", user_type="dd", timeouts=TIMEOUTS)
    if not login_result["success"]:
        return {"success": False, "error": f"Login failed: {login_result['error']}"}
    logger.info("Login successful.")

    # 2) Запускаем workflow
    so_result = run_generate_sales_order_flow(driver, TIMEOUTS)
    if not so_result["success"]:
        return so_result

    return {"success": True, "error": None}

if __name__ == "__main__":
    test_id = f"test_sales_order_{uuid.uuid4().hex[:8]}"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger.info(f"Starting test: {test_id}")

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
        logout_from_system(driver, project_name="et_eu")
        release_driver(driver)
