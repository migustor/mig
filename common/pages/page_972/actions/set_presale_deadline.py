# /common/pages/page_972/actions/set_presale_deadline.py
import logging
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from common.utils.error_handling import jenkins_aware
from common.pages.page_972.page_info import get_created_presale_url
from common.pages.page_972.locators import Page972WithLeadLocators

@jenkins_aware()
def set_presale_deadline(driver, project_name, presale_id, specific_date=None, days_from_now=None, timeouts=None):
    """
    Sets the deadline for accepting offers in a presale.
    
    Args:
        driver: Selenium WebDriver
        project_name: Project code (e.g. "sm_us")
        presale_id: ID of the presale to modify
        specific_date: A specific date to set (string in format 'YYYY-MM-DD' or datetime object)
        days_from_now: Number of days from current date to set as deadline (default=None)
        timeouts: Optional dict of timeouts, e.g. {"action": 15}
    
    Returns:
        dict: Result with "success" flag and optional "error" message
    """
    logger = logging.getLogger("test")
    logger.info(f"Setting deadline for presale ID={presale_id} on project={project_name}")
    
    action_timeout = timeouts.get("action", 15) if timeouts else 15
    
    try:
        # Determine the deadline date
        if specific_date:
            if isinstance(specific_date, str):
                try:
                    # Try to parse the date string
                    deadline_date = datetime.strptime(specific_date, "%Y-%m-%d")
                except ValueError:
                    error_msg = f"Invalid date format: {specific_date}. Expected format: YYYY-MM-DD"
                    logger.error(error_msg)
                    return {"success": False, "error": error_msg}
            else:
                # Assume it's already a datetime object
                deadline_date = specific_date
        elif days_from_now is not None:
            # Calculate date based on days from now
            deadline_date = datetime.now() + timedelta(days=days_from_now)
        else:
            # Default to 1 day from now if neither specific_date nor days_from_now provided
            deadline_date = datetime.now() + timedelta(days=1)
        
        # Format the date for JavaScript
        formatted_date = deadline_date.strftime("%Y-%m-%d")
        
        # 1) Generate the URL and navigate to the presale edit page
        presale_url = get_created_presale_url(project_name, presale_id)
        if not presale_url:
            error_msg = f"Could not build presale edit URL for project '{project_name}'"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        logger.info(f"Navigating to: {presale_url}")
        driver.get(presale_url)
        
        # Wait for page to fully load
        WebDriverWait(driver, action_timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        # 2) Try a different approach - use JavaScript to click the radio button
        # First, find the actual input element
        logger.info("Clicking 'Yes' radio button for deadline using JavaScript")
        try:
            # Look for the actual radio input element
            radio_input = WebDriverWait(driver, action_timeout).until(
                EC.presence_of_element_located((By.ID, "accept_offers_deadline_yes"))
            )
            # Use JavaScript to click it
            driver.execute_script("arguments[0].click(); arguments[0].checked = true;", radio_input)
            logger.info("Successfully clicked radio button using JavaScript")
        except Exception as e:
            logger.warning(f"Failed to click radio input with ID. Trying alternative approach: {str(e)}")
            # Alternative approach - find enclosing div and click using JS
            js_script = """
            var radioYes = document.querySelector('input[name="accept_offers_deadline"][value="1"]');
            if (radioYes) {
                radioYes.checked = true;
                var event = new Event('change', { bubbles: true });
                radioYes.dispatchEvent(event);
                return true;
            }
            return false;
            """
            success = driver.execute_script(js_script)
            if not success:
                logger.warning("JavaScript approach didn't find the radio button. Trying XPath...")
                # As a last resort, try clicking the yes radio button by its XPath
                radio_xpath = "//input[@name='accept_offers_deadline' and @value='1']"
                radio_element = driver.find_element(By.XPATH, radio_xpath)
                driver.execute_script("arguments[0].click();", radio_element)
        
        time.sleep(1)  # Give page time to react
        
        # 3) Set the deadline date using JavaScript approach
        logger.info(f"Setting deadline to: {formatted_date}")
        deadline_field = WebDriverWait(driver, action_timeout).until(
            EC.presence_of_element_located(Page972WithLeadLocators.DEADLINE_DATE_FIELD)
        )
        
        # Use JavaScript to set the date value directly
        date_script = "arguments[0].value = arguments[1];"
        driver.execute_script(date_script, deadline_field, formatted_date)
        
        # Trigger an onchange event to ensure the form recognizes the change
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", deadline_field)
        
        # 4) Click the Update button using JavaScript to avoid any interception
        logger.info("Clicking Update button using JavaScript")
        update_button = WebDriverWait(driver, action_timeout).until(
            EC.presence_of_element_located(Page972WithLeadLocators.UPDATE_BUTTON)
        )
        driver.execute_script("arguments[0].click();", update_button)
        
        # Wait for page to process the update
        time.sleep(2)
        
        # Format date for return value in a more human-readable format
        display_date = deadline_date.strftime("%d-%b-%Y")  # e.g. "02-May-2025"
        
        return {
            "success": True,
            "presale_id": presale_id,
            "deadline_date": display_date
        }
            
    except (TimeoutException, NoSuchElementException) as e:
        error_msg = f"Element not found or timed out during set_presale_deadline: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Error setting presale deadline: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}