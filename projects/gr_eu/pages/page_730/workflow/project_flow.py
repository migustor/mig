# common/pages/page_730/workflow/projects_flow.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from projects.gr_eu.pages.page_730.actions.select_project import select_project_js
from common.utils.wait_for_xls_and_check import wait_for_xls_and_check

logger = logging.getLogger(__name__)

PROJECTS_TO_TEST = [
    ("Agava", "5"),
    ("Argon Trading", "26"),
    ("MTEAM", "2"),
]

def test_projects_flow(driver, script_dir, timeouts):
    """
    Дополнительная проверка проектов:
      1. Снимаем все чекбоксы
      2. Выбираем нужный проект
      3. Search -> первая ссылка
      4. Переход на 729 -> проверяем select id=candidate_projects_1
      5. Экспорт -> проверка XLS
    """
    logger.info("=== Начинаем проверку проектов (Agava, Argon, MTEAM) ===")

    # Переходим на page_id=730 (прим. URL может быть разным)
    driver.get("https://stage15.office.grafit.md/sage/index.cfm?page_id=730")
    time.sleep(2)

    for proj_name, proj_value in PROJECTS_TO_TEST:
        logger.info(f"--- Subtest project={proj_name}, value={proj_value} ---")

        # 1) Выбираем проект
        select_project_js(driver, proj_value)

        # 2) Search
        search_btn = driver.find_element(By.XPATH, '//button[@type="submit" and contains(.,"Search")]')
        search_btn.click()

        # 3) Ждём таблицу
        wait = WebDriverWait(driver, timeouts.get("action", 15))
        table_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.panel.panel-default[data-grid-view-form-id="frm_search"]')))
        rows = table_container.find_elements(By.CSS_SELECTOR, "tbody tr")
        if not rows:
            err = f"No rows found for project={proj_name}"
            logger.error(err)
            return {"success": False, "error": err}

        first_link = rows[0].find_element(By.CSS_SELECTOR, "td a").get_attribute("href")
        logger.info(f"First link for {proj_name} => {first_link}")

        # 4) Открываем в новой вкладке
        driver.execute_script("window.open(arguments[0], '_blank');", first_link)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)

        sel = Select(driver.find_element(By.ID, "candidate_projects_1"))
        actual_value = sel.first_selected_option.get_attribute("value")
        if actual_value != proj_value:
            err = f"Expected project_value={proj_value}, got={actual_value}"
            logger.error(err)
            return {"success": False, "error": err}

        logger.info(f"Project on 729 is correct: {proj_name}")

        # Считываем first_name
        first_name_value = driver.find_element(By.ID, "first_name").get_attribute("value")
        logger.info(f"first_name={first_name_value}")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # 5) Экспорт
        export_btn = driver.find_element(By.ID, "export_btn")
        export_btn.click()

        result_div = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#result .alert.alert-info")))
        download_link = result_div.find_element(By.TAG_NAME, "a")
        download_link.click()

        # Проверяем XLS
        wait_for_xls_and_check(download_dir=script_dir, first_name_expected=first_name_value, timeout=30)
        logger.info(f"[OK] XLS check for {proj_name} done.")

    logger.info("[OK] All projects tested successfully.")
    return {"success": True, "error": None}
