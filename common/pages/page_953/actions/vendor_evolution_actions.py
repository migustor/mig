# /common/pages/page_953/actions/vendor_evolution_actions.py
import logging
import time
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import locators
from common.pages.page_953.locators import VENDOR_EVOLUTION_FORM, REPORT_RESULTS, ERROR_MESSAGES

def navigate_to_vendor_evolution_page(driver, project_name="ag_eu"):
    """
    Navigates to the Vendor Evolution Report page
    
    Args:
        driver: Selenium WebDriver
        project_name: Project code (default: "ag_eu")
        
    Returns:
        bool: True if navigation successful, False otherwise
    """
    logger = logging.getLogger('test')
    
    try:
        # Import page_info here to avoid circular imports
        from common.pages.page_953.page_info import get_page_953_url
        url = get_page_953_url(project_name)
        
        logger.info(f"Navigating to Vendor Evolution Report page: {url}")
        driver.get(url)
        
        # Wait for page to load - check for company input field
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(VENDOR_EVOLUTION_FORM["company_name_input"])
        )
        
        logger.info("Successfully navigated to Vendor Evolution Report page")
        return True
        
    except Exception as e:
        logger.error(f"Failed to navigate to Vendor Evolution Report page: {str(e)}")
        return False

def input_company_name(driver, company_name, wait_timeout=10):
    """
    Inputs company name and selects it from autocomplete dropdown
    
    Args:
        driver: Selenium WebDriver
        company_name: Company name or ID to search for
        wait_timeout: Timeout for waiting elements
        
    Returns:
        bool: True if company selected successfully, False otherwise
    """
    logger = logging.getLogger('test')
    
    try:
        logger.info(f"Inputting company name: {company_name}")
        
        # Find and clear the company name input field
        company_input = WebDriverWait(driver, wait_timeout).until(
            EC.element_to_be_clickable(VENDOR_EVOLUTION_FORM["company_name_input"])
        )
        company_input.clear()
        company_input.send_keys(company_name)
        
        # Wait for autocomplete dropdown to appear
        logger.info("Waiting for autocomplete dropdown...")
        time.sleep(1)  # Small delay to ensure dropdown appears
        
        # Click on the first autocomplete suggestion
        autocomplete_item = WebDriverWait(driver, wait_timeout).until(
            EC.element_to_be_clickable(VENDOR_EVOLUTION_FORM["company_autocomplete_item"])
        )
        
        # Extract selected company text for verification
        selected_company_text = autocomplete_item.text
        logger.info(f"Found autocomplete suggestion: {selected_company_text}")
        
        # Click on the suggestion
        autocomplete_item.click()
        
        logger.info(f"Successfully selected company: {selected_company_text}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to input and select company: {str(e)}")
        return False

def set_date_range(driver, from_date="01-Jan-2024", to_date=None, wait_timeout=10):
    """
    Sets only the from date in format "01-Jan-2024" using JavaScript
    
    Args:
        driver: Selenium WebDriver
        from_date: Start date in format "01-Jan-2024" 
        to_date: Not used, kept for backward compatibility
        wait_timeout: Timeout for waiting elements
        
    Returns:
        bool: True if date set successfully, False otherwise
    """
    logger = logging.getLogger('test')
    
    try:
        # Set default date if not provided
        if from_date is None:
            from_date = "01-Jan-2024"
            
        logger.info(f"Setting from date: {from_date}")
        
        # JavaScript to set input value
        script = "arguments[0].value = arguments[1];"
        
        # Set From date using JavaScript
        from_date_field = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(VENDOR_EVOLUTION_FORM["date_from_field"])
        )
        driver.execute_script(script, from_date_field, from_date)
        
        logger.info(f"Date '{from_date}' set successfully using JavaScript")
        return True
        
    except Exception as e:
        logger.error(f"Failed to set date: {str(e)}")
        return False

def submit_vendor_evolution_form(driver, wait_timeout=10):
    """
    Submits the Vendor Evolution Report form
    
    Args:
        driver: Selenium WebDriver
        wait_timeout: Timeout for waiting elements
        
    Returns:
        bool: True if form submitted successfully, False otherwise
    """
    logger = logging.getLogger('test')
    
    try:
        logger.info("Submitting Vendor Evolution Report form")
        
        # Click the Submit button
        submit_button = WebDriverWait(driver, wait_timeout).until(
            EC.element_to_be_clickable(VENDOR_EVOLUTION_FORM["submit_button"])
        )
        submit_button.click()
        
        # Wait for results or error message
        try:
            # Try to wait for purchase history section (success case)
            WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located(REPORT_RESULTS["purchase_history_section"])
            )
            logger.info("Form submitted successfully, purchase history section is displayed")
            return True
        except TimeoutException:
            # Check if "No data found" message is displayed
            try:
                no_data_element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located(ERROR_MESSAGES["no_data_found"])
                )
                logger.warning(f"Form submitted, but no data found: {no_data_element.text}")
                return True  # Still consider this a successful submission
            except:
                # Check for error message
                try:
                    error_element = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located(ERROR_MESSAGES["validation_error"])
                    )
                    logger.error(f"Form submission failed with error: {error_element.text}")
                    return False
                except:
                    logger.error("Form submission status unknown")
                    return False
        
    except Exception as e:
        logger.error(f"Failed to submit form: {str(e)}")
        return False

def verify_purchase_history_section(driver, wait_timeout=10):
    """
    Verifies that the purchase history section is displayed with data
    
    Args:
        driver: Selenium WebDriver
        wait_timeout: Timeout for waiting elements
        
    Returns:
        dict: Result with keys 'success', 'item_count', and 'message'
    """
    logger = logging.getLogger('test')
    
    try:
        logger.info("Verifying purchase history section")
        
        # Wait for purchase history section
        WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_element_located(REPORT_RESULTS["purchase_history_section"])
        )
        
        # Get all item rows
        try:
            item_rows = driver.find_elements(*REPORT_RESULTS["items_rows"])
            item_count = len(item_rows)
            
            if item_count > 0:
                logger.info(f"Purchase history section verified with {item_count} items")
                return {
                    "success": True,
                    "item_count": item_count,
                    "message": f"Found {item_count} items in purchase history"
                }
            else:
                logger.warning("Purchase history section exists but contains no items")
                return {
                    "success": True,
                    "item_count": 0,
                    "message": "Purchase history section exists but contains no items"
                }
        except:
            logger.warning("Failed to count items in purchase history section")
            return {
                "success": True,
                "item_count": -1,
                "message": "Purchase history section exists but failed to count items"
            }
        
    except TimeoutException:
        # Check if "No data found" message is displayed
        try:
            no_data_element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(ERROR_MESSAGES["no_data_found"])
            )
            logger.warning(f"No data found message displayed: {no_data_element.text}")
            return {
                "success": True,
                "item_count": 0,
                "message": "No data found for the selected criteria"
            }
        except:
            logger.error("Purchase history section not found")
            return {
                "success": False,
                "item_count": 0,
                "message": "Purchase history section not found"
            }
    except Exception as e:
        logger.error(f"Error verifying purchase history section: {str(e)}")
        return {
            "success": False,
            "item_count": 0,
            "message": f"Error: {str(e)}"
        }