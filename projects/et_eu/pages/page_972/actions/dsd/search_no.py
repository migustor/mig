# /common/pages/page_972/actions/search_no.py
"""
Action file for searching presale with 'Has Items Accepted for Stock' = NO on page 972
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
def search_no(driver, project_name, timeouts=None):
    """
    Searches presale with 'Has Items Accepted for Stock' set to NO and verifies results.

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
        # Navigate to page 972
        page_972_url = get_page_972_url(project_name)
        if not page_972_url:
            return {"success": False, "error": f"Could not build page 972 URL for {project_name}"}
        driver.get(page_972_url)
        WebDriverWait(driver, action_timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")

        # Ожидаем, пока появится радио-кнопка "No"
        wait = WebDriverWait(driver, action_timeout)
        radio_no = wait.until(EC.presence_of_element_located((By.ID, "has_items_accepted_for_stock_no")))

        # Кликаем по радио-кнопке "No" через JavaScript
        driver.execute_script("arguments[0].click();", radio_no)

        # Ожидаем кнопку поиска и нажимаем её
        submit_btn = wait.until(EC.element_to_be_clickable(Page972WithoutLeadLocators.SEARCH_BUTTON))
        submit_btn.click()

        # Wait for search results to appear
        WebDriverWait(driver, action_timeout).until(EC.presence_of_element_located((By.CLASS_NAME, "result-row")))

        # Verify and extract presale ID
        presale_id = driver.find_element(By.CLASS_NAME, "presale-id").text
        return {"success": True, "presale_id": presale_id}

    except (TimeoutException, NoSuchElementException) as e:
        return {"success": False, "error": str(e)}

    except UnexpectedAlertPresentException as e:
        driver.switch_to.alert.accept()
        return {"success": False, "error": "Unexpected alert detected"}

    except Exception as e:
        return {"success": False, "error": str(e)}
