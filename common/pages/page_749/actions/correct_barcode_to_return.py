# ───────────── correct_barcode_to_return.py ────────────────
import logging
import time                                  # ← добавили

from selenium.webdriver.common.by      import By
from selenium.webdriver.common.keys    import Keys
from selenium.webdriver.support.ui     import WebDriverWait
from selenium.webdriver.support        import expected_conditions as EC

from common.utils.timeouts             import smart_sleep
from common.utils.error_handling       import jenkins_aware
from common.pages.page_749.page_info   import get_page_749_url


@jenkins_aware()
def correct_barcode_to_return(
    driver,
    project: str,
    barcode: str,
    tout: int = 20,
) -> dict:
    """
    Mark *barcode* as RETURN via data-correction tool (page 749).
    """
    log  = logging.getLogger("test")
    wait = WebDriverWait(driver, tout)

    try:
        url = get_page_749_url(project)
        log.info("[749] %s", url)
        driver.get(url)
        smart_sleep("medium", "page 749 load")

        # 1 ── Scan barcode
        bc_in = wait.until(EC.element_to_be_clickable((By.ID, "bar_code")))
        bc_in.clear()
        bc_in.send_keys(barcode)
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="data_correct_form"]/div/div[3]/div/div[2]/button')
            )
        ).click()
        smart_sleep("short", "first check")

        # 2 ── Confirm barcode
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="barcodes_frm"]/div[2]/div/div[2]/button')
            )
        ).click()
        smart_sleep("short", "second check")

        # 3 ── Set part number = RETURN
        pn = wait.until(EC.element_to_be_clickable((By.ID, "part_number")))
        pn.clear()
        pn.send_keys("RETURN")
        time.sleep(3)                       # ← строгая 3-секундная пауза
        pn.send_keys(Keys.ENTER)
        smart_sleep("short", "part_number=RETURN + Enter")

        # 4 ── Update
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="update_data"]/div/div[3]/div/div[2]/button')
            )
        ).click()
        smart_sleep("medium", "barcode corrected")

        return {"success": True}

    except Exception as exc:
        log.error("correct_barcode_to_return ❌ %s", exc)
        return {"success": False, "error": str(exc)}
