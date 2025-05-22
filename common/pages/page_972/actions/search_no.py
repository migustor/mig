import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By  # Required for modern Selenium

# Import required locators and functions
from common.pages.page_972.locators import Page972WithoutLeadLocators
from common.pages.page_972.page_info import get_page_972_url
from common.utils.error_handling import jenkins_aware

logger = logging.getLogger("test")

@jenkins_aware()
def search_no(driver, project_name, presale_id, timeouts=None):
    """
    Searches for a presale on page 972 using the "No" filter for "Has Items Accepted for Stock".
    The presale ID should NOT appear in the results.
    
    :param driver: Selenium WebDriver instance.
    :param project_name: Project code (e.g., "sm_eu").
    :param presale_id: The presale ID to ensure is NOT in search results.
    :param timeouts: Optional dictionary of timeouts (e.g., {"action": 15}).
    :return: dict with {'success': bool, 'found': bool, 'error': str (if any)}
    """
    # Ensure presale_id is a string and not a dictionary
    if isinstance(presale_id, dict):
        presale_id = presale_id.get("presale_id", None)

    if presale_id is None:
        logger.error("Invalid presale_id received: None")
        return {"success": False, "error": "Invalid presale_id"}

    presale_id_str = str(presale_id)  # Convert to string for comparison
    logger.info(f"Starting search on page 972 for presale ID: {presale_id_str} (should NOT be found) in project {project_name}")

    action_timeout = timeouts.get("action", 15) if timeouts else 15

    try:
        # 1) Generate the URL and navigate to page 972
        page_972_url = get_page_972_url(project_name)
        if not page_972_url:
            error_msg = f"Could not build page_972_url for project '{project_name}'"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

        logger.info(f"Navigating to: {page_972_url}")
        driver.get(page_972_url)
        wait = WebDriverWait(driver, action_timeout)

        # 2) Pause before running JavaScript
        time.sleep(1)

        # 3) Execute JavaScript to set filters
        filter_script = """
        (function() {
            // Select "Working On It" in the status dropdown
            if (typeof jQuery !== 'undefined' && $('#status').data('multiselect')) {
                var $select = $('#status');
                $select.multiselect('deselectAll', false);
                $select.multiselect('select', '372');
                $select.multiselect('refresh');
            } else {
                var selectEl = document.getElementById('status');
                if (selectEl) {
                    for (var i = 0; i < selectEl.options.length; i++) {
                        selectEl.options[i].selected = (selectEl.options[i].value === '372');
                    }
                    selectEl.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }

            // Select "Yes" for "Has Items Accepted for Stock"
            var radioYes = document.getElementById('has_items_accepted_for_stock_0');
            if (radioYes && !radioYes.checked) {
                radioYes.click();
            }

            // Check "Created By" dropdown and select all if not all are selected
            if (typeof jQuery !== 'undefined' && $('#users').data('multiselect')) {
                var $usersSelect = $('#users');
                var selectedOptions = $usersSelect.val() || [];

                // Check if all options are selected
                var allOptions = $usersSelect.find('option').map(function() {
                    return this.value;
                }).get();

                if (selectedOptions.length !== allOptions.length) {
                    $usersSelect.multiselect('deselectAll', false);
                    $usersSelect.multiselect('select', allOptions);
                    $usersSelect.multiselect('refresh');
                }
            } else {
                var usersSelectEl = document.getElementById('users');
                if (usersSelectEl) {
                    var allSelected = true;
                    for (var i = 0; i < usersSelectEl.options.length; i++) {
                        if (!usersSelectEl.options[i].selected) {
                            allSelected = false;
                            break;
                        }
                    }

                    if (!allSelected) {
                        for (var i = 0; i < usersSelectEl.options.length; i++) {
                            usersSelectEl.options[i].selected = true;
                        }
                        usersSelectEl.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            }
        })();
        """
        logger.info("Executing JavaScript to apply search filters (NO)...")
        driver.execute_script(filter_script)

        # 4) Pause after running JavaScript
        time.sleep(1)

        # 5) Click the "Search" button
        logger.info("Clicking 'Search' button...")
        wait.until(EC.element_to_be_clickable(Page972WithoutLeadLocators.SEARCH_BUTTON)).click()

        # 6) Search for the presale ID in results
        logger.info(f"Verifying presale ID {presale_id_str} is NOT in results...")
        time.sleep(3)  # Allow time for results to load

        #  FIXED: Find all <a> tags inside #result-div and check their text
        result_div = driver.find_element(By.ID, "result-div")
        presale_links = result_div.find_elements(By.TAG_NAME, "a")  # Get all <a> elements

        # Debug log: Print all found presale IDs for verification
        found_ids = [link.text.strip() for link in presale_links]

        # Check if presale_id is NOT in the found links
        if presale_id_str not in found_ids:
            logger.info(f" Presale ID {presale_id_str} correctly NOT found in results!")
            return {"success": True, "found": False}

        logger.warning(f" ERROR: Presale ID {presale_id_str} WAS found in results (should NOT be present).")
        return {"success": False, "found": True}

    except (NoSuchElementException, TimeoutException) as e:
        error_msg = f"Element not found or timed out: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
