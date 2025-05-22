# ───────────────── truck_arrival_package.py ──────────────────
import logging
import textwrap

from selenium.webdriver.common.by          import By
from selenium.webdriver.support.ui         import WebDriverWait
from selenium.webdriver.support            import expected_conditions as EC

from common.utils.timeouts                 import smart_sleep
from common.utils.error_handling           import jenkins_aware
from common.pages.page_884.page_info       import get_page_884_url   # already существует

_JS_PACKAGE = textwrap.dedent("""\
(function () {
  /* Fill dimensions & carrier ▼ */
  ['shipping_package_length','shipping_package_width',
   'shipping_package_height','shipping_package_weight']
   .forEach(id=>{
      const el=document.querySelector(`input[name="${id}"]`);
      if(el){
         el.value=10;
         el.dispatchEvent(new Event('input',{bubbles:true}));
         el.dispatchEvent(new Event('change',{bubbles:true}));
      }
   });
  const sel=document.querySelector('select[name="shipping_package_carrier_id"]');
  if(sel){
     sel.value='54';
     sel.dispatchEvent(new Event('change',{bubbles:true}));
  }
})();""")

@jenkins_aware()
def truck_arrival_package(driver, project: str, po_id: str, tout: int = 20) -> dict:
    """
    Open page 884 for given PO, add shipping package and follow the
    redirect to Warehouse Receive page.
    """
    log  = logging.getLogger("test")
    wait = WebDriverWait(driver, tout)

    try:
        url = get_page_884_url(project)
        log.info("[884] Open %s", url)
        driver.get(url)
        smart_sleep("medium", "page 884 load")

        # PO input
        po_in = wait.until(EC.element_to_be_clickable((By.ID, "po_id")))
        po_in.clear(); po_in.send_keys(po_id)
        smart_sleep("short", "PO id typed")

        # First “Register”
        wait.until(EC.element_to_be_clickable((By.ID, "build_report"))).click()
        smart_sleep("medium", "1st Register")

        # Add package
        wait.until(EC.element_to_be_clickable(
            (By.ID, "add_shipping_package_button"))).click()
        driver.execute_script(_JS_PACKAGE)
        smart_sleep("short", "package JS executed")

        # Second “Register”
        wait.until(EC.element_to_be_clickable((By.ID, "build_report"))).click()
        smart_sleep("medium", "2nd Register")

        # Link to warehouse receive
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="layoutContainer"]/div[4]/span/b[2]/a'))).click()
        smart_sleep("long", "redirect to Warehouse Receive")

        return {"success": True}
    except Exception as exc:
        log.error("truck_arrival_package ❌ %s", exc)
        return {"success": False, "error": str(exc)}
