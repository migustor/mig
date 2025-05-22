import logging
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from projects.et_eu.pages.page_888.locators_sales_order import (
    row_by_part_number,
    DROPDOWN_HOWER,
    DELETE_ITEM_LINK,
    SWAL_CONFIRM_BUTTON
)

logger = logging.getLogger(__name__)

def delete_item_from_so(driver, part_number, timeout=15):
    """
    Удаляем товар по part_number:
     1) Находим строку <tr data-item-found-part-number=part_number>
     2) Наводим мышь на div.dropdown-hower (чтобы меню открылось)
     3) Кликаем "Delete item from this sales order"
     4) SweetAlert2 confirm
     5) Проверяем, что строка пропала
    """
    wait = WebDriverWait(driver, timeout)
    row_loc = row_by_part_number(part_number)

    try:
        row_el = wait.until(EC.visibility_of_element_located(row_loc))
        logger.info(f"Row found for part_number={part_number}, ready to delete.")

        dropdown_el = row_el.find_element(*DROPDOWN_HOWER)
        ActionChains(driver).move_to_element(dropdown_el).perform()
        time.sleep(1)  # даём меню раскрыться

        delete_link = row_el.find_element(*DELETE_ITEM_LINK)
        delete_link.click()
        logger.info(f"Clicked 'Delete item...' for part_number={part_number}")
        time.sleep(1)

        confirm_btn = wait.until(EC.element_to_be_clickable(SWAL_CONFIRM_BUTTON))
        confirm_btn.click()
        wait.until(EC.invisibility_of_element_located(row_loc))
        logger.info(f"Row for {part_number} disappeared — item deleted.")
        return {"success": True, "error": None}

        # Проверяем, что строка пропала
        try:
            driver.find_element(*row_loc)
            logger.warning(f"Row for {part_number} still found => maybe not deleted?")
        except NoSuchElementException:
            logger.info(f"Row for {part_number} no longer present => item deleted.")
        return {"success": True, "error": None}

    except TimeoutException as te:
        err = f"Timeout in delete_item_from_so({part_number}): {str(te)}"
        logger.error(err)
        return {"success": False, "error": err}
    except Exception as ex:
        err = f"Exception in delete_item_from_so({part_number}): {str(ex)}"
        logger.error(err)
        return {"success": False, "error": err}
