# common/pages/page_730/workflow/run_search_workflow.py
import logging
from projects.gr_eu.pages.page_730.actions.select_language import select_language
from projects.gr_eu.pages.page_730.actions.select_language_level import select_language_level
from projects.gr_eu.pages.page_730.actions.click_search_button import click_search_button
from projects.gr_eu.pages.page_730.actions.wait_for_table import wait_for_table

logger = logging.getLogger(__name__)

def run_search_workflow(driver, language="Romanian", level="Default", timeout=15):
    """
    Выполняет все шаги на странице 730:
      1) Выбор языка
      2) Выбор уровня
      3) Клик по Search
      4) Ожидание загрузки таблицы
    Возвращает WebElement (таблица) или None, если не получилось.
    """
    # 1) select_language
    res_lang = select_language(driver, language, timeout)
    if not res_lang["success"]:
        raise Exception(f"Failed to select_language: {res_lang['error']}")

    # 2) select_language_level
    res_level = select_language_level(driver, level, timeout)
    if not res_level["success"]:
        raise Exception(f"Failed to select_language_level: {res_level['error']}")

    # 3) click_search_button
    res_click = click_search_button(driver, timeout)
    if not res_click["success"]:
        raise Exception(f"Failed to click Search: {res_click['error']}")

    # 4) wait_for_table
    table_el = wait_for_table(driver, timeout)
    if not table_el:
        raise Exception("Table not found after waiting.")

    logger.info("run_search_workflow completed successfully.")
    return table_el
