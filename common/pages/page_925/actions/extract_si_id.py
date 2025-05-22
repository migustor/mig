# /common/pages/page_925/actions/extract_si_id.py
import logging
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import locators
from common.pages.page_925.locators import RESULTS_TABLE

def extract_si_id(driver, timeouts=None):
    """
    Extracts the SI ID from the results table
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with success status, SI ID and error message if any
    """
    logger = logging.getLogger('test')
    logger.info("Extracting SI ID from results table")
    
    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)  # Default to 15 if not specified
    
    try:
        # Wait for the results table to be present
        logger.info("Waiting for results table...")
        WebDriverWait(driver, action_timeout).until(
            EC.presence_of_element_located(RESULTS_TABLE["table_panel"])
        )
        
        # Check if there are any rows in the table
        si_links = driver.find_elements(*RESULTS_TABLE["si_links"])
        
        if not si_links:
            logger.warning("No SI links found in results table")
            return {"success": True, "si_id": None, "error": None}
        
        # Extract the SI ID from the first link's href attribute
        first_link = si_links[0]
        href = first_link.get_attribute("href")
        
        # Parse the ID from the URL using regex
        match = re.search(r'&id=(\d+)', href)
        if match:
            si_id = match.group(1)
            logger.info(f"Successfully extracted SI ID: {si_id}")
            return {"success": True, "si_id": si_id, "error": None}
        else:
            error_msg = f"Could not extract SI ID from href: {href}"
            logger.error(error_msg)
            return {"success": False, "si_id": None, "error": error_msg}
            
    except TimeoutException as te:
        error_msg = f"Timeout waiting for results table: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "si_id": None, "error": error_msg}
    
    except NoSuchElementException as nse:
        error_msg = f"Results table not found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "si_id": None, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error extracting SI ID: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "si_id": None, "error": error_msg}