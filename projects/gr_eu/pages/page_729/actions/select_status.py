# common/pages/page_729/actions/select_status.py
import logging
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from projects.gr_eu.pages.page_729.locators import STATUS_ID_SELECT
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

def select_status(driver, status_value="413", timeout=15):
    """
    В выпадающем списке (id="status_id") выбирает нужный value, напр. "413" (Dismissal).
    """
    try:
        wait = WebDriverWait(driver, timeout)
        select_el = wait.until(EC.presence_of_element_located(STATUS_ID_SELECT))
        Select(select_el).select_by_value(status_value)
        logger.info(f"Selected status value={status_value} in <select id='status_id'>")
        return {"success": True, "error": None}
    except (TimeoutException, NoSuchElementException) as e:
        err = f"Failed to select status_id='{status_value}': {str(e)}"
        logger.error(err)
        return {"success": False, "error": err}
    except Exception as ex:
        err = f"Unexpected error in select_status: {str(ex)}"
        logger.error(err)
        return {"success": False, "error": err}
