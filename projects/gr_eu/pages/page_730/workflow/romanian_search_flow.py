# common/pages/page_730/workflow/romanian_search_flow.py
import logging
import time
from selenium.webdriver.common.by import By

from projects.gr_eu.pages.page_730.workflow.run_search_workflow import run_search_workflow
from projects.gr_eu.pages.page_729.actions.detail_page_actions import check_language_and_level

# например, функция, проверяющая XLS
from common.utils.wait_for_xls_and_check import wait_for_xls_and_check

logger = logging.getLogger(__name__)

ALL_LEVELS = [
    "Native", "Default", "A1", "A2", "B1", "B2", "C1", "C2"
]

def test_romanian_search(driver, level_name, timeouts):
    """
    Тест на поиск (Romanian + level_name), проверку колонок, экспорт и т.д.
    Возвращает {success: bool, error: str}
    """
    try:
        table_element = run_search_workflow(
            driver,
            language="Romanian",
            level=level_name,
            timeout=timeouts.get("action", 15)
        )

        # Ищем ссылки в колонке Full Name
        rows = table_element.find_elements(By.CSS_SELECTOR, "tbody tr")
        links = []
        for row in rows:
            try:
                link = row.find_element(By.CSS_SELECTOR, "td a").get_attribute("href")
                links.append(link)
            except:
                pass

        if not links:
            return {"success": False, "error": f"No links found for level={level_name}"}

        first_link = links[0]
        logger.info(f"Opening link: {first_link}")
        driver.execute_script("window.open(arguments[0], '_blank');", first_link)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)

        # Проверяем язык+уровень на странице 729
        check_language_and_level(driver, "Romanian", level_name)
        first_name_value = driver.find_element(By.ID, "first_name").get_attribute("value")
        logger.info(f"first_name from page 729: {first_name_value}")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # Экспорт
        export_btn = driver.find_element(By.ID, "export_btn")
        export_btn.click()

        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        wait = WebDriverWait(driver, 30)
        result_div = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#result .alert.alert-info")))
        download_link = result_div.find_element(By.TAG_NAME, "a")
        download_link.click()

        # Проверка XLS
        import os
        script_dir = timeouts.get("download_dir") or os.path.dirname(__file__)

        wait_for_xls_and_check(
            download_dir=script_dir,
            first_name_expected=first_name_value,
            timeout=30
        )

        return {"success": True, "error": None}

    except Exception as e:
        err = str(e)
        logger.error(f"test_romanian_search error: {err}")
        return {"success": False, "error": err}


def run_all_romanian_levels_test(driver, timeouts):
    """
    Запускает test_romanian_search для всех уровней из ALL_LEVELS.
    """
    logger.info("=== Starting run_all_romanian_levels_test ===")
    for level in ALL_LEVELS:
        logger.info(f"Subtest for level={level}")
        res = test_romanian_search(driver, level, timeouts)
        if not res["success"]:
            return {"success": False, "error": f"Level '{level}' failed: {res['error']}"}

    return {"success": True, "error": None}
