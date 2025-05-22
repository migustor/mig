# common/pages/page_730/actions/select_date_type.py
import logging
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from projects.gr_eu.pages.page_730.locators import DATE_TYPE_SELECT
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

def select_date_type(driver, value="dismissal_resignation", timeout=15):
    """
    На странице 730 выбирает в select id="date_type" нужное value, 
    напр. "dismissal_resignation".
    """
    try:
        wait = WebDriverWait(driver, timeout)
        select_el = wait.until(EC.presence_of_element_located(DATE_TYPE_SELECT))
        Select(select_el).select_by_value(value)
        logger.info(f"Selected date_type={value} in <select id='date_type'>")
        return {"success": True, "error": None}
    except (TimeoutException, NoSuchElementException) as e:
        err = f"Failed to select date_type='{value}': {str(e)}"
        logger.error(err)
        return {"success": False, "error": err}
    except Exception as ex:
        err = f"Unexpected error in select_date_type: {str(ex)}"
        logger.error(err)
        return {"success": False, "error": err}
