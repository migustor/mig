"""
Test for VAT validation in German zone
"""
import logging
import time
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Common utilities
from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.config.login.login_as_user import login_as_user
from common.utils.error_handling import jenkins_aware

# Page 864 actions
from common.pages.page_864.actions.de_zone_vat_set_0 import de_zone_vat_set_0
from common.pages.page_864.actions.de_zone_vat_add_to_inv import de_zone_vat_add_to_inv
from common.pages.page_864.actions.de_zone_vat_popup_no import de_zone_vat_popup_no
from common.pages.page_864.actions.de_zone_vat_popup_yes import de_zone_vat_popup_yes
from common.pages.page_864.actions.de_zone_vat_add_old_VAT import de_zone_vat_add_old_VAT
from common.pages.page_864.actions.de_zone_vat_add_old_INV import de_zone_vat_add_old_inv_net
from common.pages.page_864.locators import Page864Locators
from common.pages.page_864.page_info import get_page_864_url

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(" - MAIN TEST - ")

def set_field_value(driver, field_name, expected_value):
    """
    Helper function to set a field value if it differs from expected value
    Handles decimal values and popups
    """
    try:
        field = driver.find_element(By.CSS_SELECTOR, f"input[name='{field_name}']")
        current_value = field.get_attribute("value")
        
        # Convert both values to float for comparison
        try:
            current_float = float(current_value.replace(',', ''))
            expected_float = float(expected_value.replace(',', ''))
            
            # If values are equal (ignoring decimal places), no need to change
            if abs(current_float - expected_float) < 0.001:  # Using small epsilon for float comparison
                logger.info(f"Value {current_value} is equivalent to expected {expected_value}, no change needed")
                return False
                
            # Format expected value with 2 decimal places
            formatted_expected = f"{expected_float:.2f}"
            
            # Update the value
            field_id = field.get_attribute("id")
            driver.execute_script(f"""
                document.getElementById('{field_id}').value = '{formatted_expected}';
                const event = new Event('change', {{ bubbles: true }});
                document.getElementById('{field_id}').dispatchEvent(event);
            """)
            logger.info(f"Updated {field_name} from {current_value} to {formatted_expected}")
            time.sleep(1)
            
            # Handle potential popup
            try:
                # Wait for popup (if it appears)
                modal_elements = WebDriverWait(driver, 3).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ui-dialog-content"))
                )
                
                # Check if any modal is visible
                for element in modal_elements:
                    if element.is_displayed():
                        # Find and click the YES button
                        yes_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[text()='YES']"))
                        )
                        yes_button.click()
                        logger.info("Clicked 'YES' on popup after value change")
                        time.sleep(1)
                        break
            except:
                # No popup appeared, which is fine
                pass
                
            return True
            
        except ValueError as ve:
            logger.error(f"Error converting values to float: {str(ve)}")
            raise
            
    except Exception as e:
        logger.error(f"Error setting {field_name}: {str(e)}")
        raise

