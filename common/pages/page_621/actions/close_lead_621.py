import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Импортируем функцию для получения URL страницы
from common.pages.page_621.page_info import get_page_621_url
# Импортируем локаторы из специального файла
from common.pages.page_621.locators import Page621Locators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def close_lead_621(driver, project_name: str, lead_id: int, company_id=None, timeouts=None):
    """
    Закрывает лид, изменяя его статус на "Couldn't Close a Deal".
    
    Args:
        driver: Selenium WebDriver instance
        project_name: Код проекта (например, "sm_eu")
        lead_id: ID лида, который нужно закрыть
        company_id: ID компании (если известен)
        timeouts: (Опционально) Словарь с таймаутами
    
    Returns:
        dict: {
          "success": bool,
          "error": str или None
        }
    """
    logger = logging.getLogger("test")
    logger.info(f"Closing lead {lead_id} for project: {project_name}")
    
    try:
        # If company_id is provided, use it to construct the URL
        if company_id:
            lead_url = f"{get_page_621_url(project_name, company_id)}&lead_id={lead_id}&phase=edit"
        else:
            # Try to construct URL without company_id
            lead_url = f"{get_page_621_url(project_name, None)}&lead_id={lead_id}&phase=edit"
            
        logger.info(f"Navigating to lead URL: {lead_url}")
        
        if not lead_url:
            error_msg = f"Unknown project: {project_name}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        driver.get(lead_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(Page621Locators.LEAD_STATUS_DROPDOWN))
        time.sleep(2)
        
        # Изменяем статус лида на "Couldn't Close a Deal"
        script = """
        document.getElementById('lead_status_id').value = '24';
        var event = new Event('change', { bubbles: true });
        document.getElementById('lead_status_id').dispatchEvent(event);
        """
        driver.execute_script(script)
        logger.info("Lead status changed to 'Couldn't Close a Deal'")
        time.sleep(1)
        
        # Нажимаем кнопку "Save Changes"
        save_button = driver.find_element(*Page621Locators.SAVE_CHANGES_BUTTON)
        save_button.click()
        logger.info("Clicked on 'Save Changes' button.")
        
        # Ожидаем появления подтверждающего сообщения
        success_alert = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(Page621Locators.SUCCESS_ALERT)
        )
        if success_alert:
            logger.info("Lead closed successfully.")
            return {"success": True, "error": None}
        
    except Exception as e:
        error_msg = f"Error while closing lead {lead_id}: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}