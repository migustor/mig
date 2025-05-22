import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

def click_create_sales_order(driver, timeout=15):
    """
    На странице 888 нажимаем кнопку «Create Sales Order»
    <button id="surplus_order_btn" ...>Create Sales Order</button>
    """
    try:
        wait = WebDriverWait(driver, timeout)
        create_btn = wait.until(EC.element_to_be_clickable((
            By.ID,
            "surplus_order_btn"
        )))
        create_btn.click()
        time.sleep(2)
        logger.info("Clicked 'Create Sales Order' button on page 888.")
        return {"success": True, "error": None}

    except TimeoutException as te:
        err = f"Timeout: 'Create Sales Order' not clickable => {str(te)}"
        logger.error(err)
        return {"success": False, "error": err}
    except Exception as ex:
        err = f"Error clicking 'Create Sales Order': {str(ex)}"
        logger.error(err)
        return {"success": False, "error": err}
