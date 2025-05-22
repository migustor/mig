import logging
import time
from selenium.webdriver.common.by import By

# Import locators (XPATH strings)
from projects.ho_eu.pages.page_905.locators import (
    DELETE_ROW_BUTTON,
    CONFIRM_DELETE_BUTTON,
    ADD_SHIPPING_PACKAGE_BUTTON,
    NEW_BOX_INPUTS,
    SAVE_PACKAGE_BUTTON
)
# If there's a shared URL generator for page 905
from projects.ho_eu.pages.page_905.page_info import get_page_905_url

from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def create_additional_package(driver, project_name, sales_order_id, timeouts):
    """
    Открывает страницу 905, создает новую коробку (все поля = "10"),
    выбирает WHSE 1-Sector 1 из выпадающего списка и нажимает "Save".

    Args:
        driver: Selenium WebDriver.
        project_name: Название проекта, напр. "argon".
        sales_order_id: ID заказа (int).
        timeouts: словарь таймаутов.

    Returns:
        dict: {"success": bool, "error": str|None}
    """
    logger = logging.getLogger('test')
    logger.info(f"Creating package for sales_order_id={sales_order_id} in {project_name}.")

    # Build page URL
    page_url = get_page_905_url(project_name, sales_order_id)
    if not page_url:
        return {"success": False, "error": "Could not generate URL for the page."}

    driver.get(page_url)
    logger.info("Waiting for page to load...")
    time.sleep(5)  # Small delay to allow the page to fully load

    try:
        # Click "Add Shipping Package"
        logger.info("Clicking add package button...")
        driver.find_element(By.XPATH, ADD_SHIPPING_PACKAGE_BUTTON).click()
        time.sleep(1)

        # Fill out the inputs with "10"
        logger.info("Filling package details with '10'...")
        for field_name, xpath_locator in NEW_BOX_INPUTS.items():
            field_el = driver.find_element(By.XPATH, xpath_locator)
            field_el.clear()
            field_el.send_keys("10")
            time.sleep(1)

        # ----------------------------------------------------------
        # Choose "WHSE 1-Sector 1" in the select <name="whse_sector_new">
        # using JS to set the value to '1|1'
        try:
            sector_select = driver.find_element(By.NAME, "whse_sector_new")
            # Use JavaScript to assign the needed value to the <select>
            driver.execute_script("arguments[0].value = '1|1';", sector_select)
            logger.info("Selected WHSE 1-Sector 1 using JavaScript.")
        except Exception as e:
            logger.warning(f"Could not set sector via JS: {e}")
        # ----------------------------------------------------------

        # Finally, click the save button
        logger.info("Clicking save package button...")
        driver.find_element(By.XPATH, SAVE_PACKAGE_BUTTON).click()
        time.sleep(2)

        logger.info("Package created successfully.")
        return {"success": True, "error": None}

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
