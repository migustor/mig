# common/pages/page_730/actions/click_search_button.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from projects.gr_eu.pages.page_730.locators import SEARCH_BUTTON

logger = logging.getLogger(__name__)

def click_search_button(driver, timeout=15):
    """
    Кликает по кнопке 'Search'.
    """
    try:
        wait = WebDriverWait(driver, timeout)
        search_btn = wait.until(EC.element_to_be_clickable(SEARCH_BUTTON))
        search_btn.click()
        time.sleep(1)  # небольшая пауза для UI
        logger.info("Clicked Search button")
        return {"success": True, "error": None}
    except TimeoutException as te:
        err_msg = f"Timeout waiting for Search button: {str(te)}"
        logger.error(err_msg)
        return {"success": False, "error": err_msg}
    except Exception as e:
        err_msg = f"Error clicking Search button: {str(e)}"
        logger.error(err_msg)
        return {"success": False, "error": err_msg}
