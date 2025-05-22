# common/pages/page_730/workflow/after_test_flow.py
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Actions для страницы 730
from projects.gr_eu.pages.page_730.actions.click_search_button import click_search_button
from projects.gr_eu.pages.page_730.actions.wait_for_table import wait_for_table
from projects.gr_eu.pages.page_730.actions.sort_table_by_status import sort_table_by_status
from projects.gr_eu.pages.page_730.actions.open_first_link_in_table import open_first_link_in_table
from projects.gr_eu.pages.page_730.actions.select_date_type import select_date_type
from projects.gr_eu.pages.page_730.actions.select_today_in_datepicker import select_today_in_datepicker

# Actions для страницы 729
from projects.gr_eu.pages.page_729.actions.select_status import select_status
from projects.gr_eu.pages.page_729.actions.select_candidate_project_1 import select_candidate_project_1
from projects.gr_eu.pages.page_729.actions.click_save_button import click_save_button

logger = logging.getLogger(__name__)

def run_after_test_flow(driver, timeouts, stored_link=None):
    """
    Запускает новый функционал:
      1) Заходим/обновляем страницу 730
      2) Нажимаем Search
      3) Сортируем таблицу по Status
      4) Открываем первую ссылку
      5) На 729 меняем status_id -> 413, candidate_projects_1 -> 5, жмём Save
      6) Возвращаемся на 730, меняем date_type -> dismissal_resignation
      7) Открываем календарь, выбираем 'today', жмём Search
      8) Если хотим, проверяем, есть ли в таблице link = stored_link
    """
    logger.info("=== Starting after_test_flow ===")

    # 1) Переходим заново на страницу 730 (или refresh)
    driver.get("https://stage15.office.grafit.md/sage/index.cfm?page_id=730")
    time.sleep(2)

    # 2) Нажимаем Search
    res_click = click_search_button(driver, timeout=timeouts.get("action", 15))
    if not res_click["success"]:
        return {"success": False, "error": f"click_search_button: {res_click['error']}"}

    # 3) Ожидаем таблицу и сортируем по Status
    table_el = wait_for_table(driver, timeout=timeouts.get("action", 15))
    if not table_el:
        return {"success": False, "error": "Failed to find table after Search"}
    sort_res = sort_table_by_status(driver, timeout=timeouts.get("action", 15))
    if not sort_res["success"]:
        return {"success": False, "error": f"sort_table_by_status: {sort_res['error']}"}

    # 3.1) Снова ждём, пока таблица перезагрузится
    table_el = wait_for_table(driver, timeout=timeouts.get("action", 15))
    if not table_el:
        return {"success": False, "error": "Failed to find table after sorting by Status"}

    # 4) Открываем первую ссылку -> переходим на 729
    open_res = open_first_link_in_table(driver, table_el)
    if not open_res["success"]:
        return {"success": False, "error": f"open_first_link_in_table: {open_res['error']}"}
    new_link_url = open_res["link_url"]

    # 5) На 729: select_status -> 413 (Dismissal), select_candidate_project_1 -> 5 (Agava), Save
    sel_stat = select_status(driver, "413", timeout=timeouts.get("action", 15))
    if not sel_stat["success"]:
        return {"success": False, "error": f"select_status: {sel_stat['error']}"}

    sel_proj = select_candidate_project_1(driver, "5", timeout=timeouts.get("action", 15))
    if not sel_proj["success"]:
        return {"success": False, "error": f"select_candidate_project_1: {sel_proj['error']}"}

    save_res = click_save_button(driver, timeout=timeouts.get("action", 15))
    if not save_res["success"]:
        return {"success": False, "error": f"click_save_button: {save_res['error']}"}

    # 5.1) Возвращаемся на 730 (предположим, driver.back() или опять driver.get)
    driver.get("https://stage15.office.grafit.md/sage/index.cfm?page_id=730")
    time.sleep(2)

    # 6) Выбираем date_type = dismissal_resignation
    date_type_res = select_date_type(driver, value="dismissal_resignation", timeout=timeouts.get("action", 15))
    if not date_type_res["success"]:
        return {"success": False, "error": f"select_date_type: {date_type_res['error']}"}

    # 6.1) (Опционально) Открываем календарь - если для этого нужен клик по input?
    # Допустим, у нас есть input#start_date, мы делаем input.click().
    driver.find_element(By.NAME, "date_from").click()
    time.sleep(1)

    # 7) Выбираем today
    pick_res = select_today_in_datepicker(driver, timeout=timeouts.get("action", 15))
    if not pick_res["success"]:
        return {"success": False, "error": f"select_today_in_datepicker: {pick_res['error']}"}

    # 7.1) Нажимаем Search
    res_click2 = click_search_button(driver, timeout=timeouts.get("action", 15))
    if not res_click2["success"]:
        return {"success": False, "error": f"click_search_button: {res_click2['error']}"}

    # 7.2) Ждём таблицу
    table_el2 = wait_for_table(driver, timeout=timeouts.get("action", 15))
    if not table_el2:
        return {"success": False, "error": "Failed to find table after date filter"}

    # 8) Если хотим проверить, что "старая" ссылка (stored_link) есть в таблице:
    if stored_link:
        all_hrefs = []
        rows = table_el2.find_elements(By.CSS_SELECTOR, "tbody tr")
        for r in rows:
            anchors = r.find_elements(By.CSS_SELECTOR, "td a")
            for a in anchors:
                all_hrefs.append(a.get_attribute("href"))
        if stored_link in all_hrefs:
            logger.info(f"[OK] Found previously-stored link in new table results: {stored_link}")
        else:
            logger.warning(f"[WARN] Did NOT find previously-stored link: {stored_link}")

    logger.info("=== after_test_flow completed successfully. ===")
    return {"success": True, "error": None}
