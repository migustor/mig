# common/pages/page_730/actions/open_first_link_in_table.py
import logging
import time
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

def open_first_link_in_table(driver, table_element):
    """
    Находит первую ссылку в tbody tr (колонка Full Name, например),
    открывает её в новой вкладке. Возвращает URL, чтобы мы могли потом искать его.
    """
    try:
        rows = table_element.find_elements(By.CSS_SELECTOR, "tbody tr")
        if not rows:
            msg = "No rows in the table"
            logger.warning(msg)
            return {"success": True, "error": None, "link_url": None}

        first_link = None
        for row in rows:
            links = row.find_elements(By.CSS_SELECTOR, "td a")
            if links:
                first_link = links[0].get_attribute("href")
                break

        if not first_link:
            msg = "No link found in any row"
            logger.warning(msg)
            return {"success": True, "error": None, "link_url": None}

        logger.info(f"Opening link in new tab: {first_link}")
        driver.execute_script("window.open(arguments[0], '_blank');", first_link)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)

        return {"success": True, "error": None, "link_url": first_link}

    except Exception as e:
        err = f"Error in open_first_link_in_table: {e}"
        logger.error(err)
        return {"success": False, "error": err, "link_url": None}
