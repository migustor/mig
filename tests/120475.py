from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, JavascriptException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import sys

class DropdownTest:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.logs = []
        self.dropdown_options = [
            ("1", "Order Date", False),        # No future dates allowed
            ("2", "Request Date", False),      # No future dates allowed
            ("6", "Est. Pickup Date", True),   # Future dates allowed
            ("3", "Est. Delivery Date", True), # Future dates allowed
            ("5", "Launched Date", False)      # No future dates allowed
        ]

    def parse_end_date(self, date_range_value):
        if not date_range_value:
            return None
        try:
            end_date_str = date_range_value.split(" - ")[1].strip()
            return datetime.strptime(end_date_str, "%m/%d/%Y")
        except (IndexError, ValueError):
            return None

    def select_option(self, option_id, option_name):
        js_dropdown_script = f"""
        var done = arguments[arguments.length - 1];
        (function selectOption() {{
            try {{
                // First, ensure any existing dropdowns are closed
                const existingDropdowns = document.querySelectorAll('.multiselect-container.dropdown-menu.show');
                existingDropdowns.forEach(dropdown => {{
                    dropdown.classList.remove('show');
                }});

                const dropdownButton = document.querySelector('.multiselect.dropdown-toggle');
                if (!dropdownButton) {{
                    done('Dropdown button not found.');
                    return;
                }}

                // Force dropdown to show
                dropdownButton.click();
                
                setTimeout(() => {{
                    const option = document.querySelector('.multiselect-container input[type="radio"][value="{option_id}"]');
                    if (!option) {{
                        done("Option with ID {option_id} not found.");
                        return;
                    }}

                    // Set checked state and dispatch multiple events
                    option.checked = true;
                    
                    // Create and dispatch events
                    ['change', 'input', 'click'].forEach(eventType => {{
                        const event = new Event(eventType, {{ bubbles: true, cancelable: true }});
                        option.dispatchEvent(event);
                    }});

                    // Close dropdown after a short delay
                    setTimeout(() => {{
                        dropdownButton.click();
                        
                        // Final verification
                        setTimeout(() => {{
                            const isStillSelected = option.checked;
                            done(isStillSelected ? 
                                `Option {option_id} ({option_name}) selected successfully.` : 
                                `Selection failed to stick for option {option_id}`);
                        }}, 200);
                    }}, 200);
                }}, 200);

            }} catch (error) {{
                done(`Dropdown JavaScript Error: ${{error.message}}`);
            }}
        }})();
        """
        try:
            result = self.driver.execute_async_script(js_dropdown_script)
            print(f"Debug: {result}")
            
            # Add a verification step after the async operation
            verify_script = f"""
            return document.querySelector('.multiselect-container input[type="radio"][value="{option_id}"]').checked;
            """
            time.sleep(1)  # Short wait before verification
            is_selected = self.driver.execute_script(verify_script)
            
            if not is_selected:
                print(f"Warning: Selection verification failed for option {option_id}")
                self.logs.append(f"Selection verification failed for option {option_id}")
                return False
            return True
                
        except JavascriptException as e:
            print(f"Dropdown JavaScript execution - Test Failed: {e}")
            self.logs.append(f"Dropdown JavaScript execution - Test Failed: {e}")
            return False

    def set_date(self, old_input_till_value):
        js_revert_script = f"""
        (function revertDate() {{
            try {{
                const $inputTill = jQuery('#date_range_till');
                if (!$inputTill.length) {{
                    return 'Element not found.';
                }}

                const originalDate = '{old_input_till_value}';
                console.log("Reverting date to original:", originalDate);
                console.log("Before revert, input value:", $inputTill.val());
                $inputTill.datepicker('setDate', originalDate);
                $inputTill.datepicker('update');
                $inputTill.trigger('changeDate');
                console.log("After revert, input value:", $inputTill.val());
                return "Reverted to original date.";
            }} catch (error) {{
                return `Calendar JavaScript Error: ${{error.message}}`;
            }}
        }})();
        """
        try:
            revert_result = self.driver.execute_script(js_revert_script)
            print(f"Debug (Revert): {revert_result}")
            time.sleep(3)
        except JavascriptException as e:
            print(f"Calendar revert execution - Test Failed: {e}")
            self.logs.append(f"Calendar revert execution - Test Failed: {e}")

    def check_future_date_allowed(self):
        js_calendar_script = r"""
        (function checkAndSetNextYear() {
            try {
                const $inputTill = jQuery('#date_range_till');
                if (!$inputTill.length) {
                    return 'Element not found.';
                }

                const currentValue = $inputTill.val();
                console.log("Current #date_range_till value before setting future date:", currentValue);

                const datePattern = /^(\d{2})-([A-Za-z]{3})-(\d{4})$/;
                const match = currentValue.match(datePattern);

                if (!match) {
                    console.log("Date format not recognized for currentValue:", currentValue);
                    return 'Date format not recognized.';
                }

                const day = match[1];
                const month = match[2];
                const year = match[3];
                const currentYear = parseInt(year, 10);
                const nextYear = currentYear + 1;
                const newDateStr = `${day}-${month}-${nextYear}`;

                console.log("Attempting to set future date:", newDateStr);

                const newDateMoment = moment.utc(newDateStr, 'DD-MMM-YYYY');
                if (!newDateMoment.isValid()) {
                    console.log("New date is invalid:", newDateStr);
                    return 'New date is invalid.';
                }

                $inputTill.datepicker('setDate', newDateMoment.toDate());
                $inputTill.datepicker('update');
                $inputTill.trigger('changeDate');

                console.log("After setting future date, input value:", $inputTill.val());

                return newDateStr;
            } catch (error) {
                return `Calendar JavaScript Error: ${error.message}`;
            }
        })();
        """
        try:
            self.driver.execute_script(js_calendar_script)
            time.sleep(3)
            new_date_range_value = self.driver.find_element(By.ID, 'date_range').get_attribute('value')
            return self.parse_end_date(new_date_range_value)
        except JavascriptException as e:
            print(f"Calendar JavaScript execution - Test Failed: {e}")
            self.logs.append(f"Calendar JavaScript execution - Test Failed: {e}")
            return None

    def apply_changes_and_wait_for_element(self):
        self.driver.find_element(By.ID, "build_report").click()
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h4.text-uppercase.text-danger.xmb25, div.alert.alert-info'))
            )
            print("Found either 'Purchase Orders found' or 'No results found' element after changes.")
            return True
        except TimeoutException:
            print("Timed out waiting for the results element.")
            return False

    def login(self):
        self.driver.get("https://stage15.office.grafit.md/sage/?logout")
        try:
            login_name_element = self.driver.find_element(By.ID, "login_name")
            login_name_element.send_keys("victor.moisei@mteam.md")
            print("Login name input - Test Passed")
            self.logs.append("Login name input - Test Passed")

            password_element = self.driver.find_element(By.ID, "password")
            password_element.send_keys("12")
            password_element.send_keys(Keys.RETURN)
            print("Password input - Test Passed")
            self.logs.append("Password input - Test Passed")
            return True
        except NoSuchElementException:
            print("Login or password input - Test Failed")
            self.logs.append("Login or password input - Test Failed")
            return False

    def run_tests(self):
        try:
            # Step 1: Login
            if not self.login():
                return False

            # Step 2: Navigate after login
            time.sleep(3)
            self.driver.get("https://stage15.office.grafit.md/sage/index.cfm?page_id=907&order_type=po")

            option_index = 1
            for (option_id, option_name, expected_future) in self.dropdown_options:
                if not self.select_option(option_id, option_name):
                    result = f"Option {option_index} ({option_name}) - FAILED (could not select option)"
                    self.logs.append(result)
                    print(result)
                    self.driver.refresh()
                    option_index += 1
                    continue

                time.sleep(2)

                old_input_till_value = self.driver.find_element(By.ID, 'date_range_till').get_attribute('value')
                old_date_range_value = self.driver.find_element(By.ID, 'date_range').get_attribute('value')
                old_end_date = self.parse_end_date(old_date_range_value)
                
                if not old_end_date:
                    result = f"Option {option_index} ({option_name}) - FAILED (invalid original date)"
                    self.logs.append(result)
                    print(result)
                    if option_id == "6":
                        time.sleep(2)
                    self.driver.refresh()
                    option_index += 1
                    continue

                new_end_date = self.check_future_date_allowed()

                # Determine PASS/FAIL
                if not new_end_date:
                    if expected_future:
                        result = f"Option {option_index} ({option_name}) - FAILED (future dates not allowed)"
                    else:
                        result = f"Option {option_index} ({option_name}) - PASSED (future dates blocked)"
                else:
                    moved_forward = (new_end_date.year == old_end_date.year + 1 and
                                  new_end_date.month == old_end_date.month and
                                  new_end_date.day == old_end_date.day)

                    if expected_future and moved_forward:
                        result = f"Option {option_index} ({option_name}) - PASSED (future dates allowed)"
                    elif expected_future and not moved_forward:
                        result = f"Option {option_index} ({option_name}) - FAILED (future dates not allowed)"
                    elif not expected_future and moved_forward:
                        result = f"Option {option_index} ({option_name}) - FAILED (future dates allowed)"
                    else:
                        result = f"Option {option_index} ({option_name}) - PASSED (future dates blocked)"

                self.logs.append(result)
                print(result)

                if "PASSED" in result:
                    if "blocked" in result:
                        self.set_date(old_input_till_value)

                    success = self.apply_changes_and_wait_for_element()
                    if success:
                        self.logs.append("Report was built successfully")
                    else:
                        self.logs.append("No report result found")

                if option_id == "6":
                    time.sleep(0.1)

                self.driver.refresh()
                option_index += 1

            return True

        finally:
            self.print_summary()

    def print_summary(self):
        print("\n--- Test Summary ---")
        for log in self.logs:
            print(log)

        if any("FAILED" in line for line in self.logs):
            print("One or more tests have failed.")
            return False
        else:
            print("All tests passed successfully.")
            return True

    def cleanup(self):
        if self.driver:
            self.driver.quit()

def main():
    test = DropdownTest()
    try:
        success = test.run_tests()
        sys.exit(0 if success else 1)
    finally:
        test.cleanup()

if __name__ == "__main__":
    main()