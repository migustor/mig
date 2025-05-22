# common/pages/page_730/actions/select_language_level.py
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from projects.gr_eu.pages.page_730.locators import LANGUAGE_LEVEL_SELECT
from selenium.webdriver.support.ui import Select

logger = logging.getLogger(__name__)

def select_language_level(driver, level_name, timeout=15):
    """
    Выбирает указанный уровень (name="language_level_id").
    """
    try:
        wait = WebDriverWait(driver, timeout)
        level_el = wait.until(EC.presence_of_element_located(LANGUAGE_LEVEL_SELECT))
        Select(level_el).select_by_visible_text(level_name)
        logger.info(f"Selected language_level={level_name} in <select name='language_level_id'>")
        return {"success": True, "error": None}
    except (TimeoutException, NoSuchElementException) as e:
        err_msg = f"Failed to select language_level='{level_name}': {str(e)}"
        logger.error(err_msg)
        return {"success": False, "error": err_msg}
    except StaleElementReferenceException as se:
        err_msg = f"StaleElementReferenceException on select_language_level: {str(se)}"
        logger.error(err_msg)
        return {"success": False, "error": err_msg}
    except Exception as ex:
        err_msg = f"Unexpected error in select_language_level: {str(ex)}"
        logger.error(err_msg)
        return {"success": False, "error": err_msg}