@jenkins_aware()
def test_de_zone_vat_validation():
    """
    Test for VAT validation in German zone
    """
    driver = setup_chrome_driver(headless=False)
    
    # Test parameters
    project_name = "sm_eu"
    document_id = 58435
    
    # Expected initial values (as strings, will be formatted with decimals in set_field_value)
    expected_inv_net = "1000"
    expected_vat = "200"
    
    # Variables to store original values
    original_vat = None
    original_inv_net = None
    
    try:
        # Step 1: Login as user 'vb'
        logger.info("Step 1: Logging in as user 'vb'")
        time.sleep(1)
        login_result = login_as_user(driver, project_name, "vb")
        time.sleep(1)
        
        if not login_result["success"]:
            logger.error(f"Login failed: {login_result.get('error', 'Unknown error')}")
            return {"success": False, "error": "Login failed"}
            
        # Navigate to specific document page
        url = get_page_864_url(project_name, document_id)
        driver.get(url)
        logger.info(f"Navigated to {url}")
        time.sleep(3)  # Wait for page to load
        
        # Step 1.1: Check and adjust initial values if needed
        logger.info("Step 1.1: Checking and adjusting initial values")
        try:
            # Get current values
            vat_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_vat_amount']")
            inv_net_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_net_amount']")
            original_vat = vat_input.get_attribute("value")
            original_inv_net = inv_net_input.get_attribute("value")
            
            # Check and adjust values if needed
            vat_changed = set_field_value(driver, "invoice_vat_amount", expected_vat)
            inv_net_changed = set_field_value(driver, "invoice_net_amount", expected_inv_net)
            
            if vat_changed or inv_net_changed:
                logger.info("Initial values were adjusted to match expected values")
                time.sleep(2)  # Give time for changes to take effect
        except Exception as e:
            logger.error(f"Failed to check/adjust initial values: {str(e)}")
            return {"success": False, "error": "Failed to check/adjust initial values"}
        
        # Step 2: Set VAT to 0
        logger.info("Step 2: Setting VAT to 0")
        time.sleep(1)
        vat_result = de_zone_vat_set_0(driver, project_name, document_id)
        time.sleep(1)
        
        if not vat_result["success"]:
            logger.error(f"Failed to set VAT to 0: {vat_result.get('error', 'Unknown error')}")
            return {"success": False, "error": "Failed to set VAT to 0"}
        
        # Save original VAT value
        original_vat = vat_result["original_vat"]
        logger.info(f"Saved original VAT value: {original_vat}")
        
        # Step 2.1: Check for red background after setting VAT to 0
        logger.info("Step 2.1: Checking for red background after setting VAT to 0")
        time.sleep(3)  # Give more time for background change
        
        try:
            # Check if red background appears
            red_cell = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(Page864Locators.TOTAL_CELL_RED)
            )
            logger.info("Confirmed: Total cell has red background as expected after setting VAT to 0")
        except Exception as e:
            logger.error(f"Red background check failed: {str(e)}")
            return {"success": False, "error": "Total cell did not change to red background after setting VAT to 0"}
        
        # Step 3: Add VAT to Invoice Net
        logger.info("Step 3: Adding VAT to Invoice Net")
        time.sleep(1)
        inv_result = de_zone_vat_add_to_inv(driver, project_name, document_id, original_vat)
        time.sleep(1)
        
        if not inv_result["success"]:
            logger.error(f"Failed to add VAT to Invoice Net: {inv_result.get('error', 'Unknown error')}")
            return {"success": False, "error": "Failed to add VAT to Invoice Net"}
        
        # Save original Invoice Net value
        original_inv_net = inv_result["original_inv_net"]
        logger.info(f"Saved original Invoice Net value: {original_inv_net}")
        
        # Step 4: Click NO on popup
        logger.info("Step 4: Clicking NO on popup")
        time.sleep(1)
        no_result = de_zone_vat_popup_no(driver)
        time.sleep(1)
        
        if not no_result["success"]:
            logger.error(f"Failed to click NO on popup: {no_result.get('error', 'Unknown error')}")
            return {"success": False, "error": "Failed to click NO on popup"}
        
        # Step 4.1: Verify background is still red after clicking NO
        logger.info("Step 4.1: Verifying background is still red after clicking NO")
        time.sleep(3)  # Give more time for background change
        
        try:
            # Check if red background is still present
            red_cell = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(Page864Locators.TOTAL_CELL_RED)
            )
            logger.info("Confirmed: Total cell still has red background as expected after clicking NO")
        except Exception as e:
            logger.error(f"Red background check failed: {str(e)}")
            return {"success": False, "error": "Total cell no longer has red background after clicking NO"}
        
        # Step 5: Add VAT to Invoice Net again
        logger.info("Step 5: Adding VAT to Invoice Net again")
        time.sleep(1)
        inv_result_2 = de_zone_vat_add_to_inv(driver, project_name, document_id, original_vat)
        time.sleep(1)
        
        if not inv_result_2["success"]:
            logger.error(f"Failed to add VAT to Invoice Net (second attempt): {inv_result_2.get('error', 'Unknown error')}")
            return {"success": False, "error": "Failed to add VAT to Invoice Net (second attempt)"}
        
        # Step 6: Click YES on popup
        logger.info("Step 6: Clicking YES on popup")
        time.sleep(1)
        yes_result = de_zone_vat_popup_yes(driver)
        time.sleep(1)
        
        if not yes_result["success"]:
            logger.error(f"Failed to click YES on popup: {yes_result.get('error', 'Unknown error')}")
            return {"success": False, "error": "Failed to click YES on popup"}
        
        # Step 6.1: Check for neutral background in Total cell after clicking YES
        logger.info("Step 6.1: Checking that background becomes neutral after clicking YES")
        time.sleep(3)  # Give more time for background change
        
        try:
            # Check for normal cell (neutral background)
            normal_cell = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(Page864Locators.TOTAL_CELL)
            )
            logger.info("Confirmed: Total cell has neutral background as expected after clicking YES")
        except Exception as e:
            logger.error(f"Neutral background check failed: {str(e)}")
            return {"success": False, "error": "Total cell did not change to neutral background"}
        
        # Step 7: Restore original VAT value
        logger.info("Step 7: Restoring original VAT value")
        time.sleep(1)
        restore_vat_result = de_zone_vat_add_old_VAT(driver, project_name, document_id, original_vat)
        time.sleep(1)
        
        if not restore_vat_result["success"]:
            logger.error(f"Failed to restore original VAT: {restore_vat_result.get('error', 'Unknown error')}")
            return {"success": False, "error": "Failed to restore original VAT"}
        
        # Step 8: Restore original Invoice Net value
        logger.info("Step 8: Restoring original Invoice Net value")
        time.sleep(1)
        restore_inv_result = de_zone_vat_add_old_inv_net(driver, project_name, document_id, original_inv_net)
        time.sleep(1)
        
        if not restore_inv_result["success"]:
            logger.error(f"Failed to restore original Invoice Net: {restore_inv_result.get('error', 'Unknown error')}")
            return {"success": False, "error": "Failed to restore original Invoice Net"}
        
        # Step 8.1 is no longer needed since we already verified the background is neutral in step 6.1
        
        logger.info("DE zone VAT validation test completed successfully")
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Unexpected error during test: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
        
    finally:
        release_driver(driver)

