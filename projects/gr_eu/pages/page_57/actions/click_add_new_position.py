# projects/gr_eu/pages/page_57/actions/click_add_new_position.py
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


def click_add_new_position(driver, timeout: int = 10):
    """
    Нажимает «add new Position» и ждёт появления
    <select id="employee_position_1">.
    """
    wait = WebDriverWait(driver, timeout)
    add_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "add_new_position"))
    )
    add_btn.click()
    logger.info("Clicked [add new Position]")

    # подтверждение появления нового селекта
    wait.until(
        EC.presence_of_element_located((By.ID, "employee_position_1"))
    )
