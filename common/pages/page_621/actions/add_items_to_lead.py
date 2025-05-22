import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Import Jenkins‑aware decorator for robust error handling
from common.utils.error_handling import jenkins_aware

# ---------------------------------------------------------------------------
# add_items_to_lead
# ---------------------------------------------------------------------------
# This action adds an item to an existing lead and creates the corresponding
# Purchase Order (PO). All waits are explicit (WebDriverWait) with short
# additional `time.sleep()` pauses to ensure that dynamic UI elements finish
# loading before the next step executes.
# ---------------------------------------------------------------------------

@jenkins_aware()
def add_items_to_lead(
    driver,
    ean: str = "4977766525992",
    timeouts: dict | None = None,
):
    """Add an item to a lead and create the PO.

    Args:
        driver: Selenium WebDriver instance.
        ean: EAN/UPC code to search for.
        timeouts: Optional dictionary with custom timeouts. Supported keys:
            - "action": seconds to wait for elements (default 15).
    Returns:
        dict: {
            "success": bool,
            "error": str | None
        }
    """
    logger = logging.getLogger("test")
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)

    try:
        wait = WebDriverWait(driver, action_timeout)

        # Step 1: Click "Add Items" button
        logger.info("Clicking 'Add Items' button…")
        add_items_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='lead_add_item_show']/h4"))
        )
        add_items_btn.click()
        time.sleep(2)  # Allow modal/content to load

        # Step 2: Enter EAN / UPC value
        logger.info("Entering EAN/UPC value…")
        ean_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='ean_upc']"))
        )
        ean_input.clear()
        ean_input.send_keys(ean)
        time.sleep(1)

        # Step 3: Click "Search" button
        logger.info("Clicking 'Search' button…")
        search_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='search_items_module_form']/div/div[3]/div/div[2]/button[2]"))
        )
        search_btn.click()
        time.sleep(2)  # Wait for search results to appear

        # Step 4: Click "Add" button for the first search result
        logger.info("Adding the first search result to the lead…")
        add_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='add_form_899']/div[1]/div/div[4]/button"))
        )
        add_btn.click()
        time.sleep(2)

        # Step 5: Click "Create PO" button
        logger.info("Creating Purchase Order (PO)…")
        create_po_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='create_po']"))
        )
        create_po_btn.click()
        time.sleep(2)

        # Step 6: Confirm PO creation in the dialog
        logger.info("Confirming PO creation…")
        confirm_po_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='modal_dialog']/div/div/div[3]/button[2]"))
        )
        confirm_po_btn.click()
        time.sleep(2)

        logger.info("Item successfully added and PO created.")
        return {"success": True, "error": None}

    except Exception as exc:
        error_msg = f"Error while adding item to lead: {exc}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
