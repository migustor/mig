import logging
import time

from projects.gr_eu.pages.page_907.actions.input_order_id import input_order_id
from projects.gr_eu.pages.page_907.actions.build_report import build_report
from projects.gr_eu.pages.page_907.locators import Page907Locators

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def email_check_workflow(driver, order_id, timeouts=None):
    """
    1) Input the given order_id
    2) Build report (to isolate that order)
    3) Extract tracking_number and company_name
    Returns them in the result dict
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info(f"Starting email_check_workflow for order ID: {order_id}")

    result = {
        "success": False,
        "error": None,
        "order_id": order_id,
        "tracking_number": None,
        "company_name": None
    }

    try:
        # Step: input order_id
        input_res = input_order_id(driver, order_id, timeouts)
        if not input_res["success"]:
            result["error"] = f"Failed input_order_id: {input_res['error']}"
            return result
        time.sleep(2)

        # Step: build report for that single order
        build_res = build_report(driver, timeouts)
        if not build_res["success"]:
            result["error"] = f"Failed build_report: {build_res['error']}"
            return result
        time.sleep(3)

        wait_timeout = timeouts.get("wait", 20)
        
        # Wait for spinner to disappear (if any)
        spinner_locator = (By.CSS_SELECTOR, 'i.fa-spinner#rotation')
        try:
            WebDriverWait(driver, wait_timeout).until_not(
                EC.visibility_of_element_located(spinner_locator)
            )
        except:
            logger.info("Spinner not found or already gone")

        time.sleep(2)  # buffer

        # Extract tracking number
        try:
            tracking_element = WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located(Page907Locators.TRACKING_NUMBER)
            )
            tracking_number = tracking_element.text.strip()
            result["tracking_number"] = tracking_number
            logger.info(f"Found tracking number: {tracking_number}")
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Couldn't find tracking number: {e}")
            result["error"] = f"Tracking number not found: {e}"
            return result

        # Extract company name
        try:
            company_element = WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located(Page907Locators.COMPANY_NAME)
            )
            text_val = company_element.text
            if "\n" in text_val:
                company_name = text_val.split("\n", 1)[1].strip()
            else:
                company_name = text_val.replace("Company", "").strip()
            result["company_name"] = company_name
            logger.info(f"Found company name: {company_name}")
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Couldn't find company name: {e}")
            result["error"] = f"Company name not found: {e}"
            return result

        result["success"] = True
        return result

    except Exception as e:
        logger.error(f"Error in email_check_workflow: {e}")
        result["error"] = str(e)
        return result