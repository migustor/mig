import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from common.utils.error_handling import jenkins_aware

# ---------------------------------------------------------------------------
# settings_for_po (per‑field select update & detailed logging)
# ---------------------------------------------------------------------------
# • Checks each dropdown (Payment Term, Shipping Carrier, Freight Type) one‑by‑one
#   → reads current value; if equal to the desired value — skips, else updates.
# • Updates fire their own JS and dispatch the native 'change' event.
# • Every action is logged, so Jenkins output shows exactly what happened.
# ---------------------------------------------------------------------------

@jenkins_aware()
def configure_po_settings(
    driver,
    *,
    timeouts: dict | None = None,
    payment_term_val: str = "40",     # 50 % pre‑payment
    shipping_carrier_val: str = "54",  # BPS
    freight_type_val: str = "2",       # SovaMax Pays Freight
):
    """Configure Purchase Order fields and save.

    Args:
        driver: Selenium WebDriver instance already on the PO page.
        timeouts: Optional mapping → {"action": seconds for explicit waits}.
        payment_term_val: value for Payment Term dropdown.
        shipping_carrier_val: value for Shipping Carrier dropdown.
        freight_type_val: value for Freight Type dropdown.
    """

    logger = logging.getLogger("test")
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)

    try:
        wait = WebDriverWait(driver, action_timeout)

        # --- Address selection ------------------------------------------------
        logger.info("[PO] Opening address selector …")
        wait.until(EC.element_to_be_clickable((By.XPATH,
            "//*[@id='general_information']/div[5]/div[2]/div/div[1]/fieldset[2]/legend/button"))).click()
        time.sleep(1.5)

        logger.info("[PO] Confirming address …")
        wait.until(EC.element_to_be_clickable((By.XPATH,
            "//*[@id='address_editor_form']/div[2]/div/div/div/div[2]/table/tbody/tr[2]/td[1]/div/button"))).click()
        time.sleep(1.5)

        # --- Lot selection ----------------------------------------------------
        logger.info("[PO] Selecting lot …")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='price_per_section']/div[1]/label"))).click()
        time.sleep(1)

        # --- Contact selection ------------------------------------------------
        logger.info("[PO] Choosing contact …")
        contact_dd = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='responsible_user_id']")))
        contact_dd.click(); contact_dd.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
        time.sleep(1)

        # --- Email selection --------------------------------------------------
        logger.info("[PO] Choosing email …")
        email_dd = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='responsible_email_id']")))
        email_dd.click(); email_dd.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
        time.sleep(1)

        # --- Helper to update <select> safely ---------------------------------
        def _update_select_if_needed(dom_id: str, desired: str, label: str):
            current = driver.execute_script("return document.getElementById(arguments[0])?.value", dom_id)
            logger.info("[PO] %s → current=%s, desired=%s", label, current, desired)
            if str(current) == str(desired):
                logger.info("[PO] %s already correct → skip", label)
                return "skipped"
            driver.execute_script(
                """
                const el = document.getElementById(arguments[0]);
                if (el) {
                    const oldVal = el.value;
                    el.value = arguments[1];
                    el.dispatchEvent(new Event('change', {bubbles:true}));
                    return oldVal;
                }
                return null;
                """, dom_id, str(desired))
            logger.info("[PO] %s changed to %s", label, desired)
            time.sleep(0.6)
            return "changed"

        # --- Update dropdowns sequentially ------------------------------------
        results = {
            "PaymentTerm": _update_select_if_needed("payment_term_id",    payment_term_val,    "Payment Term"),
            "ShipCarrier": _update_select_if_needed("shipping_carrier_id", shipping_carrier_val, "Shipping Carrier"),
            "FreightType": _update_select_if_needed("freight_type_id",    freight_type_val,    "Freight Type"),
        }
        logger.info("[PO] Dropdown update results → %s", results)

        # --- Transfer items from Lead to PO -----------------------------------
        logger.info("[PO] Opening 'Add items to PO' dialog …")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='lead_items_to_po_show']/h4"))).click()
        time.sleep(1.5)

        logger.info("[PO] Adding all items from Lead to PO …")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='add_all_items_from_lead']"))).click()
        time.sleep(1.5)

        # --- Save PO -----------------------------------------------------------
        logger.info("[PO] Saving PO changes …")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='result']"))).click()
        time.sleep(2)

        logger.info("[PO] PO settings saved successfully.")
        return {"success": True, "error": None, "dropdown_results": results}

    except Exception as exc:
        err_msg = f"Error while configuring PO settings: {exc}"
        logger.error(err_msg)
        return {"success": False, "error": err_msg}
