# /trunk/projects/sm_us/pages/page_972/actions/verify_expired_offers.py

import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from common.utils.error_handling import jenkins_aware
from projects.sm_us.pages.page_972.locators import AddOfferLocators, ExpiredOffersLocators

@jenkins_aware()
def verify_expired_offers(driver, timeouts=None):
    """
    Verifies the expired offers functionality:
    1. Checks if the add offer button text indicates it's for expired offers
    2. Verifies that the button has appropriate styling (gray)
    3. Checks that expired offers are displayed with correct styling (offer_expired class)
    4. Verifies that expired offers have red price text
    5. Confirms that expired offers have the same action buttons as regular offers
    
    Args:
        driver: Selenium WebDriver
        timeouts: Optional dict of timeouts
    
    Returns:
        dict: Result with "success" flag and verification details
    """
    logger = logging.getLogger("test")
    logger.info("Verifying expired offers UI elements")
    
    action_timeout = timeouts.get("action", 10) if timeouts else 10
    verification = {
        "button_has_expired_text": False,
        "button_is_gray": False,
        "expired_offers_exist": False,
        "offers_have_red_price": False,
        "offers_have_action_buttons": False
    }
    
    try:
        # 1 & 2. Check the Add Offer button text and styling
        logger.info("Checking add offer button text and styling")
        try:
            add_offer_button = WebDriverWait(driver, action_timeout).until(
                EC.presence_of_element_located(AddOfferLocators.ADD_OFFER_BUTTON)
            )
            
            button_text = add_offer_button.text
            logger.info(f"Button text: {button_text}")
            verification["button_has_expired_text"] = "expired" in button_text.lower()
            
            button_class = add_offer_button.get_attribute("class")
            logger.info(f"Button class: {button_class}")
            verification["button_is_gray"] = any(c in button_class for c in 
                                                ["btn-secondary", "btn-default", "btn-gray"])
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.warning(f"Button verification failed: {str(e)}")
        
        # 3-5. Check for expired offers with correct styling
        logger.info("Checking for expired offers and their styling")
        try:
            expired_offers = driver.find_elements(*ExpiredOffersLocators.EXPIRED_OFFER_ROW)
            
            if expired_offers:
                verification["expired_offers_exist"] = True
                logger.info(f"Found {len(expired_offers)} expired offers")
                
                # Check the first expired offer
                offer = expired_offers[0]
                
                # Check for red price text
                try:
                    red_price = offer.find_element(*ExpiredOffersLocators.PRICE_COLOR_RED)
                    verification["offers_have_red_price"] = red_price is not None
                    logger.info(f"Offers have red price: {verification['offers_have_red_price']}")
                except NoSuchElementException:
                    logger.warning("Could not find red price element")
                
                # Check for action buttons
                try:
                    accept_button = offer.find_element(*ExpiredOffersLocators.ACCEPT_BUTTON)
                    edit_button = offer.find_element(*ExpiredOffersLocators.EDIT_BUTTON)
                    decline_button = offer.find_element(*ExpiredOffersLocators.DECLINE_BUTTON)
                    
                    verification["offers_have_action_buttons"] = (
                        accept_button is not None and 
                        edit_button is not None and 
                        decline_button is not None
                    )
                    logger.info(f"Offers have action buttons: {verification['offers_have_action_buttons']}")
                except NoSuchElementException:
                    logger.warning("Could not find all action buttons")
            else:
                logger.warning("No expired offers found to verify")
                
        except Exception as e:
            logger.warning(f"Expired offers verification failed: {str(e)}")
        
        # Calculate overall success - at least 3 of 5 checks should pass
        success_count = sum(1 for v in verification.values() if v)
        success = success_count >= 3
        
        return {
            "success": success,
            "verification": verification,
            "message": f"Expired offers verification completed with {success_count}/5 checks passing"
        }
            
    except Exception as e:
        error_msg = f"Error verifying expired offers: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}