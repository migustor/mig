# ───────────── insert_item_details.py ────────────────
import logging
import textwrap

from selenium.webdriver.common.by      import By
from selenium.webdriver.support.ui     import WebDriverWait
from selenium.webdriver.support        import expected_conditions as EC

from common.utils.timeouts             import smart_sleep
from common.utils.error_handling       import jenkins_aware

_JS_SELECTS = textwrap.dedent("""\
(function () {
  const cond = document.getElementById('box_condition_select');
  if(cond){cond.value='A'; cond.dispatchEvent(new Event('change',{bubbles:true}));}

  const coo = document.getElementById('country_of_origin_select');
  if(coo){coo.value='262'; coo.dispatchEvent(new Event('change',{bubbles:true}));}
})();""")

@jenkins_aware()
def insert_item_details(driver, tout: int = 20) -> dict:
    """
    Fill mandatory details after receiving product.
    """
    log  = logging.getLogger("test")
    wait = WebDriverWait(driver, tout)

    try:
        # Universal qty = 1
        uni = wait.until(EC.element_to_be_clickable((By.ID, "universal")))
        uni.clear(); uni.send_keys("1")
        smart_sleep("short", "universal qty")

        # Set condition & COO via JS
        driver.execute_script(_JS_SELECTS)
        smart_sleep("short", "condition / COO")

        # Quantity
        qty = wait.until(EC.element_to_be_clickable((By.ID, "box_qty")))
        qty.clear(); qty.send_keys("1")
        smart_sleep("short", "qty=1")

        # Next item
        wait.until(EC.element_to_be_clickable((By.ID, "nextItem"))).click()
        smart_sleep("medium", "next item")

        # Review → notes
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="item_search_form"]/p[2]/input[2]'))).click()
        smart_sleep("short", "review click")

        notes = wait.until(EC.element_to_be_clickable((By.NAME, "recvg_notes")))
        notes.clear(); notes.send_keys("testtesttesttesttest")

        # Confirm
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="review_form"]/input[3]'))).click()
        smart_sleep("medium", "details confirmed")

        return {"success": True}
    except Exception as exc:
        log.error("insert_item_details ❌ %s", exc)
        return {"success": False, "error": str(exc)}