@jenkins_aware()
def test_eu_zone_vat_validation():
    """
    Test for VAT validation in EU zone
    """
    driver = setup_chrome_driver(headless=False)
    
    # Test parameters
    project_name = "sm_eu"
    document_id = 58138
    
    # Expected initial values (as strings, will be formatted with decimals in set_field_value)
    expected_inv_net = "2000"
    expected_vat = "0"
    
    # Variables to store original values
    original_vat = None
    original_inv_net = None
    
    try:
        # Step 1: Login as user 'vb'
        logger.info("Step 1: Logging in as user 'vb'")
        time.sleep(1)
        login_result = login_as_user(driver, project_name, "vb")
        time.sleep(1)
        
        if not login_result["success"]:
            logger.error(f"Login failed: {login_result.get('error', 'Unknown error')}")
            return {"success": False, "error": "Login failed"}
        
        # Navigate to specific document page
        url = get_page_864_url(project_name, document_id)
        driver.get(url)
        logger.info(f"Navigated to {url}")
        time.sleep(3)  # Wait for page to load
        
        # Step 1.1: Check and adjust initial values if needed
        logger.info("Step 1.1: Checking and adjusting initial values")
        try:
            # Get current values
            vat_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_vat_amount']")
            inv_net_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_net_amount']")
            original_vat = vat_input.get_attribute("value")
            original_inv_net = inv_net_input.get_attribute("value")
            
            # Check and adjust values if needed
            vat_changed = set_field_value(driver, "invoice_vat_amount", expected_vat)
            inv_net_changed = set_field_value(driver, "invoice_net_amount", expected_inv_net)
            
            if vat_changed or inv_net_changed:
                logger.info("Initial values were adjusted to match expected values")
                time.sleep(2)  # Give time for changes to take effect
        except Exception as e:
            logger.error(f"Failed to check/adjust initial values: {str(e)}")
            return {"success": False, "error": "Failed to check/adjust initial values"}
        
        # Step 2: Insert VAT - 10
        logger.info("Step 2: Setting VAT to 10")
        time.sleep(1)
        
        try:
            # Find VAT input field again to avoid stale reference
            vat_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_vat_amount']")
            vat_input_id = vat_input.get_attribute("id")
            
            # Use JavaScript to set VAT to 10
            driver.execute_script(f"""
                document.getElementById('{vat_input_id}').value = '10';
                const event = new Event('change', {{ bubbles: true }});
                document.getElementById('{vat_input_id}').dispatchEvent(event);
            """)
            logger.info("Set VAT value to 10")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Failed to set VAT to 10: {str(e)}")
            return {"success": False, "error": "Failed to set VAT to 10"}
        
        # Step 3: Handle EU zone popup - press NO
        logger.info("Step 3: Clicking NO on EU zone popup")
        time.sleep(2)
        
        try:
            # Find the modal dialog content
            modal_elements = driver.find_elements(By.CSS_SELECTOR, ".ui-dialog-content")
            alert_present = False
            alert_text = ""
            
            # Expected text for EU zone
            eu_expected_text = "The customer belongs to the EU/NON-EU zone. VAT/TAX should not be listed in the document. Are you sure you need to enter this information?"
            
            if modal_elements:
                for element in modal_elements:
                    if element.is_displayed():
                        alert_text = element.text.strip()
                        if eu_expected_text in alert_text:
                            alert_present = True
                            logger.info("EU ZONE ALERT PRESENT")
                            break
            
            if not alert_present:
                logger.error(f"EU ZONE ALERT NOT FOUND! Text found: '{alert_text}'")
                return {
                    "success": False, 
                    "error": "Expected EU zone alert text not found",
                    "alert_present": False,
                    "alert_text": alert_text
                }
            
            # Find and click the NO button
            no_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='NO']"))
            )
            no_button.click()
            logger.info("Clicked 'NO' button on EU zone popup")
            time.sleep(1)
            
        except Exception as e:
            error_msg = f"Error handling EU zone popup: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Step 4: Check that background hasn't changed (no red background)
        logger.info("Step 4: Verifying no background change after clicking NO")
        time.sleep(3)
        
        try:
            # Check for normal cell (no red background)
            normal_cell = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(Page864Locators.TOTAL_CELL)
            )
            logger.info("Confirmed: Total cell has no red background as expected after clicking NO")
        except Exception as e:
            logger.error(f"Background check failed: {str(e)}")
            return {"success": False, "error": "Failed to verify background state after clicking NO"}
        
        # Step 5: Insert VAT 10 again
        logger.info("Step 5: Setting VAT to 10 again")
        time.sleep(1)
        
        try:
            # Find VAT input field again to avoid stale reference
            vat_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_vat_amount']")
            vat_input_id = vat_input.get_attribute("id")
            
            # Use JavaScript to set VAT to 10 again
            driver.execute_script(f"""
                document.getElementById('{vat_input_id}').value = '10';
                const event = new Event('change', {{ bubbles: true }});
                document.getElementById('{vat_input_id}').dispatchEvent(event);
            """)
            logger.info("Set VAT value to 10 again")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Failed to set VAT to 10 again: {str(e)}")
            return {"success": False, "error": "Failed to set VAT to 10 again"}
        
        # Step 6: Handle EU zone popup - press YES
        logger.info("Step 6: Clicking YES on EU zone popup")
        time.sleep(2)
        
        try:
            # Find the modal dialog content
            modal_elements = driver.find_elements(By.CSS_SELECTOR, ".ui-dialog-content")
            alert_present = False
            alert_text = ""
            
            # Expected text for EU zone
            eu_expected_text = "The customer belongs to the EU/NON-EU zone. VAT/TAX should not be listed in the document. Are you sure you need to enter this information?"
            
            if modal_elements:
                for element in modal_elements:
                    if element.is_displayed():
                        alert_text = element.text.strip()
                        if eu_expected_text in alert_text:
                            alert_present = True
                            logger.info("EU ZONE ALERT PRESENT")
                            break
            
            if not alert_present:
                logger.error(f"EU ZONE ALERT NOT FOUND! Text found: '{alert_text}'")
                return {
                    "success": False, 
                    "error": "Expected EU zone alert text not found",
                    "alert_present": False,
                    "alert_text": alert_text
                }
            
            # Find and click the YES button
            yes_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='YES']"))
            )
            yes_button.click()
            logger.info("Clicked 'YES' button on EU zone popup")
            time.sleep(1)
            
        except Exception as e:
            error_msg = f"Error handling EU zone popup: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Step 7: Check for red background
        logger.info("Step 7: Checking for red background after clicking YES")
        time.sleep(3)
        
        try:
            # Check if red background appears
            red_cell = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(Page864Locators.TOTAL_CELL_RED)
            )
            logger.info("Confirmed: Total cell has red background as expected after clicking YES")
        except Exception as e:
            logger.error(f"Red background check failed: {str(e)}")
            return {"success": False, "error": "Total cell did not change to red background after clicking YES"}
        
        # Step 8: Calculate and set new Invoice Net value (original minus VAT)
        logger.info("Step 8: Dividing 10 from Invoice Net value")
        time.sleep(1)
        
        try:
            # Find the Invoice Net input field again to avoid stale reference
            inv_net_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_net_amount']")
            inv_net_input_id = inv_net_input.get_attribute("id")
            
            # Convert to float and subtract 10
            inv_net_float = float(original_inv_net.replace(',', ''))
            new_inv_net = inv_net_float - 10
            new_inv_net_str = f"{new_inv_net:.2f}"
            
            # Use JavaScript to set new Invoice Net value
            driver.execute_script(f"""
                document.getElementById('{inv_net_input_id}').value = '{new_inv_net_str}';
                const event = new Event('change', {{ bubbles: true }});
                document.getElementById('{inv_net_input_id}').dispatchEvent(event);
            """)
            logger.info(f"Set Invoice Net value to {new_inv_net_str}")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Failed to update Invoice Net value: {str(e)}")
            return {"success": False, "error": "Failed to update Invoice Net value"}
        
        # Step 9: Check for neutral background after updating Invoice Net
        logger.info("Step 9: Checking that background becomes neutral after updating Invoice Net")
        time.sleep(3)
        
        try:
            # Check for normal cell (neutral background)
            normal_cell = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(Page864Locators.TOTAL_CELL)
            )
            logger.info("Confirmed: Total cell has neutral background as expected after updating Invoice Net")
        except Exception as e:
            logger.error(f"Neutral background check failed: {str(e)}")
            return {"success": False, "error": "Total cell did not change to neutral background after updating Invoice Net"}
        
        # Step 10: Set VAT to 0
        logger.info("Step 10: Setting VAT to 0")
        time.sleep(1)
        
        try:
            # Find VAT input field again to avoid stale reference
            vat_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_vat_amount']")
            vat_input_id = vat_input.get_attribute("id")
            
            # Use JavaScript to set VAT to 0
            driver.execute_script(f"""
                document.getElementById('{vat_input_id}').value = '0';
                const event = new Event('change', {{ bubbles: true }});
                document.getElementById('{vat_input_id}').dispatchEvent(event);
            """)
            logger.info("Set VAT value to 0")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Failed to set VAT to 0: {str(e)}")
            return {"success": False, "error": "Failed to set VAT to 0"}
        
        # Step 11: Handle EU zone popup for VAT=0 - press YES
        logger.info("Step 11: Clicking YES on EU zone popup for VAT=0")
        time.sleep(2)
        
        try:
            # Check if popup appears for VAT=0
            modal_elements = driver.find_elements(By.CSS_SELECTOR, ".ui-dialog-content")
            if modal_elements and any(element.is_displayed() for element in modal_elements):
                # Find and click the YES button if popup appears
                yes_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='YES']"))
                )
                yes_button.click()
                logger.info("Clicked 'YES' button on EU zone popup for VAT=0")
            else:
                logger.info("No popup appeared for VAT=0 (this is expected in some cases)")
            
            time.sleep(1)
            
        except Exception as e:
            error_msg = f"Error handling EU zone popup for VAT=0: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Step 12: Check that background is still neutral
        logger.info("Step 12: Checking that background is still neutral")
        time.sleep(3)
        
        try:
            # Check for normal cell (neutral background)
            normal_cell = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(Page864Locators.TOTAL_CELL)
            )
            logger.info("Confirmed: Total cell still has neutral background as expected")
        except Exception as e:
            logger.error(f"Neutral background check failed: {str(e)}")
            return {"success": False, "error": "Failed to verify neutral background state"}
        
        # Step 13: Restore original Invoice Net value
        logger.info("Step 13: Restoring original Invoice Net value")
        time.sleep(1)
        
        try:
            # Find the Invoice Net input field again to avoid stale reference
            inv_net_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_net_amount']")
            inv_net_input_id = inv_net_input.get_attribute("id")
            
            # Use JavaScript to restore original Invoice Net value
            driver.execute_script(f"""
                document.getElementById('{inv_net_input_id}').value = '{original_inv_net}';
                const event = new Event('change', {{ bubbles: true }});
                document.getElementById('{inv_net_input_id}').dispatchEvent(event);
            """)
            logger.info(f"Restored Invoice Net value to {original_inv_net}")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Failed to restore Invoice Net value: {str(e)}")
            return {"success": False, "error": "Failed to restore Invoice Net value"}
        
        # Step 14: Check that background is still neutral
        logger.info("Step 14: Checking that background is still neutral")
        time.sleep(3)
        
        try:
            # Check for normal cell (neutral background)
            normal_cell = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(Page864Locators.TOTAL_CELL)
            )
            logger.info("Confirmed: Total cell still has neutral background as expected")
        except Exception as e:
            logger.error(f"Neutral background check failed: {str(e)}")
            return {"success": False, "error": "Failed to verify neutral background state"}
        
        # Restore original VAT value
        logger.info("Step 15: Restoring original VAT value")
        time.sleep(1)
        
        try:
            # Find VAT input field again to avoid stale reference
            vat_input = driver.find_element(By.CSS_SELECTOR, "input[name='invoice_vat_amount']")
            vat_input_id = vat_input.get_attribute("id")
            
            # Use JavaScript to restore original VAT value
            driver.execute_script(f"""
                document.getElementById('{vat_input_id}').value = '{original_vat}';
                const event = new Event('change', {{ bubbles: true }});
                document.getElementById('{vat_input_id}').dispatchEvent(event);
            """)
            logger.info(f"Restored VAT value to {original_vat}")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Failed to restore VAT value: {str(e)}")
            return {"success": False, "error": "Failed to restore VAT value"}
        
        logger.info("EU zone VAT validation test completed successfully")
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Unexpected error during test: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
        
    finally:
        release_driver(driver)

