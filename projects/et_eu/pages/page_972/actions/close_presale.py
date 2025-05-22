import logging
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from common.pages.page_972.page_info import get_created_presale_url
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def close_presale(driver, project_name, presale_id, timeouts=None):
    """
    Closes an existing presale by navigating to its edit page and clicking the close buttons.
    """
    logger = logging.getLogger("test")
    logger.info(f"Starting close_presale action for presale_id={presale_id} on project={project_name}")

    action_timeout = timeouts.get("action", 15) if timeouts else 15

    try:
        # Получаем URL страницы пресейла
        page_972_url = get_created_presale_url(project_name, presale_id)
        if not page_972_url:
            error_msg = f"Could not build page_972_url for project '{project_name}'"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        logger.info(f"Navigating to: {page_972_url}")
        driver.get(page_972_url)

        wait = WebDriverWait(driver, action_timeout)

        # Кликаем на "Close Pre-sale Effort"
        driver.find_element(By.XPATH, "//button[contains(text(), 'Close Pre-sale Effort')]").click()

        # Ждем появления попапа
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Yes!')]")
        ))

        # Кликаем на "Yes!"
        driver.find_element(By.XPATH, "//button[contains(text(), 'Yes!')]").click()

        # Ожидание завершения процесса
        time.sleep(5)

        # Проверяем, что статус изменился на "Couldn't Close a Deal. Expired or Canceled"
        logger.info(f"Checking presale status on: {page_972_url}")
        driver.get(page_972_url)
        time.sleep(2)  # Даем странице прогрузиться

        try:
            status_text = driver.find_element(By.XPATH, "//*[contains(text(), \"Couldn't Close a Deal. Expired or Canceled\")]")
            if status_text:
                logger.info("Presale is successfully closed (status: Couldn't Close a Deal. Expired or Canceled).")
                return {"success": True, "error": None}
        except NoSuchElementException:
            logger.error("Presale was not closed properly.")
            return {"success": False, "error": "Presale status incorrect"}

    except (TimeoutException, NoSuchElementException) as e:
        error_msg = f"Element not found or timed out during close_presale: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except Exception as e:
        error_msg = f"Unexpected error in close_presale: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
