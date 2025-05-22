# common/pages/page_696/actions/configure_columns.py
"""
Модуль для настройки колонок документа в процессе загрузки файла на странице 696.
"""
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Импортируем локаторы для страницы 696
from common.pages.page_696.locators import Page696Locators

# Dictionary mapping column names to their expected option text
COLUMN_TYPES = {
    "upc_ean": ["UPC/EAN", "UPC", "EAN"],
    "description": ["Description", "Desc", "Product Description"],
    "quantity": ["Quantity", "Qty", "Amount"],
    "qty_per_pallet": ["Qty per Pallet", "Pallet Qty", "Pallet Quantity", "Items per Pallet"]
}

def configure_document_columns(driver, project_code=None, upload_timeout=10):
    """
    Настраивает колонки загруженного документа, проходит все этапы обработки и возвращается на страницу лида.
    
    Args:
        driver: Selenium WebDriver
        project_code: Code of the current project (optional)
        upload_timeout: Таймаут ожидания элементов
        
    Returns:
        dict: Результат настройки {'success': bool, 'error': str или None, 'step': str или None}
    """
    logger = logging.getLogger('test')
    logger.info("Configuring document columns and processing all steps on page 696")
    
    try:
        # Function to check if dropdown already has the correct option text and set it if needed
        def configure_dropdown_by_text(locator, option_texts, column_name):
            dropdown = WebDriverWait(driver, upload_timeout).until(
                EC.presence_of_element_located(locator)
            )
            select = Select(dropdown)
            
            # Get all available options
            options = select.options
            option_texts_lower = [text.lower() for text in option_texts]
            
            # Get the currently selected option text
            current_text = select.first_selected_option.text.strip()
            current_text_lower = current_text.lower()
            
            # Check if current selection is one of our target texts
            if current_text_lower in option_texts_lower:
                logger.info(f"{column_name} is already set to '{current_text}', skipping")
                return True
                
            # Find the first matching option
            option_found = False
            for option in options:
                option_text = option.text.strip()
                if option_text.lower() in option_texts_lower:
                    logger.info(f"Setting {column_name} to '{option_text}'")
                    select.select_by_visible_text(option_text)
                    time.sleep(0.5)
                    option_found = True
                    break
            
            if not option_found:
                # If no exact match, log all available options for debugging
                available_options = [o.text for o in options]
                logger.warning(f"Could not find any of {option_texts} for {column_name}. Available options: {available_options}")
                
                # Fall back to index-based selection for most common columns
                if "Column 1" in column_name:
                    logger.info(f"Falling back to selecting first option for {column_name}")
                    select.select_by_index(1)  # Often the first real option (after "Skip")
                    return True
                elif "Column 2" in column_name:
                    logger.info(f"Falling back to selecting second option for {column_name}")
                    select.select_by_index(2)  # Often the description
                    return True
                elif "Column 3" in column_name:
                    logger.info(f"Falling back to selecting quantity-like option for {column_name}")
                    # Try to find quantity in the available options
                    for i, opt_text in enumerate(available_options):
                        if "qty" in opt_text.lower() or "quant" in opt_text.lower() or "amount" in opt_text.lower():
                            select.select_by_index(i)
                            return True
                    # If still not found, select the third option
                    select.select_by_index(3)
                    return True
                elif "Column 4" in column_name:
                    logger.info(f"Falling back to selecting pallet-like option for {column_name}")
                    # Try to find pallet in the available options
                    for i, opt_text in enumerate(available_options):
                        if "pallet" in opt_text.lower():
                            select.select_by_index(i)
                            return True
                    # If still not found, select the fourth option
                    if len(options) > 4:
                        select.select_by_index(4)
                    else:
                        # If not enough options, select the last option
                        select.select_by_index(len(options) - 1)
                    return True
                
            return option_found
            
        # Step 1: Configure column 1 as UPC/EAN
        logger.info("Step 1: Checking/Setting column 1 to UPC/EAN")
        configure_dropdown_by_text(Page696Locators.COLUMN_1_DROPDOWN, COLUMN_TYPES["upc_ean"], "Column 1")
        
        # Step 2: Configure column 2 as Description
        logger.info("Step 2: Checking/Setting column 2 to Description")
        configure_dropdown_by_text(Page696Locators.COLUMN_2_DROPDOWN, COLUMN_TYPES["description"], "Column 2")
        
        # Step 3: Configure column 3 as Quantity
        logger.info("Step 3: Checking/Setting column 3 to Quantity")
        configure_dropdown_by_text(Page696Locators.COLUMN_3_DROPDOWN, COLUMN_TYPES["quantity"], "Column 3")
        
        # Step 4: Configure column 4 as Qty per Pallet
        logger.info("Step 4: Checking/Setting column 4 to Qty per Pallet")
        configure_dropdown_by_text(Page696Locators.COLUMN_4_DROPDOWN, COLUMN_TYPES["qty_per_pallet"], "Column 4")
        
        # Step 5: Click the Save Configuration button
        logger.info("Step 5: Clicking the Save Configuration button")
        save_button = WebDriverWait(driver, upload_timeout).until(
            EC.element_to_be_clickable(Page696Locators.SAVE_CONFIG_BUTTON)
        )
        
        # Scroll to the button to ensure it's visible
        driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
        time.sleep(0.5)
        
        save_button.click()
        
        # Wait for the page to process after save
        time.sleep(3)
        
        # NEW STEPS: Process through all the remaining steps
        
        # Step 6: Click "Save Quantities and Mark Incorrect Ones..." button
        logger.info("Step 6: Clicking Save Quantities button to proceed to next step")
        save_quantities_btn = WebDriverWait(driver, upload_timeout).until(
            EC.element_to_be_clickable(Page696Locators.SAVE_QUANTITIES_BUTTON)
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", save_quantities_btn)
        save_quantities_btn.click()
        time.sleep(2)
        
        # Step 7: Check if SKIP_STEP_3_BUTTON exists, if not - skip to Step 8
        try:
            logger.info("Step 7: Checking if 'No items found, skip this step' button for step 3 exists")
            skip_btn1 = WebDriverWait(driver, 3).until(  # Shorter timeout for element existence check
                EC.presence_of_element_located(Page696Locators.SKIP_STEP_3_BUTTON)
            )
            # If element exists, click it
            logger.info("Step 7: Clicking first 'No items found, skip this step' button")
            driver.execute_script("arguments[0].scrollIntoView(true);", skip_btn1)
            skip_btn1.click()
            time.sleep(2)
        except TimeoutException:
            logger.info("Step 7: 'No items found, skip this step' button for step 3 not found, proceeding to next step")
            # Skip to the next step without clicking
        
        # Step 8: Click "No items found, skip this step" (second skip)
        logger.info("Step 8: Clicking 'No items found, skip this step' button for step 4")
        try:
            skip_btn2 = WebDriverWait(driver, upload_timeout).until(
                EC.element_to_be_clickable(Page696Locators.SKIP_STEP_4_BUTTON)
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", skip_btn2)
            skip_btn2.click()
            time.sleep(2)
        except TimeoutException:
            logger.warning("Skip button for step 4 not found, attempting to continue anyway")
        
        # Step 9: Click "Add processed items to the lead"
        logger.info("Step 9: Clicking 'Add processed items to the lead' button")
        add_processed_btn = WebDriverWait(driver, upload_timeout).until(
            EC.element_to_be_clickable(Page696Locators.ADD_PROCESSED_ITEMS_BUTTON)
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", add_processed_btn)
        add_processed_btn.click()
        time.sleep(3)
        
        # Step 10: Click "Back to Lead Editor"
        logger.info("Step 10: Clicking 'Back to Lead Editor' button")
        back_btn = WebDriverWait(driver, upload_timeout).until(
            EC.element_to_be_clickable(Page696Locators.BACK_TO_LEAD_EDITOR_BUTTON)
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", back_btn)
        back_btn.click()
        time.sleep(3)
        
        logger.info("Successfully configured and processed all document import steps")
        return {"success": True, "error": None, "step": "document_import_completed"}
            
    except TimeoutException as te:
        error_msg = f"Timeout occurred during document processing: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "step": "document_processing_timeout"}
        
    except NoSuchElementException as nse:
        error_msg = f"Element not found during document processing: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "step": "document_processing_element_not_found"}
        
    except Exception as e:
        error_msg = f"Unexpected error during document processing: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "step": "document_processing_error"}