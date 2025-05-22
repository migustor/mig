import logging
import time
import importlib
import sys

from selenium.webdriver.common.by import By

# Driver, login, status change
from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.config.login.login_as_user import login_as_user
from common.pages.page_888.actions.so_change_status import change_status_and_save

# Deleting a package (the same for everyone, in the folder common/page_905)
from common.pages.page_905.actions.delete_package import delete_package

# Re-saving the package for 902 and 905 (the same for all projects)
from common.pages.page_902.actions.several_saves import several_saves as several_saves_902
from common.pages.page_905.actions.several_saves import several_saves as several_saves_905

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_sales_order")


# Helper to dynamically import project-specific or common actions
def import_action(project_name, page, action):
    try:
        mod = importlib.import_module(f"projects.{project_name}.pages.{page}.actions.{action}")
        return getattr(mod, action)
    except ImportError:
        mod = importlib.import_module(f"common.pages.{page}.actions.{action}")
        return getattr(mod, action)


def count_created_boxes(driver):
    time.sleep(2)
    boxes = driver.find_elements(By.CSS_SELECTOR, "tr.box_row")
    return len(boxes)

def test_change_sales_order_status():
    driver = setup_chrome_driver(headless=False)

    projects = {
        "ag_eu": 50307,
        "ho_eu": 1274,
        "et_eu": 276785,
        "ra_eu": 100915,
        "lt_eu": 88073,
        "sm_eu": 629762
    }

    errors = []

    try:
        for project_name, sales_order_id in projects.items():
            logger.info(f"Starting test for project {project_name} with order {sales_order_id}")

            # 1) Login
            login_result = login_as_user(driver, project_name, "vb")
            if not login_result["success"]:
                error_msg = f"Login failed in {project_name}: {login_result['error']}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

            # 2) Change status (888, common)
            status_result = change_status_and_save(driver, project_name, sales_order_id)
            if not status_result["success"]:
                error_msg = f"Status change failed in {project_name}: {status_result['error']}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

            # 3) Delete boxes (905, common)
            delete_result = delete_package(driver, project_name, sales_order_id, timeouts={"action": 10})
            if not delete_result["success"]:
                error_msg = f"Delete package failed in {project_name}: {delete_result['error']}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

            # 4) Create a new box (902)
            create_package = import_action(project_name, "page_902", "create_package")
            create_result = create_package(driver, project_name, sales_order_id)
            if not create_result["success"]:
                error_msg = f"Create package failed in {project_name}: {create_result['error']}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

            several_saves_result = several_saves_902(driver)
            if not several_saves_result["success"]:
                error_msg = f"several_saves 902 failed in {project_name}: {several_saves_result['error']}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

            box_count = count_created_boxes(driver)
            if box_count != 1:
                error_msg = f"Too many boxes on 902 in {project_name}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

            # 5) Additional box (905)
            create_additional_package = import_action(project_name, "page_905", "create_additional_package")
            create_905_result = create_additional_package(driver, project_name, sales_order_id, {"action": 10})
            if not create_905_result["success"]:
                error_msg = f"Create package 905 failed in {project_name}: {create_905_result['error']}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

            several_saves_result = several_saves_905(driver)
            if not several_saves_result["success"]:
                error_msg = f"several_saves 905 failed in {project_name}: {several_saves_result['error']}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

            final_delete_result = delete_package(driver, project_name, sales_order_id, timeouts={"action": 10})
            if not final_delete_result["success"]:
                error_msg = f"Final delete on 905 failed in {project_name}: {final_delete_result['error']}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

            box_count_after_delete = count_created_boxes(driver)
            if box_count_after_delete != 1:
                error_msg = f"Expected 1 box left after final delete in {project_name}, found {box_count_after_delete}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue

            logger.info(f"Test successfully completed for {project_name}")

        if errors:
            logger.info("Test completed with errors:")
            for err in errors:
                logger.error(err)
            return {"success": False, "errors": errors}
        else:
            logger.info("All projects processed without errors")
            return {"success": True}

    finally:
        release_driver(driver, quit=True)


def main():
    result = test_change_sales_order_status()

    # Final summary
    if not result.get("success", True):
        logger.info("==== TEST COMPLETED WITH ERRORS ====")
        for err in result.get("errors", []):
            logger.info(f" - {err}")
        sys.exit(1)  # This signals Jenkins to treat build as failed
    else:
        logger.info("==== ALL PROJECTS PASSED SUCCESSFULLY ====")

if __name__ == "__main__":
    main()
