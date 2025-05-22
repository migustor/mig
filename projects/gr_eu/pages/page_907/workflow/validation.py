import logging
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Action that clicks "Generate email" and "Empty"
from projects.gr_eu.pages.page_907.actions.generate_email_and_empty_select import generate_email_and_empty_select
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def validation_workflow(driver, order_data, timeouts=None):
    """
    1) Generate email (click 'Generate email', select 'Empty')
    2) Extract subject from #send_logistics_email_subject
    3) Check that subject contains order_id, tracking_number, company_name
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info("Starting validation_workflow")

    result = {
        "success": False,
        "skipped": False,
        "error": None,
        "email_subject": None,
        "validation": {
            "order_id_match": False,
            "tracking_number_match": False,
            "company_name_match": False,
            "overall_match": False
        }
    }

    order_id = str(order_data.get("order_id", "")).strip()
    tracking = str(order_data.get("tracking_number", "")).strip()
    company = str(order_data.get("company_name", "")).strip()

    if not order_id or not tracking or not company:
        result["error"] = "Missing order_id, tracking_number, or company_name"
        return result

    # Step 1: generate email
    try:
        gen_res = generate_email_and_empty_select(driver, timeouts)
        if not gen_res["success"]:
            if gen_res.get("skipped", False):
                # This is a soft failure - just mark as skipped and return
                logger.info(f"Skipping validation for order {order_id}: {gen_res['error']}")
                result["skipped"] = True
                result["error"] = gen_res["error"]
                return result
            else:
                # This is a hard failure
                result["error"] = f"Failed to generate email: {gen_res['error']}"
                return result
    except Exception as e:
        result["error"] = f"Exception in generate_email_and_empty_select: {str(e)}"
        return result

    time.sleep(3)  # wait for the email subject to appear

    # Step 2: extract email subject
    wait_timeout = timeouts.get("wait", 20)
    try:
        subject_el = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located((By.ID, "send_logistics_email_subject"))
        )
        subject_text = subject_el.get_attribute("value").strip()
        result["email_subject"] = subject_text
        logger.info(f"Email subject: {subject_text}")
    except (TimeoutException, NoSuchElementException) as e:
        result["error"] = f"Failed to get email subject: {e}"
        return result

    # Step 3: check order_id, tracking, company in subject
    order_match = (order_id in subject_text)
    tracking_match = (tracking in subject_text)
    company_match = (company in subject_text)

    result["validation"]["order_id_match"] = order_match
    result["validation"]["tracking_number_match"] = tracking_match
    result["validation"]["company_name_match"] = company_match
    result["validation"]["overall_match"] = order_match and tracking_match and company_match

    logger.info(f"Validation results: order_id_match={order_match}, tracking_number_match={tracking_match}, company_name_match={company_match}, overall_match={result['validation']['overall_match']}")

    if not result["validation"]["overall_match"]:
        if not order_match:
            logger.error(f"Order ID mismatch: expected '{order_id}' not found in subject '{subject_text}'")
        if not tracking_match:
            logger.error(f"Tracking number mismatch: expected '{tracking}' not found in subject '{subject_text}'")
        if not company_match:
            logger.error(f"Company name mismatch: expected '{company}' not found in subject '{subject_text}'")
        logger.warning("Validation failed on subject match")
        result["error"] = "Some data not found in email subject"
        return result

    result["success"] = True
    return result