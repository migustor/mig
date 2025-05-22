# projects/et_eu/pages/page_888/actions/click_add_more_items_panel.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException
)
from selenium.webdriver.common.by import By

# ⇒ добавьте импорт textarea‑локатора
from projects.et_eu.pages.page_888.locators_item_search import PART_NUMBER_TEXTAREA

logger = logging.getLogger(__name__)

def click_add_more_items_panel(driver, timeout=15):
    """
    Делает панель открытой (идемпотентно).
    • Если textarea уже видна → панель раскрыта → сразу success.
    • Иначе кликаем по <div id="item_search_form"> и ждём появления textarea.
    """
    try:
        wait = WebDriverWait(driver, timeout)

        # --- 1. Проверяем, открыта ли уже панель ---
        visible_txt = [
            el for el in driver.find_elements(*PART_NUMBER_TEXTAREA)
            if el.is_displayed()
        ]
        if visible_txt:
            logger.info("'Add More Items' panel is already open.")
            return {"success": True, "error": None}

        # --- 2. Панель закрыта → кликаем заголовок ---
        header = wait.until(
            EC.element_to_be_clickable((By.ID, "item_search_form"))
        )
        header.click()
        # ждём, пока textarea появится
        wait.until(EC.visibility_of_element_located(PART_NUMBER_TEXTAREA))
        time.sleep(0.5)
        logger.info("Clicked 'Add More Items' panel heading.")
        return {"success": True, "error": None}

    except ElementClickInterceptedException:
        # если click перехвачен, но textarea уже видна → считаем, что панель открыта
        visible_txt = [
            el for el in driver.find_elements(*PART_NUMBER_TEXTAREA)
            if el.is_displayed()
        ]
        if visible_txt:
            logger.info("'Add More Items' panel already open "
                        "(click intercepted, but textarea visible).")
            return {"success": True, "error": None}
        err = "Element click intercepted and panel still closed."
        logger.error(err)
        return {"success": False, "error": err}

    except TimeoutException as te:
        err = f"Timeout opening 'Add More Items' panel: {te}"
        logger.error(err)
        return {"success": False, "error": err}

    except Exception as ex:
        err = f"Error clicking 'Add More Items' panel: {ex}"
        logger.error(err)
        return {"success": False, "error": err}
