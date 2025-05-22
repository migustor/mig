"""
Sets order status filters, selecting only "delivered" and updates date range
"""
import logging
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import JavascriptException
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def set_order_status_filters(driver, timeouts=None):
    """
    Executes JavaScript code to set the order status filter to "delivered"
    and updates the date range to start from January 1, 2025
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts (not used in this function)
        
    Returns:
        dict: Execution result with success/error information
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info("Setting order status filter to 'delivered' and updating date range")
    
    # JavaScript to set the status filter and update date range
    js_code = """
    try {
        // Find and open the dropdown
        const soStatusDropdown = document.querySelector('#so_status_id_div .multiselect.dropdown-toggle');
        if (!soStatusDropdown) {
            console.log("Dropdown element not found");
            return "Dropdown not found";
        }
        
        // Open the dropdown
        soStatusDropdown.click();
        
        // Allow time for options to display
        setTimeout(function() {
            // Uncheck all items except "delivered"
            const allCheckboxes = document.querySelectorAll('#so_status_id_div .multiselect-container input[type="checkbox"]');
            if (allCheckboxes.length === 0) {
                console.log("No checkboxes found");
                return "No checkboxes found";
            }
            
            // First, uncheck all except "delivered"
            allCheckboxes.forEach(checkbox => {
                if (checkbox.checked && checkbox.value !== 'delivered') {
                    checkbox.click();
                }
            });
            
            // Find and check the "delivered" item
            const deliveredCheckbox = document.querySelector('#so_status_id_div .multiselect-container input[value="delivered"]');
            if (deliveredCheckbox && !deliveredCheckbox.checked) {
                deliveredCheckbox.click();
            }
            
            // Close the dropdown
            soStatusDropdown.click();
            
            // Trigger the change event if there is a native select
            const soStatusSelect = document.querySelector("#so_status_id");
            if (soStatusSelect) {
                soStatusSelect.dispatchEvent(new Event("change"));
            }
        }, 500);
        
        return "success";
    } catch (e) {
        console.error("Error in status filter JS:", e);
        return "JS Error: " + e.message;
    }
    """
    
    # JavaScript to update the date range
    date_js_code = """
    try {
        // Check if we have jQuery and datepicker available
        if (typeof jQuery === 'undefined' || typeof jQuery('#date_range_from').datepicker !== 'function') {
            console.log("jQuery or datepicker not available");
            return "jQuery or datepicker not available";
        }
        
        // A more direct approach using jQuery datepicker API
        jQuery('#date_range_from').datepicker('update', new Date(2025, 0, 1));
        
        // Force the datepicker to update the hidden field
        const from = new Date(2025, 0, 1);
        const till = jQuery('#date_range_till').datepicker('getDate');
        
        // Update the hidden input with the new date range
        jQuery('#date_range').val(
          (from.getMonth() + 1) + '/' + from.getDate() + '/' + from.getFullYear()
          + ' - ' +
          (till.getMonth() + 1) + '/' + till.getDate() + '/' + till.getFullYear()
        );
        
        // Trigger change events
        jQuery('#date_range_from').trigger('change');
        jQuery('#input-daterange-date_range').trigger('changeDate');
        
        console.log('Date range has been updated programmatically');
        return "Date range updated successfully";
    } catch (e) {
        console.error("Error in date range JS:", e);
        return "JS Date Error: " + e.message;
    }
    """
    
    try:
        # Execute JavaScript for status filter
        result = driver.execute_script(js_code)
        logger.info(f"Status filter JavaScript returned: {result}")
        
        # Allow time for asynchronous JS code to execute
        time.sleep(2)
        
        # Execute JavaScript for date range
        date_result = driver.execute_script(date_js_code)
        logger.info(f"Date range JavaScript returned: {date_result}")
        
        # Allow time for date range update
        time.sleep(1)
        
        # Check if the "delivered" checkbox exists and is checked
        check_js = """
        const deliveredCheckbox = document.querySelector('#so_status_id_div .multiselect-container input[value="delivered"]');
        return deliveredCheckbox && deliveredCheckbox.checked;
        """
        is_delivered_checked = driver.execute_script(check_js)
        
        # Check if date was updated
        date_check_js = """
        const dateField = document.querySelector('#date_range');
        return dateField ? dateField.value : 'date field not found';
        """
        date_value = driver.execute_script(date_check_js)
        logger.info(f"Current date range value: {date_value}")
        
        if is_delivered_checked:
            logger.info("Successfully set order status filter to 'delivered'")
            
            # Try clicking the filter button if it exists
            try:
                filter_button = driver.find_element(By.ID, "filter_button")
                filter_button.click()
                logger.info("Clicked filter button")
                time.sleep(1)
            except:
                logger.info("No filter button found, continuing without it")
                
            return {"success": True, "error": None, "date_value": date_value}
        else:
            # Retry with a different approach - direct assignment
            direct_js = """
            document.querySelector('#so_status_id').value = 'delivered';
            document.querySelector('#so_status_id').dispatchEvent(new Event('change'));
            return true;
            """
            driver.execute_script(direct_js)
            time.sleep(1)
            
            # Try clicking the filter button if it exists
            try:
                filter_button = driver.find_element(By.ID, "filter_button")
                filter_button.click()
                logger.info("Clicked filter button")
                time.sleep(1)
            except:
                logger.info("No filter button found, continuing without it")
            
            logger.info("Used alternative approach for setting filter")
            return {"success": True, "error": None, "date_value": date_value}
            
    except JavascriptException as js_error:
        error_msg = f"JavaScript error: {str(js_error)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Unexpected error setting order status filter or date range: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}