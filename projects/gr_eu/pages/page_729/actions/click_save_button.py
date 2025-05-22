# common/pages/page_729/actions/click_save_button.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from projects.gr_eu.pages.page_729.locators import SAVE_BUTTON
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

def click_save_button(driver, timeout=15):
    """
    Клик по кнопке Save на странице 729
    """
    try:
        wait = WebDriverWait(driver, timeout)
        save_btn = wait.until(EC.element_to_be_clickable(SAVE_BUTTON))
        save_btn.click()
        time.sleep(2)
        logger.info("Clicked 'Save' button.")
        return {"success": True, "error": None}
    except TimeoutException as e:
        err = f"Timeout waiting for Save button: {e}"
        logger.error(err)
        return {"success": False, "error": err}
    except Exception as ex:
        err = f"Error clicking Save: {ex}"
        logger.error(err)
        return {"success": False, "error": err}
