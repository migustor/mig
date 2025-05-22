# projects/gr_eu/pages/page_57/actions/open_position_dropdown.py
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


def open_position_dropdown(driver, timeout: int = 15, select_index: int = 0):
    """
    Открывает выпадающий список позиции по индексу:
       <select id="employee_position_{index}">
    Bootstrap-Multiselect рендерит к нему .btn-group > button; кликаем по
    клавише, ждём появления UL-контейнера.

    Возвращает объект UL (WebElement) либо None.
    """
    try:
        wait = WebDriverWait(driver, timeout)

        # Кнопка возле скрытого <select>
        btn = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f'#employee_position_{select_index} + div.btn-group > button'
            ))
        )
        btn.click()
        logger.info("Открыли drop-down позиции #%s", select_index)

        # Видимый UL с вариантами
        ul = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "ul.multiselect-container.dropdown-menu"
            ))
        )
        return ul

    except TimeoutException:
        logger.error("Не удалось открыть drop-down позиции #%s", select_index)
        return None
    