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
def create_lead_621(driver, project_name: str, company_id: int, timeouts=None):
    """
    Создает лид на странице 621, выбирает радио-кнопку "Should be used", нажимает "Create",
    ожидает создания лида и возвращает его ID.
    
    Args:
        driver: Selenium WebDriver instance
        project_name: Код проекта (например, "sm_eu")
        company_id: ID компании (например, 500000)
        timeouts: (Опционально) Словарь с таймаутами
    
    Returns:
        dict: {
          "success": bool,
          "error": str или None,
          "lead_id": str или None
        }
    """
    logger = logging.getLogger("test")
    logger.info(f"Opening page 621 for project: {project_name}, company_id: {company_id}")
    
    try:
        # Получаем URL страницы с помощью функции из page_info.py
        lead_url = get_page_621_url(project_name, company_id)
        if not lead_url:
            error_msg = f"Unknown project: {project_name}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "lead_id": None}
        
        # Переходим на страницу создания лида
        driver.get(lead_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(Page621Locators.RADIO_BUTTON_SHOULD_BE_USED))
        time.sleep(2)
        
        # Выбираем радио-кнопку "Should be used" через JS
        script = """
        document.getElementById('use_in_presale_1').click();
        """
        driver.execute_script(script)
        logger.info("Clicked on 'Should be used' radio button via JS.")
        time.sleep(1)
        
        # Нажимаем кнопку "Create"
        create_button = driver.find_element(*Page621Locators.CREATE_BUTTON)
        create_button.click()
        logger.info("Clicked on 'Create' button.")
        
        # Ожидаем появления ID лида
        time.sleep(3)
        lead_id_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(Page621Locators.LEAD_ID_HEADER)
        )
        lead_id_text = lead_id_element.text
        lead_id = lead_id_text.split("Lead ID: ")[-1].strip()
        
        logger.info(f"Lead created successfully with ID: {lead_id}")
        return {"success": True, "error": None, "lead_id": lead_id}
        
    except Exception as e:
        error_msg = f"Error while creating lead on page 621: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "lead_id": None}