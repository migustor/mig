# common/pages/page_730/actions/select_project.py
import logging
from selenium.common.exceptions import JavascriptException
from projects.gr_eu.pages.page_730.locators import CANDIDATE_PROJECT

logger = logging.getLogger(__name__)

def select_project_js(driver, project_value):
    """
    Снимаем все галочки в #candidate_project, затем отмечаем нужный project_value,
    обновляем кнопку (Bootstrap Multiselect).
    """
    try:
        # Если локатор нужен для клика по самому селекту - импортируем, но обычно JS достаточно.
        driver.execute_script("$('#candidate_project').multiselect('deselectAll', false);")
        driver.execute_script(f"$('#candidate_project').multiselect('select', '{project_value}');")
        driver.execute_script("$('#candidate_project').multiselect('updateButtonText');")
        logger.info(f"Selected project_value='{project_value}' via JS multiselect")
    except JavascriptException as e:
        logger.error(f"JS error for select_project_js: {str(e)}")
    except Exception as ex:
        logger.error(f"Unexpected error in select_project_js: {str(ex)}")
