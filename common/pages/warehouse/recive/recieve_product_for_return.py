# ───────────── recieve_product_for_return.py ─────────────
"""Receive product by EAN and assign provided barcode.

The barcode is generated earlier in the E2E flow by `get_barcode.py`.
This module only inputs the EAN, registers product, fills barcode,
and submits the form. Comments/logs English only per project guideline.
"""

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.utils.timeouts import smart_sleep
from common.utils.error_handling import jenkins_aware


@jenkins_aware()
def recieve_product_for_return(
    driver,
    ean: str,
    barcode: str,
    tout: int = 20,
) -> dict:
    """Receive product identified by *ean* and assign *barcode*.

    Parameters
    ----------
    driver : selenium.webdriver
        Selenium WebDriver already on the “Receive product” page.
    ean : str
        Product EAN (part number) to receive.
    barcode : str
        Pre‑generated unique barcode string.
    tout : int, optional
        Explicit‑wait timeout in seconds (default **20**).

    Returns
    -------
    dict
        {"success": bool, "barcode": str, "error": str | None}
    """

    log = logging.getLogger("test")
    wait = WebDriverWait(driver, tout)

    try:
        log.info("[receive] EAN %s", ean)

        # 1 ── Enter EAN
        ean_in = wait.until(EC.element_to_be_clickable((By.ID, "part_number")))
        ean_in.clear()
        ean_in.send_keys(ean)
        smart_sleep("short", "EAN entered")

        # 2 ── Register product
        wait.until(EC.element_to_be_clickable((By.ID, "register_product"))).click()
        smart_sleep("medium", "product registered")

        # 3 ── Enter provided barcode
        bc_in = wait.until(EC.element_to_be_clickable((By.ID, "universal")))
        bc_in.clear()
        bc_in.send_keys(barcode)
        bc_in.send_keys(Keys.ENTER)
        smart_sleep("short", "barcode entered")

        # 4 ── Submit receive form
        wait.until(EC.element_to_be_clickable((By.ID, "submit_btn"))).click()
        smart_sleep("medium", "receive submit")

        return {"success": True, "barcode": barcode, "error": None}
    except Exception as exc:
        log.error("recieve_product_for_return ❌ %s", exc)
        return {"success": False, "barcode": None, "error": str(exc)}
