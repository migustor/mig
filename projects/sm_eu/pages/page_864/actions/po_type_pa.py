# projects/sm_eu/pages/page_864/actions/po_type_pa.py
"""
 ACC PO Type: PA  
  ▸ if current VAT == 0   → 10 → 0  (two changes)
  ▸ if current VAT != 0  → 0  → 10 → original (three changes)

 ACC PO Type: Company (popup on every change)
  ▸ same sequences as above.

 After *each* change:
     1. set new value through JS
     2. click `<body>` to blur & trigger save
     3. **refetch** the `<input>` (DOM may be rerendered!)
     4. wait 1.5 s → verify value, otherwise fail immediately.

 This prevents duplicated log lines and the stale‑element errors you saw –
 we never reuse a WebElement across iterations.
"""
from __future__ import annotations

import logging, time
from typing import Set, List

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from common.pages.page_864.page_info import get_page_864_url
from common.utils.error_handling import jenkins_aware

# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------
WAIT_AFTER_SAVE = 1.5  # seconds – empirically enough for Sage to persist


def _find_input(driver):
    """Return a *fresh* WebElement of the VAT field inside credit‑note table."""
    return driver.find_element(
        By.CSS_SELECTOR,
        "#credit_note_document_tbl input[name='credit_note_vat_amount']",
    )


def _js_set(driver, element, value: str):
    """Set value via JS & fire events."""
    driver.execute_script(
        """
        const el = arguments[0];
        el.value = arguments[1];
        ['input','change'].forEach(e => el.dispatchEvent(new Event(e,{bubbles:true})));
        """,
        element,
        value,
    )


def _blur_save(driver):
    driver.find_element(By.TAG_NAME, "body").click()
    time.sleep(WAIT_AFTER_SAVE)


def _wait_value(driver, expected: Set[str], timeout=10):
    """Wait until the field shows *one of* expected strings."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: _find_input(d).get_attribute("value").strip() in expected
        )
        return True
    except (TimeoutException, StaleElementReferenceException):
        return False


def _as_set(v: str):
    return {v, f"{float(v):.2f}"} if v.replace(".", "", 1).isdigit() else {v}


def _run_sequence(driver, log, sequence: List[str], popup: bool = False):
    """Generic runner for PA/Company. `popup=True` – confirm YES every change."""
    for target in sequence:
        # always refetch fresh element *before* we set it – avoids stale refs
        field = _find_input(driver)

        try:
            _js_set(driver, field, target)
        except StaleElementReferenceException:
            # one automatic retry with a fresh element
            field = _find_input(driver)
            _js_set(driver, field, target)

        _blur_save(driver)

        if popup:
            _confirm_company_popup(driver, log)

        if not _wait_value(driver, _as_set(target)):
            raise RuntimeError(f"Не удалось установить {target}")
        log.info(f"VAT set to {target} (confirmed)")


# ---------------------------------------------------------------------------
# PA action – без всплывашек
# ---------------------------------------------------------------------------
@jenkins_aware()
def po_type_pa(driver, project_name: str, document_id: str):
    log = logging.getLogger(" - TYPE PA - ")
    driver.get(get_page_864_url(project_name, document_id))
    time.sleep(3)

    initial = _find_input(driver).get_attribute("value").strip()
    log.info(f"Initial VAT: {initial}")

    seq = ["10.00", "0.00"] if initial in {"0", "0.00"} else ["0.00", "10.00", initial]

    try:
        _run_sequence(driver, log, seq, popup=False)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Company action – требует подтверждения
# ---------------------------------------------------------------------------
POPUP_TEXT = "VAT"  # substring present in modal dialog


def _confirm_company_popup(driver, log):
    try:
        modal = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".ui-dialog-content"))
        )
        if POPUP_TEXT.lower() in modal.text.lower():
            modal.find_element(By.XPATH, "//button[text()='YES']").click()
            log.info("YES clicked")
    except TimeoutException:
        log.warning("Popup did not appear – продолжаем")


@jenkins_aware()
def po_type_company(driver, project_name: str, document_id: str):
    log = logging.getLogger("test")
    driver.get(get_page_864_url(project_name, document_id))
    time.sleep(3)

    initial = _find_input(driver).get_attribute("value").strip()
    log.info(f"Initial VAT: {initial}")

    seq = ["10.00", "0.00"] if initial in {"0", "0.00"} else ["0.00", "10.00", initial]

    try:
        _run_sequence(driver, log, seq, popup=True)
        log.info("Original VAT restored")
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
