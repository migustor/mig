"""
Acc PO Type: Company – изменение VAT только в credit_note_document_tbl
(обработка поп‑апа YES).

Алгоритм:
 1. remembered = текущее значение.
 2. if remembered != 0 → ставим 0 (YES) → reload.
 3. ставим 10 (YES) → reload.
 4. возвращаем remembered (YES) → reload.
"""

import logging, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from common.utils.error_handling import jenkins_aware
from common.pages.page_864.page_info import get_page_864_url


@jenkins_aware()
def po_type_company(driver, project, doc_id):
    log = logging.getLogger(" - TYPE COMPANY - ")
    driver.get(get_page_864_url(project, doc_id)); time.sleep(3)

    def inp():
        return driver.find_element(
            By.CSS_SELECTOR,
            "#credit_note_document_tbl input[name='credit_note_vat_amount']",
        )

    vat_id = inp().get_attribute("id")
    remembered = inp().get_attribute("value").strip()
    log.info(f"Initial VAT: {remembered}")

    JS_SET = """
      const e=arguments[0],v=arguments[1];
      e.value=v;
      ['input','change','blur'].forEach(ev=>e.dispatchEvent(new Event(ev,{bubbles:true})));
      if(typeof update_document_detail==='function'){
        const id=e.id.match(/\\d+$/); if(id) update_document_detail('credit_note','vat_amount',id[0]);
      }"""

    popup_flag = False  # будет True, если хотя бы раз нажали YES

    def click_yes():
        nonlocal popup_flag
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[translate(normalize-space(.),'yes','YES')='YES']")
                )
            ).click()
            popup_flag = True
            log.info("YES clicked")
        except TimeoutException:
            pass  # поп‑ап не всегда появляется (например, при 0→10 в DE‑зоне)

    def set_and_confirm(value, expected):
        for _ in range(3):
            try:
                driver.execute_script(JS_SET, driver.find_element(By.ID, vat_id), value)
                driver.find_element(By.TAG_NAME, "body").click()
                click_yes()
                WebDriverWait(driver, 2).until(
                    lambda d: d.find_element(By.ID, vat_id)
                    .get_attribute("value")
                    .strip()
                    in expected
                )
                return True
            except (StaleElementReferenceException, TimeoutException):
                time.sleep(0.6)
        return False

    # ---------- ставим 0 только если нужно
    if remembered not in {"0", "0.00"}:
        if not set_and_confirm("0.00", {"0", "0.00"}):
            return {"success": False, "error": "Cannot set VAT to 0"}
        driver.refresh()
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, vat_id).get_attribute("value").strip()
            in {"0", "0.00"}
        )
        log.info("VAT set to 0 (confirmed)")

    # ---------- 0 → 10
    if not set_and_confirm("10.00", {"10", "10.00"}):
        return {"success": False, "error": "Cannot set VAT to 10"}
    driver.refresh()
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, vat_id).get_attribute("value").strip()
        in {"10", "10.00"}
    )
    log.info("VAT set to 10 (confirmed)")

    # ---------- 10 → исходное
    if not set_and_confirm(remembered, {remembered}):
        return {"success": False, "error": "Cannot restore VAT"}
    driver.refresh()
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, vat_id).get_attribute("value").strip()
        == remembered
    )
    log.info("Original VAT restored")

    return {
        "success": True,
        "original_vat": remembered,
        "popup_appeared": popup_flag,
    }
