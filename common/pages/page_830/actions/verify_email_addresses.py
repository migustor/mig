import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from common.pages.page_830.locators import Page830Locators

def verify_email_addresses(driver, timeout=10):
    """
    Verifies email addresses on page 830, extracting the type (personal, invoice, business)
    and the email address itself.
    
    Args:
        driver: Selenium WebDriver
        timeout: Wait time for elements on the page (in seconds)
        
    Returns:
        list: List of dictionaries with information about each email,
              for example [{'type': 'personal', 'email': 'personal@nt.gl'}, ...]
    """
    logger = logging.getLogger('test')
    logger.info("Extracting email addresses from page 830")
    
    try:
        # Wait for the visible container with email addresses
        container = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(Page830Locators.EMAIL_CONTAINER)
        )
        
        # Find all email data elements within the container
        email_elements = container.find_elements(*Page830Locators.EMAIL_DATA_ELEMENTS)
        emails = []
        
        for fontEl in email_elements:
            try:
                email_anchor = fontEl.find_element(*Page830Locators.EMAIL_LINK)
                email_value = email_anchor.text.strip()
            except NoSuchElementException:
                email_value = ""
            
            try:
                type_input = fontEl.find_element(*Page830Locators.EMAIL_TYPE_INPUT)
                type_id = type_input.get_attribute("value").strip()
            except NoSuchElementException:
                type_id = ""
            
            email_type = "unknown"
            if type_id == "8":
                email_type = "personal"
            elif type_id == "9":
                email_type = "business"
            elif type_id == "11":
                email_type = "invoice"
                
            emails.append({"email": email_value, "type": email_type})
            logger.info(f"Found email: {email_value} of type: {email_type}")
        
        logger.info(f"Found {len(emails)} email addresses")
        return emails
    
    except TimeoutException:
        logger.error("Timeout while waiting for email container")
        return []
    
    except Exception as e:
        logger.error("Error extracting email addresses: " + str(e))
        return []