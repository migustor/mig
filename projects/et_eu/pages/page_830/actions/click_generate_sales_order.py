import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

def click_generate_sales_order(driver, timeout=15):
    """
    На странице 830 кликаем по ссылке «Generate Sales Order».
    Предполагается, что локатор – через XPATH или что угодно:
    <a href="...page_id=888..." target="_blank">Generate Sales Order</a>
    """
    try:
        wait = WebDriverWait(driver, timeout)
        # Пример локатора:
        generate_so_link = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            '//a[contains(@href,"page_id=888") and contains(text(),"Generate Sales Order")]'
        )))
        generate_so_link.click()
        time.sleep(1)
        logger.info("Clicked 'Generate Sales Order' link.")
        return {"success": True, "error": None}

    except TimeoutException as te:
        err = f"Timeout: Could not click Generate Sales Order => {str(te)}"
        logger.error(err)
        return {"success": False, "error": err}
    except Exception as ex:
        err = f"Error in click_generate_sales_order: {str(ex)}"
        logger.error(err)
        return {"success": False, "error": err}
