# projects/gr_eu/pages/page_729/actions/click_add_new_position.py
import logging, time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from projects.gr_eu.pages.page_729.locators import ADD_NEW_POSITION_BTN

logger = logging.getLogger(__name__)

def click_add_new_position(driver, timeout=10):
    """
    Нажимает кнопку “add new Position” и ждёт,
    пока в <div id="position_div"> появится новый <select name="position_id">.
    """
    try:
        # сколько селектов было ДО нажатия
        before = len(driver.find_elements(*POSITION_SELECTS))

        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(ADD_NEW_POSITION_BTN)
        ).click()
        logger.info("Clicked 'add new Position'")

        # ждём +1 селект
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(*POSITION_SELECTS)) == before + 1
        )
        time.sleep(0.5)      # мелкая пауза, пока мультиселект инициализируется bootstrap-скриптом
        return {"success": True, "error": None}
    except TimeoutException as e:
        return {"success": False, "error": f\"Timeout waiting for new position select: {e}\"}
