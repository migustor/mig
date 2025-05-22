# projects/gr_eu/pages/page_57/workflow/quick_position_search.py
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from projects.gr_eu.pages.page_57.actions.open_position_dropdown import open_position_dropdown
from projects.gr_eu.pages.page_57.actions.search_position_keyword import search_position_keyword
from projects.gr_eu.pages.page_57.actions.click_add_new_position import click_add_new_position

logger = logging.getLogger(__name__)

KEYWORDS = ["Manager", "Representative", "QA"]


def _run_keyword_cycle(driver, keywords, timeout):
    for kw in keywords:
        if not search_position_keyword(driver, kw, timeout):
            raise AssertionError(f"Поиск по '{kw}' не прошёл")


def run_quick_position_search(driver, timeout: int = 15):
    """
    Полный цикл:
      1. «Create Employee»
      2. Проверяем позиции в первом селекте
      3. Добавляем ещё один селект и проверяем те же ключевые слова
    """
    logger.info("=== Starting quick_position_search workflow ===")

    wait = WebDriverWait(driver, timeout)

    # 1) «Create Employee»
    create_btn = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        "a[href*='page_id=57'][href*='phase=new']"
    )))
    create_btn.click()
    logger.info("Clicked [Create Employee]")

    # форма готова
    wait.until(
        lambda d: (
            d.find_elements(By.ID, "frm_employee") or
            d.find_elements(By.CSS_SELECTOR, '#employee_position_0')
        )
    )
    logger.info("Create-Employee form is ready")

    # 2) Первый селект
    open_position_dropdown(driver, timeout, select_index=0)
    _run_keyword_cycle(driver, KEYWORDS, timeout)

    # закрываем дроп (клик по кнопке ещё раз)
    driver.find_element(By.CSS_SELECTOR,
                        '#employee_position_0 + div.btn-group > button').click()

    # 3) Добавляем второй селект
    click_add_new_position(driver, timeout)
    open_position_dropdown(driver, timeout, select_index=1)
    _run_keyword_cycle(driver, KEYWORDS, timeout)

    logger.info("=== quick_position_search успешно завершён ===")
