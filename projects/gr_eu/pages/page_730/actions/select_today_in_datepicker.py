# common/pages/page_730/actions/select_today_in_datepicker.py
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from projects.gr_eu.pages.page_730.locators import TODAY_DAY_IN_CALENDAR
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

def select_today_in_datepicker(driver, timeout=15):
    """
    Предполагается, что календарь уже открыт, и нужно кликнуть по "today day".
    Либо, если нужно открыть календарь, делаем это до вызова этой функции.
    """
    try:
        wait = WebDriverWait(driver, timeout)
        today_el = wait.until(EC.element_to_be_clickable(TODAY_DAY_IN_CALENDAR))
        today_el.click()
        time.sleep(1)
        logger.info("Clicked 'today' in datepicker.")
        return {"success": True, "error": None}
    except TimeoutException as e:
        err = f"Timeout waiting for 'today' in datepicker: {e}"
        logger.error(err)
        return {"success": False, "error": err}
    except Exception as ex:
        err = f"Error clicking 'today' day: {ex}"
        logger.error(err)
        return {"success": False, "error": err}
