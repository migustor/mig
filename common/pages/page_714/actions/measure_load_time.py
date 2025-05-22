# common/pages/page_714/actions/measure_load_time.py
import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.pages.page_714.locators import DATA_CONTAINER, LOADING_SPINNER

logger = logging.getLogger(__name__)

def measure_page714_load_time(driver, timeout=30):
    """
    Считает, сколько миллисекунд проходит между открытием URL и полной
    отрисовкой данных (DATA_CONTAINER виден, LOADING_SPINNER исчез).
    Вернёт dict с ключами success / error / load_time_ms.
    """
    start = time.perf_counter()

    wait = WebDriverWait(driver, timeout)

    try:
        # 1. Ждём появления контейнера с данными
        wait.until(EC.presence_of_element_located(DATA_CONTAINER))
        # 2. Ждём, пока спиннер полностью исчезнет (если он вообще есть)
        wait.until_not(EC.presence_of_element_located(LOADING_SPINNER))
    except Exception as e:
        err = f"Данные не успели прогрузиться за {timeout}s: {e}"
        logger.error(err)
        return {"success": False, "error": err, "load_time_ms": None}

    load_time_ms = round((time.perf_counter() - start) * 1000)
    logger.info(f"[714] Данные загружены за {load_time_ms} мс")
    return {"success": True, "error": None, "load_time_ms": load_time_ms}
