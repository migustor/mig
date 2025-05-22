# ───────────── post_po_and_check.py ────────────────
import logging
import re
import time                                          # ← new

from selenium.webdriver.common.by      import By
from selenium.webdriver.support.ui     import WebDriverWait
from selenium.webdriver.support        import expected_conditions as EC
from selenium.common.exceptions        import NoSuchElementException  # ← new

from common.utils.timeouts             import smart_sleep
from common.utils.error_handling       import jenkins_aware
from common.pages.page_879.page_info   import get_page_879_url

_POSTED_RX   = re.compile(r"PO is already Posted", re.I)
_MAX_RETRIES = 3        # post-button attempts
_PAUSE_SEC   = 3        # hard pause after clicking Post

@jenkins_aware()
def post_po_and_check(
    driver,
    project: str,
    receipt_id: str,
    tout: int = 20,
) -> dict:
    """Post PO to GP from receipt page and verify banner."""
    log  = logging.getLogger("test")
    wait = WebDriverWait(driver, tout)

    try:
        url = get_page_879_url(project, receipt_id)
        log.info("[879] %s", url)
        driver.get(url)
        smart_sleep("medium", "receipt page load")

        # ── click Post + Yes with retry ─────────────────────────────
        for attempt in range(1, _MAX_RETRIES + 1):
            wait.until(
                EC.element_to_be_clickable((By.ID, "post_po_to_gp_button"))
            ).click()
            log.info("Clicked Post (try %s/%s)", attempt, _MAX_RETRIES)

            time.sleep(_PAUSE_SEC)  # strict pause
            try:
                yes_btn = driver.find_element(
                    By.XPATH, '//*[@id="confirmButtons"]/a[1]'
                )
                yes_btn.click()
                log.info("Clicked Yes")
                break  # success
            except NoSuchElementException:
                log.warning("Yes popup not found (try %s)", attempt)
                if attempt == _MAX_RETRIES:
                    return {
                        "success": False,
                        "error": "Yes-popup did not appear after "
                                 f"{_MAX_RETRIES} attempts",
                    }

        smart_sleep("long", "GP posting")

        # ── reload & check banner ──────────────────────────────────
        driver.get(url)
        smart_sleep("medium", "post reload")
        if _POSTED_RX.search(driver.page_source):
            log.info("PO posted ✅")
            return {"success": True}
        return {"success": False, "error": "Confirmation banner not found"}

    except Exception as exc:
        log.error("post_po_and_check ❌ %s", exc)
        return {"success": False, "error": str(exc)}
