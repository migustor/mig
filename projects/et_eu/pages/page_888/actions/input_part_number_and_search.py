import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from projects.et_eu.pages.page_888.locators_item_search import (
    PART_NUMBER_TEXTAREA,
    SEARCH_BUTTON,
    SEARCH_RESULTS_TABLE,
    SPINNER                         # ← новый импорт
)

logger = logging.getLogger(__name__)

def input_part_number_and_search(driver, part_number, timeout=15):
    """
    1) Вводит part_number в textarea
    2) Нажимает «Search»
    3) Ждёт, пока спиннер исчезнет, и затем — появления таблицы результатов
    """
    try:
        wait = WebDriverWait(driver, timeout)

        # --- вводим part number ---
        txt_el = wait.until(EC.presence_of_element_located(PART_NUMBER_TEXTAREA))
        txt_el.clear()
        txt_el.send_keys(part_number)
        logger.info(f"Entered part_number={part_number} into textarea")

        # --- жмём Search ---
        btn_search = wait.until(EC.element_to_be_clickable(SEARCH_BUTTON))
        btn_search.click()
        logger.info("Clicked 'Search' button for item search.")

        # --- 1. ждём появления спиннера (необязательно, вдруг страница быстрая) ---
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(SPINNER)
            )
            logger.debug("Spinner appeared.")
        except TimeoutException:
            # спиннер не показался — бывает, если результаты мгновенные
            pass

        # --- 2. ждём исчезновения спиннера ---
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(SPINNER)
        )
        logger.debug("Spinner disappeared.")

        # --- 3. ждём таблицу результатов ---
        wait.until(EC.presence_of_element_located(SEARCH_RESULTS_TABLE))
        logger.info("Search results table appeared.")
        return {"success": True, "error": None}

    except TimeoutException as te:
        err = f"Timeout in input_part_number_and_search({part_number}): {str(te)}"
        logger.error(err)
        return {"success": False, "error": err}

    except Exception as ex:
        err = f"Exception in input_part_number_and_search({part_number}): {str(ex)}"
        logger.error(err)
        return {"success": False, "error": err}
