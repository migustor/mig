# ───────────── allocate_waterfall_cost.py ────────────────
"""Allocate waterfall cost by setting *max waterfall buys* on the
Receipt page (879). The function stays in the **same tab**: it no
longer clicks the receipt link that would normally open a new window.
Instead, it extracts the *receipt_id* and navigates to page 879 via
`get_page_879_url`.

Extraction strategy keeps the **original behaviour** (digits from link
text) but adds a safe fallback to `href` in case the text is empty.
"""

import logging
import re

from selenium.webdriver.common.by      import By
from selenium.webdriver.support.ui     import WebDriverWait
from selenium.webdriver.support        import expected_conditions as EC

from common.utils.timeouts             import smart_sleep
from common.utils.error_handling       import jenkins_aware
from common.pages.page_839.page_info   import get_page_839_url
from common.pages.page_879.page_info   import get_page_879_url


@jenkins_aware()
def allocate_waterfall_cost(
    driver,
    project: str,
    po_id: str,
    tout: int = 20,
) -> dict:
    """Set *max waterfall buys* on receipt and return ``receipt_id``.

    Workflow:
    1. Open PO page 839.
    2. Read *receipt_id* from the link text (fallback — from ``href``).
    3. Build URL for page 879 and open it **in the same tab**.
    4. Grab the PO € value and submit it into *waterfall_max_buys*.
    """

    log  = logging.getLogger("test")
    wait = WebDriverWait(driver, tout)

    try:
        # 1 ── PO page ────────────────────────────────────────────────
        url_po = get_page_839_url(project, po_id)
        log.info("[839] %s", url_po)
        driver.get(url_po)
        smart_sleep("medium", "PO page load")

        # 2 ── Receipt link (no click) ───────────────────────────────
        rec_link = wait.until(EC.visibility_of_element_located((
            By.XPATH,
            '//*[@id="general_information"]//a[contains(@href,"page_id=879")]',
        )))

        text_digits = re.search(r"(\d{5,})", rec_link.text or "")
        href_digits = re.search(r"receipt_id=(\d+)", rec_link.get_attribute("href") or "")
        m = text_digits or href_digits
        if not m:
            raise ValueError("Cannot extract receipt_id from link")
        receipt_id = m.group(1)
        log.info("Receipt id → %s", receipt_id)

        # 3 ── Receipt page (same tab) ───────────────────────────────
        url_rec = get_page_879_url(project, receipt_id)
        log.info("[879] %s", url_rec)
        driver.get(url_rec)
        smart_sleep("medium", "receipt page load")

        # 4 ── Grab PO value (first € cell) ──────────────────────────
        cell = wait.until(EC.visibility_of_element_located(
            (By.XPATH, '//td[contains(text(), "€")]')))
        match_val = re.search(r"([\d\.]+)", cell.text)
        if not match_val:
            raise ValueError("Could not parse euro value on receipt page")
        value = match_val.group(1)
        log.info("PO value €%s", value)

        # 5 ── Set *max waterfall buys* ──────────────────────────────
        wb_in = wait.until(EC.element_to_be_clickable((By.ID, "waterfall_max_buys")))
        wb_in.clear(); wb_in.send_keys(value)
        wait.until(EC.element_to_be_clickable((By.ID, "waterfall_max_buys_button"))).click()
        smart_sleep("medium", "max buys set")

        return {"success": True, "receipt_id": receipt_id}

    except Exception as exc:
        log.error("allocate_waterfall_cost ❌ %s", exc)
        return {"success": False, "error": str(exc)}
