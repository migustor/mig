import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Импортируем информацию о странице
from common.config.base_urls import PROJECT_BASE_URLS
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def create_basic_lead(driver, project_name: str, company_id: int, timeouts=None):
    """
    Создает лид на странице 621, нажимает "Create",
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
        # Получаем базовый URL проекта
        base_url = PROJECT_BASE_URLS.get(project_name, "")
        if not base_url:
            error_msg = f"Unknown project: {project_name}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "lead_id": None}
        
        # Формируем URL для создания лида
        lead_url = f"{base_url}index.cfm?page_id=621&company_id={company_id}"
        driver.get(lead_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='use_in_presale' and @value='1']")))
        time.sleep(2)
        
        # Нажимаем кнопку "Create"
        create_button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'btn btn-primary')]")
        create_button.click()
        logger.info("Clicked on 'Create' button.")
        
        # Ожидаем появления ID лида
        time.sleep(3)
        lead_id_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@id='title_page_name']"))
        )
        lead_id_text = lead_id_element.text
        lead_id = lead_id_text.split("Lead ID: ")[-1].strip()
        
        logger.info(f"Lead created successfully with ID: {lead_id}")
        return {"success": True, "error": None, "lead_id": lead_id}
        
    except Exception as e:
        error_msg = f"Error while creating lead on page 621: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "lead_id": None}
