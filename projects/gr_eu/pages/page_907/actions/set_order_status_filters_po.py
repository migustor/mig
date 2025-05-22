"""
Executes JavaScript code to uncheck all PO statuses, 
then checks only 'waiting_for_pick_up' and 'waiting_for_arrival' 
in the #po_status_id_div multiselect, and finally closes the dropdown.
"""

import logging
import time
from selenium.common.exceptions import JavascriptException
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def set_order_status_filters_po(driver, timeouts=None):
    """
    Runs a JavaScript snippet to:
      1) Open the dropdown
      2) Uncheck all selected statuses
      3) Check specific statuses (waiting_for_pick_up, waiting_for_arrival)
      4) Close the dropdown

    Returns a dict indicating success or failure.
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info("Setting PO filter: 'Waiting for Pick-Up' and 'Waiting for Arrival'")

    # JavaScript code with step 4 added to close the dropdown
    js_code = r"""
    (function() {
      // Step 1: Open the dropdown
      document.querySelector('#po_status_id_div .multiselect.dropdown-toggle').click();
      
      // Step 2: Uncheck all selected statuses
      document.querySelectorAll('#po_status_id_div .multiselect-container li.active input[type="checkbox"]')
        .forEach(checkbox => checkbox.click());
    
      // Step 3: Check the required statuses
      ['waiting_for_pick_up', 'waiting_for_arrival'].forEach(value => {
        const checkbox = document.querySelector(`#po_status_id_div .multiselect-container input[value="${value}"]`);
        if (checkbox) {
          checkbox.click();
        }
      });
      
      // Step 4: Close the dropdown
      document.querySelector('#po_status_id_div .multiselect.dropdown-toggle').click();
    })();
    """

    try:
        driver.execute_script(js_code)
        logger.info("JavaScript executed for PO status filter")
        
        # Give some time for the page to update
        time.sleep(2)

        return {"success": True, "error": None}
    
    except JavascriptException as js_error:
        error_msg = f"JavaScript error: {str(js_error)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
