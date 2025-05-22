# /trunk/projects/sm_us/pages/page_972/actions/add_expired_offer.py
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from common.utils.error_handling import jenkins_aware
from projects.sm_us.pages.page_972.locators import AddOfferLocators

@jenkins_aware()
def add_expired_offer(driver, company_id, quantity=2, price=33, timeouts=None):
    """
    Adds an expired offer to a presale.
    
    Args:
        driver: Selenium WebDriver
        company_id: Company ID for the offer
        quantity: Quantity to add (default=2)
        price: Price to set (default=33)
        timeouts: Optional dict of timeouts, e.g. {"action": 15}
    
    Returns:
        dict: Result with "success" flag and optional "error" message
    """
    logger = logging.getLogger("test")
    logger.info(f"Adding expired offer for company ID={company_id} with quantity={quantity} and price={price}")
    
    action_timeout = timeouts.get("action", 10) if timeouts else 10
    
    try:
        # 1) Click the "Add Offer" button
        logger.info("Clicking 'Add Offer' button")
        add_offer_button = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable(AddOfferLocators.ADD_OFFER_BUTTON)
        )
        add_offer_button.click()
        
        # 2) Enter company ID in the autocompleter
        logger.info(f"Entering company ID: {company_id}")
        company_field = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable(AddOfferLocators.COMPANY_AUTOCOMPLETE_FIELD)
        )
        company_field.clear()
        company_field.send_keys(str(company_id))
        
        # 3) Wait for and click the autocomplete dropdown item
        logger.info("Waiting for autocomplete dropdown to appear")
        time.sleep(1)  # Give autocomplete time to show suggestions
        
        # Look for the dropdown item with the specific company ID
        autocomplete_item = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable((
                By.XPATH, 
                f"//ul[contains(@class, 'typeahead')]/li[@data-value='{company_id}']"
            ))
        )
        logger.info(f"Found autocomplete item with data-value={company_id}, clicking it")
        autocomplete_item.click()
        
        # 4) Enter quantity
        logger.info(f"Entering quantity: {quantity}")
        quantity_field = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable(AddOfferLocators.QUANTITY_FIELD)
        )
        quantity_field.clear()
        quantity_field.send_keys(str(quantity))
        
        # 5) Enter price
        logger.info(f"Entering price: {price}")
        price_field = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable(AddOfferLocators.PRICE_FIELD)
        )
        price_field.clear()
        price_field.send_keys(str(price))
        
        # 6) Click the Add button to submit the form
        logger.info("Clicking 'Add Offer' submit button")
        add_button = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable(AddOfferLocators.SUBMIT_BUTTON)
        )
        add_button.click()
        
        # 7) Wait for form submission to complete
        time.sleep(2)
        
        return {
            "success": True,
            "company_id": company_id,
            "quantity": quantity,
            "price": price
        }
            
    except (TimeoutException, NoSuchElementException) as e:
        error_msg = f"Element not found or timed out during add_expired_offer: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Error adding expired offer: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}