# ───────────────── stock_items.py ──────────────────
import logging

from selenium.webdriver.common.by      import By
from selenium.webdriver.common.keys    import Keys
from selenium.webdriver.support.ui     import WebDriverWait
from selenium.webdriver.support        import expected_conditions as EC

from common.utils.timeouts             import smart_sleep
from common.utils.error_handling       import jenkins_aware
from common.pages.warehouse.stocking.page_info import get_stocking_url

@jenkins_aware()
def stock_items(
    driver,
    project: str,
    barcode: str,
    location: str = "VLT628",
    tout: int = 20
) -> dict:
    """
    Stock received item into warehouse location.
    """
    log  = logging.getLogger("test")
    wait = WebDriverWait(driver, tout)

    try:
        url = get_stocking_url(project)
        log.info("[stocking] %s", url)
        driver.get(url)
        smart_sleep("medium", "stocking page load")

        in_code = wait.until(EC.element_to_be_clickable((By.ID, "in_code")))
        in_code.clear(); in_code.send_keys(barcode); in_code.send_keys(Keys.ENTER)
        smart_sleep("medium", "barcode entered")

        in_code.clear(); in_code.send_keys(location); in_code.send_keys(Keys.ENTER)
        smart_sleep("medium", "location entered")

        return {"success": True}
    except Exception as exc:
        log.error("stock_items ❌ %s", exc)
        return {"success": False, "error": str(exc)}
