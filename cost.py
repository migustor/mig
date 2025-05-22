"""cost.py – End-to-End Lead → PO → Post flow.

Barcode is fetched after PO creation (step 6) via
common.pages.barcode.get_barcode.  Change BARCODE_PROJECT below when a
different project has to be selected in the generator dropdown.

All comments/logs are English-only per project guideline.
"""

import logging
import sys
import time
from urllib.parse import urlparse, parse_qs

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system
from common.utils.timeouts import smart_sleep
from common.utils.error_handling import jenkins_aware

from common.pages.barcode.get_barcode import get_barcode
from common.pages.page_621.actions.create_basic_lead import create_basic_lead
from common.pages.page_621.actions.add_items_to_lead import add_items_to_lead
from common.pages.page_839.actions.settings_for_po import configure_po_settings
from common.pages.page_884.actions.truck_arrival_package import truck_arrival_package
from common.pages.warehouse.recive.recieve_product_for_return import (
    recieve_product_for_return,
)
from common.pages.warehouse.item_details.insert_item_details import insert_item_details
from common.pages.warehouse.stocking.stock_items import stock_items
from common.pages.page_879.actions.allocate_waterfall_cost import allocate_waterfall_cost
from common.pages.page_749.actions.correct_barcode_to_return import (
    correct_barcode_to_return,
)
from common.pages.page_879.actions.post_po_and_check import post_po_and_check

# ─── Static test data ─────────────────────────────────────────────────────
PROJECT_NAME     = "sm_eu"           # system under test
USER_TYPE        = "vb"
COMPANY_ID       = 362674
EAN_CODE         = "4977766525992"

BARCODE_PROJECT  = "SAGE"            # value in <select id="gr_projects">

# ─── Logging setup ─────────────────────────────────────────────────────────
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger("Lead→PO Flow")

# ─── Helpers ───────────────────────────────────────────────────────────────
def _extract_po_id_from_url(url: str) -> str | None:
    """Return po_id if page_id=839 is present in *url*."""
    qs = parse_qs(urlparse(url).query)
    if qs.get("page_id") == ["839"] and "po_id" in qs:
        return qs["po_id"][0]
    return None

# ─── Main test flow ────────────────────────────────────────────────────────
@jenkins_aware()
def test_lead_to_po_flow():
    driver = None
    try:
        # 0 ── Browser
        driver = setup_chrome_driver(headless=False)

        # 1 ── Login
        if not login_as_user(driver, PROJECT_NAME, user_type=USER_TYPE)["success"]:
            raise RuntimeError("Login failed")
        smart_sleep("medium", "after login redirect")

        # 2 ── Create Lead
        lead_res = create_basic_lead(driver, PROJECT_NAME, COMPANY_ID)
        if not lead_res.get("success"):
            raise RuntimeError("Lead creation failed")
        lead_id = lead_res["lead_id"]
        log.info("Lead ID = %s", lead_id)
        smart_sleep("medium")

        # 3 ── Add items
        if not add_items_to_lead(driver, ean=EAN_CODE)["success"]:
            raise RuntimeError("Add items failed")
        smart_sleep("medium", "items added – now on PO page")

        # 3b ── PO ID grab (first attempt)
        time.sleep(5)
        po_id = _extract_po_id_from_url(driver.current_url)

        # 4 ── Configure PO
        if not configure_po_settings(driver)["success"]:
            raise RuntimeError("configure_po_settings failed")

        # 5 ── PO ID grab (retry if needed)
        if not po_id:
            po_id = _extract_po_id_from_url(driver.current_url)
        if not po_id:
            raise RuntimeError("Could not determine PO ID")
        log.info("PO ID = %s", po_id)

        # 6 ── Fetch barcode for selected project
        barcode = get_barcode(driver, BARCODE_PROJECT)
        smart_sleep("short", "barcode ready")

        # 7 ── Truck-arrival package
        if not truck_arrival_package(driver, PROJECT_NAME, po_id)["success"]:
            raise RuntimeError("truck_arrival_package failed")

        # 8 ── Receive product (EAN + barcode)
        recv = recieve_product_for_return(driver, ean=EAN_CODE, barcode=barcode)
        if not recv["success"]:
            raise RuntimeError("Receive product failed")
        log.info("Barcode confirmed = %s", recv['barcode'])

        # 9 ── Insert item details
        if not insert_item_details(driver)["success"]:
            raise RuntimeError("insert_item_details failed")

        # 10 ── Stock items (project + barcode)
        if not stock_items(driver, PROJECT_NAME, barcode)["success"]:
            raise RuntimeError("stock_items failed")

        # 11 ── Waterfall allocation
        alloc = allocate_waterfall_cost(driver, PROJECT_NAME, po_id)
        if not alloc.get("success"):
            raise RuntimeError("allocate_waterfall_cost failed")
        receipt_id = alloc["receipt_id"]
        log.info("Receipt ID = %s", receipt_id)

        # 12 ── Barcode correction
        if not correct_barcode_to_return(driver, PROJECT_NAME, barcode)["success"]:
            raise RuntimeError("correct_barcode_to_return failed")

        # 13 ── Post PO
        if not post_po_and_check(driver, PROJECT_NAME, receipt_id)["success"]:
            raise RuntimeError("post_po_and_check failed")

        # 14 ── Logout
        logout_from_system(driver, PROJECT_NAME)
        log.info(
            "FLOW PASSED ✅ lead %s → po %s → receipt %s (barcode %s)",
            lead_id, po_id, receipt_id, barcode,
        )

    except Exception as exc:
        log.error("FLOW FAILED ❌ %s", exc)
        raise
    finally:
        if driver:
            release_driver(driver)

if __name__ == "__main__":
    sys.exit(test_lead_to_po_flow())
