# projects/gr_eu/pages/page_57/actions/search_position_keyword.py
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


def _visible_options(container):
    """Список видимых <li>, исключая служебные элементы."""
    return [
        li for li in container.find_elements(By.CSS_SELECTOR, "li")
        if li.is_displayed() and li.text.strip() and
           "multiselect-item" not in li.get_attribute("class")
    ]


def search_position_keyword(driver, keyword: str, timeout: int = 10):
    """
    В уже открытом выпадающем списке (UL.multiselect-container)
    вводит keyword в поле .multiselect-search и убеждается, что
    отображаемые элементы действительно отфильтрованы.

    Логирует:
      [OK] keyword 'QA' — проверка прошла (видимых элементов: 19)
    """
    wait = WebDriverWait(driver, timeout)
    try:
        container = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "ul.multiselect-container.dropdown-menu"
            ))
        )

        # Инпут поиска (появляется внутри UL)
        search_input = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "input.multiselect-search"
            ))
        )
        search_input.clear()
        search_input.send_keys(keyword)

        # ждём, пока список «схлопнется» под фильтр
        def _filtered(driver):
            opts = _visible_options(container)
            return opts and all(keyword.lower() in o.text.lower() for o in opts)

        wait.until(_filtered)
        vis_cnt = len(_visible_options(container))
        logger.info("[OK] keyword '%s' — проверка прошла (видимых элементов: %s)",
                    keyword, vis_cnt)
        # даём UI успеть (визуально приятно, но критично для JS debounce)
        time.sleep(0.3)
        return True
    except TimeoutException:
        logger.error("Поле поиска/фильтра не найдено для keyword='%s'", keyword)
        return False
