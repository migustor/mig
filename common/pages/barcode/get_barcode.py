# ───────────── get_barcode.py ─────────────
"""Fetch a fresh barcode from QA-tools.

Opens the generator page in a **new tab**, selects the required project
(determined by *project_value*), waits for a non-empty result under
#barcodes and returns it.  Comments/logs are English-only.
"""

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://dev.office.grafit.md/sage/test/qa_tools/rand_barcode.cfm"


def get_barcode(driver, project_value: str, tout: int = 10) -> str:
    """
    Parameters
    ----------
    driver : selenium.webdriver
        Active WebDriver instance.
    project_value : str
        *value* attribute in <select id="gr_projects"> (e.g. ``\"SAGE\"``).
    tout : int, optional
        Explicit-wait timeout (seconds, default **10**).

    Returns
    -------
    str
        Freshly generated barcode string.
    """
    log = logging.getLogger("barcode")
    original_window = driver.current_window_handle

    # open a new blank tab & switch to it
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])

    driver.get(URL)
    log.info("Opened barcode page (project = %s)", project_value)

    # select the project via JS and trigger onchange
    js = (
        "const dd=document.getElementById('gr_projects');"
        "if(dd){dd.value=arguments[0];"
        "dd.dispatchEvent(new Event('change',{bubbles:true}));}"
    )
    driver.execute_script(js, project_value)

    # wait until backend returns something under #barcodes
    wait = WebDriverWait(driver, tout)
    wait.until(lambda d: d.find_element(By.ID, "barcodes").text.strip() != "")
    barcode = driver.find_element(By.ID, "barcodes").text.strip()
    log.info("Barcode fetched: %s", barcode)

    # close the tab and return to original context
    driver.close()
    driver.switch_to.window(original_window)
    return barcode
