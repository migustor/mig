# create_package.py

import logging
import time
from projects.ho_eu.pages.page_902.page_info import get_page_902_url
from projects.ho_eu.pages.page_902.locators import NewBoxLocators
from projects.ho_eu.pages.page_902.actions.several_saves import several_saves
from common.utils.error_handling import jenkins_aware
from selenium.webdriver.common.by import By

@jenkins_aware()
def create_package(driver, project_name, sales_order_id):
    """
    Открывает страницу создания упаковки, вводит значения и сохраняет.

    Args:
        driver: WebDriver
        project_name: Название проекта.
        sales_order_id: ID заказа.

    Returns:
        dict: Результат выполнения.
    """
    logger = logging.getLogger("test")
    logger.info(f"Creating package for sales_order_id={sales_order_id} in {project_name}.")

    page_url = get_page_902_url(project_name, sales_order_id)
    if not page_url:
        return {"success": False, "error": "Could not generate URL for the page."}
    
    driver.get(page_url)
    logger.info("Waiting for page to load...")
    time.sleep(5)

    try:
        # Fill length, width, height, weight
        driver.find_element(*NewBoxLocators.LENGTH_INPUT).send_keys("10")
        driver.find_element(*NewBoxLocators.WIDTH_INPUT).send_keys("10")
        driver.find_element(*NewBoxLocators.HEIGHT_INPUT).send_keys("10")
        driver.find_element(*NewBoxLocators.WEIGHT_INPUT).send_keys("10")
        driver.find_element(*NewBoxLocators.PAGE_TITLE).click()
        logger.info("Clicked on page title to confirm input.")

        time.sleep(3)

        # ---------------------------------------------------
        # Choose WHSE 1-Sector 1 before saving
        # (JS-based solution to set <select> value)
        try:
            # Find the <select> element by its name attribute
            sector_select = driver.find_element(By.NAME, "whse_sector_new")
            # Use JavaScript to set option value to '1|1'
            driver.execute_script("arguments[0].value = '1|1';", sector_select)
            logger.info("Selected WHSE 1-Sector 1 using JavaScript.")
        except Exception as e:
            logger.warning(f"Could not set sector via JS: {e}")
        # ---------------------------------------------------

        driver.find_element(*NewBoxLocators.SAVE_BUTTON).click()
        logger.info("Package created successfully.")

        # Additional Save clicks, if needed
        several_saves(driver)

        return {"success": True}
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
