# /common/pages/page_972/actions/search_yes.py
"""
Action file for searching presale with 'Has Items Accepted for Stock' = YES on page 972
"""
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
from common.pages.page_972.page_info import get_page_972_url
from common.pages.page_972.locators import Page972WithoutLeadLocators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def search_yes(driver, project_name, timeouts=None):
    """
    Searches presale with 'Has Items Accepted for Stock' set to YES and verifies results.

    Args:
        driver: Selenium WebDriver instance.
        project_name: Project name (e.g., "sm_eu").
        timeouts: Optional dict with custom timeouts.

    Returns:
        dict: {"success": bool, "error": str or None}
    """
    logger = logging.getLogger("test")
    action_timeout = (timeouts or {}).get("action", 30)

    try:
        # Получаем URL страницы поиска пресейлов
        page_972_url = get_page_972_url(project_name)
        if not page_972_url:
            error_msg = f"Could not build page 972 URL for project '{project_name}'"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        # 🔥 **ФОРСИРУЕМ ПЕРЕХОД через JavaScript, чтобы избежать блокировок**
        logger.info(f"FORCING navigation to page 972 via JavaScript: {page_972_url}")
        driver.execute_script(f"window.location.href = '{page_972_url}';")
        
        # Ожидание полной загрузки страницы
        WebDriverWait(driver, action_timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        logger.info("Page 972 (presale search) loaded successfully.")

        # Ожидаем, пока появится радио-кнопка "Yes"
        wait = WebDriverWait(driver, action_timeout)
        radio_yes = wait.until(EC.presence_of_element_located((By.ID, "has_items_accepted_for_stock_yes")))

        # Кликаем по радио-кнопке "Yes" через JavaScript
        driver.execute_script("arguments[0].click();", radio_yes)

        # Ожидаем кнопку поиска и нажимаем её
        submit_btn = wait.until(EC.element_to_be_clickable(Page972WithoutLeadLocators.SEARCH_BUTTON))
        submit_btn.click()
        logger.info("Search button clicked.")

        # Ждём появления результатов
        WebDriverWait(driver, action_timeout).until(EC.presence_of_element_located((By.CLASS_NAME, "result-row")))
        logger.info("Search results loaded.")

        # Проверяем и получаем ID пресейла
        presale_id = driver.find_element(By.CLASS_NAME, "presale-id").text
        logger.info(f"Presale found: {presale_id}")

        return {"success": True, "presale_id": presale_id}

    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"Timeout or element not found: {str(e)}")
        return {"success": False, "error": str(e)}

    except UnexpectedAlertPresentException as e:
        driver.switch_to.alert.accept()
        logger.warning("Unexpected alert detected and accepted.")
        return {"success": False, "error": "Unexpected alert detected"}

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"success": False, "error": str(e)}
