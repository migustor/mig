# common/pages/page_730/actions/select_language.py
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from projects.gr_eu.pages.page_730.locators import LANGUAGE_SELECT
from selenium.webdriver.support.ui import Select

logger = logging.getLogger(__name__)


def select_language(driver, language="Romanian", timeout=10):
    """
    Работает через JS, снимает все и выбирает язык с нужным value.
    """
    try:
        lang_map = {
            "Romanian": "28",
            
        }
        language_value = lang_map.get(language)
        if not language_value:
            raise ValueError(f"Неизвестный язык: {language}")

        driver.execute_script("$('#languages').multiselect('deselectAll', false);")
        driver.execute_script(f"$('#languages').multiselect('select', '{language_value}');")
        driver.execute_script("$('#languages').multiselect('updateButtonText');")
        logger.info(f"[JS] Succesfully click language: {language} (value={language_value})")
        return {"success": True, "error": None}
    except Exception as e:
        err_msg = f"[JS] Error on choose language {language}: {e}"
        logger.error(err_msg)
        return {"success": False, "error": err_msg}
