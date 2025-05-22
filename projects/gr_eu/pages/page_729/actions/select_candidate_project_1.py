# common/pages/page_729/actions/select_candidate_project_1.py
import logging
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from projects.gr_eu.pages.page_729.locators import CANDIDATE_PROJECTS_1_SELECT
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

def select_candidate_project_1(driver, project_value="5", timeout=15):
    """
    В выпадающем списке (id="candidate_projects_1") выбирает нужный value,
    напр. "5" (Agava).
    """
    try:
        wait = WebDriverWait(driver, timeout)
        select_el = wait.until(EC.presence_of_element_located(CANDIDATE_PROJECTS_1_SELECT))
        Select(select_el).select_by_value(project_value)
        logger.info(f"Selected project value={project_value} in <select id='candidate_projects_1'>")
        return {"success": True, "error": None}
    except (TimeoutException, NoSuchElementException) as e:
        err = f"Failed to select candidate_projects_1='{project_value}': {str(e)}"
        logger.error(err)
        return {"success": False, "error": err}
    except Exception as ex:
        err = f"Unexpected error in select_candidate_project_1: {str(ex)}"
        logger.error(err)
        return {"success": False, "error": err}