def main():
    test_results = {
        "de_zone": {"status": "Not Run", "error": None},
        "eu_zone": {"status": "Not Run", "error": None}
    }
    
    # Run the DE zone test
    result = test_de_zone_vat_validation()
    
    if not result.get("success", False):
        error_msg = result.get("error", "Unknown error")
        logger.error(f"DE zone test failed: {error_msg}")
        test_results["de_zone"] = {"status": "Failed", "error": error_msg}
    else:
        logger.info("DE zone test passed successfully")
        test_results["de_zone"] = {"status": "Passed", "error": None}
    
    # Run the EU zone test
    result = test_eu_zone_vat_validation()
    
    if not result.get("success", False):
        error_msg = result.get("error", "Unknown error")
        logger.error(f"EU zone test failed: {error_msg}")
        test_results["eu_zone"] = {"status": "Failed", "error": error_msg}
    else:
        logger.info("EU zone test passed successfully")
        test_results["eu_zone"] = {"status": "Passed", "error": None}
    
    # Print test summary
    logger.info("\n" + "="*50)
    logger.info("VAT VALIDATION TEST SUMMARY")
    logger.info("="*50)
    logger.info(f"DE Zone Test: {test_results['de_zone']['status']}")
    if test_results['de_zone']['error']:
        logger.info(f"  Error: {test_results['de_zone']['error']}")
    
    logger.info(f"EU Zone Test: {test_results['eu_zone']['status']}")
    if test_results['eu_zone']['error']:
        logger.info(f"  Error: {test_results['eu_zone']['error']}")
    logger.info("="*50)
    
    # Exit with error code if any test failed
    if test_results["de_zone"]["status"] == "Failed" or test_results["eu_zone"]["status"] == "Failed":
        sys.exit(1)  # Signal to Jenkins that the test failed

if __name__ == "__main__":
    main()