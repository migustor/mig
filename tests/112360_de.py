"""
Test for VAT validation in German zone
"""
import logging
import time
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(" - MAIN TEST - ")

@jenkins_aware()
def test_de_zone_vat_validation():
    """
    Test for VAT validation in German zone
    """
    driver = setup_chrome_driver(headless=False)
    
    # Test parameters
    project_name = "sm_eu"
    document_id = 58435
    
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
        # You can keep it if you want to double-check that it remains neutral
        
        logger.info("Test completed successfully")
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Unexpected error during test: {str(e)}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
        
    finally:
        release_driver(driver)
        
def main():
    result = test_de_zone_vat_validation()
    
    if not result.get("success", False):
        logger.error(f"Test failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)  # Signal to Jenkins that the test failed
    else:
        logger.info("Test passed successfully")

if __name__ == "__main__":
    main()