import logging
import re
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.pages.page_972.page_info import get_presale_creation_url
from common.pages.page_972.locators import Page972WithLeadLocators
from common.utils.error_handling import jenkins_aware

# Dictionary to store presale IDs for later use
PRESALE_IDS = {}

@jenkins_aware()
def create_presale(driver, project_name, lead_id, timeouts=None):
    """
    Creates a presale for a given lead_id, then navigates to page 442.

    :param driver: Selenium WebDriver instance.
    :param project_name: Project code (e.g. "sm_eu").
    :param lead_id: The lead ID previously captured from page 634.
    :param timeouts: Optional dict of timeouts, e.g. {"action": 15}.
    :return: dict with "success" (bool), optional "error" (str), and "presale_id" (int).
    """
    logger = logging.getLogger("test")
    logger.info(f"Starting create_presale action for lead_id={lead_id} on project={project_name}")

    action_timeout = timeouts.get("action", 15) if timeouts else 15

    try:
        # 1) Generate the URL and navigate
        page_972_url = get_presale_creation_url(project_name, lead_id=lead_id)
        if not page_972_url:
            error_msg = f"Could not build page_972_url for project '{project_name}'"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        logger.info(f"Navigating to: {page_972_url}")
        driver.get(page_972_url)

        wait = WebDriverWait(driver, action_timeout)
        wait.until(
            EC.presence_of_element_located(Page972WithLeadLocators.PLACE_PRESALE_EFFORT_BUTTON)
        )

        # Execute JS code to fill fields
        create_presale_script = r"""
        (function() {
          const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
          let randomName = '';
          for (let i = 0; i < 10; i++) {
            randomName += chars.charAt(Math.floor(Math.random() * chars.length));
          }

          const nameField = document.querySelector('input[name="pe_name"]');
          if (nameField) {
            nameField.value = randomName;
          }

          const yesRadio = document.getElementById('activate_newsletter_yes');
          if (yesRadio) {
            yesRadio.checked = true;
          }

          const checkbox = document.getElementById('has_items_accepted_for_stock');
          if (checkbox && !checkbox.checked) {
            checkbox.click();
          }
        })();
        """
        logger.info("Executing JavaScript to fill presale form fields...")
        driver.execute_script(create_presale_script)

        # Click 'Place Presale Effort & Notify Buying managers'
        logger.info("Clicking 'Place Presale Effort & Notify Buying managers' button...")
        time.sleep(1)
        wait.until(
            EC.element_to_be_clickable(Page972WithLeadLocators.PLACE_PRESALE_EFFORT_BUTTON)
        ).click()

        # Approve the presale
        logger.info("Clicking 'Approve Pre-sale Effort & Notify Sellers' button...")
        time.sleep(1)
        wait.until(
            EC.element_to_be_clickable(Page972WithLeadLocators.APPROVE_PRESALE_EFFORT_BUTTON)
        ).click()

        # Confirm approval
        logger.info("Confirming 'Approve' popup...")
        time.sleep(1)
        wait.until(
            EC.element_to_be_clickable(Page972WithLeadLocators.CONFIRM_APPROVE_BUTTON)
        ).click()

        # Extract presale ID from the page
        presale_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h4.status b.status__text"))
        )
        presale_text = presale_element.text

        match = re.search(r'ID:\s*(\d+)', presale_text)
        if match:
            presale_id = int(match.group(1))
            PRESALE_IDS[project_name] = presale_id
            logger.info(f"Presale created with ID: {presale_id}")
            return {"success": True, "presale_id": presale_id}
        else:
            error_msg = "Presale ID not found in the page content"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    except (NoSuchElementException, TimeoutException) as e:
        error_msg = f"Element not found or timed out during create_presale: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except Exception as e:
        error_msg = f"Unexpected error in create_presale: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
