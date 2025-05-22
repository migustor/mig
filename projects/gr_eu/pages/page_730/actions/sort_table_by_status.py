# common/pages/page_730/actions/sort_table_by_status.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from projects.gr_eu.pages.page_730.locators import STATUS_HEADER_TH, TABLE_CONTAINER

logger = logging.getLogger(__name__)

def sort_table_by_status(driver, timeout=15):
    """
    Кликаем по заголовку таблицы (Status), чтобы отсортировать.
    После клика ждём, пока таблица обновится.
    """
    try:
        wait = WebDriverWait(driver, timeout)

        th_el = wait.until(EC.element_to_be_clickable(STATUS_HEADER_TH))
        th_el.click()
        logger.info("Clicked on 'Status' header to sort table.")

        # Ждём, пока таблица перегрузится (или используем тот же локатор TABLE_CONTAINER)
        # В простом случае, дадим паузу:
        time.sleep(2)

        # Или более тщательно: ждём исчезновения/появления чего-то, но часто хватает sleep(2).
        # ---
        # Возвращаем True
        return {"success": True, "error": None}
    except TimeoutException as e:
        err = f"Timeout waiting for Status header to be clickable: {e}"
        logger.error(err)
        return {"success": False, "error": err}
    except Exception as ex:
        err = f"Error while sorting by Status: {ex}"
        logger.error(err)
        return {"success": False, "error": err}
