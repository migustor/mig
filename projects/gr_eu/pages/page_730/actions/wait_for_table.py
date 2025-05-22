# common/pages/page_730/actions/wait_for_table.py
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from projects.gr_eu.pages.page_730.locators import TABLE_CONTAINER

logger = logging.getLogger(__name__)

def wait_for_table(driver, timeout=15):
    """
    Ожидает появления таблицы (panel-default[data-grid-view-form-id="frm_search"]).
    Возвращает WebElement таблицы (или None, если не найдено).
    """
    try:
        wait = WebDriverWait(driver, timeout)
        table_el = wait.until(EC.presence_of_element_located(TABLE_CONTAINER))
        logger.info("Table container appeared on page 730")
        return table_el
    except TimeoutException as te:
        err_msg = f"Timeout waiting for results table: {str(te)}"
        logger.error(err_msg)
        return None
    except Exception as e:
        logger.error(f"Unexpected error in wait_for_table: {str(e)}")
        return None
