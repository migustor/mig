import os
import time
import logging
import re
import sys  # <-- Step 1: Import sys here
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# For Sovamax
SOVAMAX_USERNAME = "victor.moisei@mteam.md"
SOVAMAX_PASSWORD = "12"

# For other systems
DEFAULT_USERNAME = os.getenv('DEFAULT_USERNAME')
DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD')

def main():
    # List of systems with their respective login and notification URLs
    systems = [
        {
            'name': 'Sovamax',
            'login_url': 'https://stage15.office.sovasystem.com/sage/index.cfm?page_id=442',
            'notifications_url': 'https://stage15.office.sovasystem.com/sage/index.cfm?page_id=939'
        },
        {
            'name': 'RA',
            'login_url': 'https://stage15.office.ratrading.eu/sage/index.cfm?page_id=442',
            'notifications_url': 'https://stage15.office.ratrading.eu/sage/index.cfm?page_id=939'
        },
        {
            'name': 'Atlas',
            'login_url': 'https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=442',
            'notifications_url': 'https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=939'
        },
        {
            'name': 'Eminia',
            'login_url': 'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=442',
            'notifications_url': 'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=939'
        },
        {
            'name': 'Lanius',
            'login_url': 'https://stage15.office.laniustoys.com/sage/index.cfm?page_id=442',
            'notifications_url': 'https://stage15.office.laniustoys.com/sage/index.cfm?page_id=939'
        },
        {
            'name': 'DbReactor',
            'login_url': 'https://stage15.office.dbreactor.com/sage/index.cfm?page_id=442',
            'notifications_url': 'https://stage15.office.dbreactor.com/sage/index.cfm?page_id=939'
        },
        {
            'name': 'Horus',
            'login_url': 'https://stage15.office.horustrading.eu/sage/index.cfm?page_id=442',
            'notifications_url': 'https://stage15.office.horustrading.eu/sage/index.cfm?page_id=939'
        },
        {
            'name': 'ARO',
            'login_url': 'https://stage15.office.arotrading.eu/sage/index.cfm?page_id=442',
            'notifications_url': 'https://stage15.office.arotrading.eu/sage/index.cfm?page_id=939'
        },
        {
            'name': 'SovamaxUSA',
            'login_url': 'https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=442',
            'notifications_url': 'https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=939'
        },
    ]

    # Initialize test results list
    test_results = []

    # Set up the Selenium WebDriver (assuming using Chrome)
    options = Options()
    options.add_argument('--start-maximized')
    # Optional: Run Chrome in headless mode
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    # For each system, perform the test
    for system in systems:
        try:
            logging.info(f"--- Starting test for {system['name']} ---")

            # Navigate to the login page
            logging.info(f"Navigating to login page: {system['login_url']}")
            driver.get(system['login_url'])

            # Wait for the login fields to be present
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.NAME, 'login_name')))

            # Determine the username and password based on the system
            if system['name'] == 'Sovamax':
                username = SOVAMAX_USERNAME
                password = SOVAMAX_PASSWORD
            else:
                username = DEFAULT_USERNAME
                password = DEFAULT_PASSWORD

            # Enter username and password
            logging.info("Entering login credentials.")
            login_field = driver.find_element(By.NAME, 'login_name')
            login_field.clear()
            login_field.send_keys(username)
            password_field = driver.find_element(By.NAME, 'password')
            password_field.clear()
            password_field.send_keys(password)

            # Click the submit button
            logging.info("Clicking the submit button.")
            submit_button = driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Submit")]')
            submit_button.click()

            # Wait for the page to load after login
            logging.info("Waiting for page to load after login.")
            wait.until(EC.presence_of_element_located((By.ID, 'notification-bar')))
            time.sleep(5)  # Additional wait to ensure full page load

            # Get the number of notifications
            logging.info("Getting the initial number of notifications.")
            notification_bell = driver.find_element(By.ID, 'notification_bell')
            notification_count = notification_bell.get_attribute('data-count')
            if notification_count and notification_count.isdigit():
                initial_notification_count = int(notification_count)
                logging.info(f"Initial number of notifications: {initial_notification_count}")
            else:
                logging.info("No notifications found or data-count attribute is invalid.")
                initial_notification_count = 0

            # Remember the initial notification count
            remembered_initial_count = initial_notification_count

            # Proceed to close one notification if there are any
            if initial_notification_count > 0:
                logging.info("Closing one notification.")
                # Click on the notification bell to open notifications
                notification_bell.click()
                time.sleep(2)  # Wait for the notifications to open

                try:
                    # Find the close button for the first notification
                    close_button = driver.find_element(By.CLASS_NAME, 'modalMessageClose')
                    driver.execute_script("arguments[0].click();", close_button)
                    time.sleep(1)  # Wait a bit after clicking
                    logging.info("One notification closed.")
                except Exception as e:
                    logging.error(f"Could not close the notification: {e}")
                    # Even if closing fails, proceed to get the updated count

                # Close the notifications panel
                notification_bell.click()
                time.sleep(1)

                # After closing one notification, get the updated notification count
                logging.info("Getting updated number of notifications.")
                try:
                    notification_bell = driver.find_element(By.ID, 'notification_bell')
                    updated_notification_count = notification_bell.get_attribute('data-count')
                    if updated_notification_count and updated_notification_count.isdigit():
                        updated_notification_count = int(updated_notification_count)
                        logging.info(f"Updated number of notifications: {updated_notification_count}")
                    else:
                        updated_notification_count = 0
                        logging.info("No notifications left.")
                except Exception as e:
                    logging.error(f"Could not retrieve updated notification count: {e}")
                    updated_notification_count = 0
            else:
                logging.info("No notifications to close.")
                updated_notification_count = initial_notification_count

            # Remember the updated notification count
            remembered_number = updated_notification_count

            # Navigate to the notifications report page
            logging.info(f"Navigating to the notifications report page: {system['notifications_url']}")
            driver.get(system['notifications_url'])

            # Wait for the date range input to be present
            try:
                # Wait for the element with name 'date_from'
                wait.until(EC.presence_of_element_located((By.NAME, 'date_from')))
            except TimeoutException:
                logging.error("Element with name 'date_from' not found.")
                # Optionally, save the page source and screenshot for debugging
                page_source = driver.page_source
                with open(f"{system['name']}_page_source.html", 'w', encoding='utf-8') as f:
                    f.write(page_source)
                logging.info(f"Page source saved to '{system['name']}_page_source.html'.")
                driver.save_screenshot(f"{system['name']}_page_screenshot.png")
                logging.info(f"Screenshot saved to '{system['name']}_page_screenshot.png'.")
                # Record the failure
                test_results.append({'name': system['name'], 'status': 'Failed', 'reason': 'Date range input not found'})
                continue  # Move to the next system

            # Use JavaScript to set the date range
            try:
                logging.info("Setting date range using JavaScript.")
                js_code = """
                (function() {
                // Get the current date
                var currentDate = new Date();

                // Get current year and subtract 1
                var year = currentDate.getFullYear() - 1;

                // Construct the date string in "01-Jan-YYYY" format
                    var dateString = "01-Jan-" + year;

                   // Set the value of the input field
                    var dateInput = document.getElementsByName('date_from')[0];
                    dateInput.value = dateString;

                    // Create a date object for the datepicker
                    var dateObj = new Date(year, 0, 1); // month is zero-based, 0 = January

                    // Update the datepicker's internal date value if jQuery and datepicker are available
                    if (window.jQuery && jQuery().datepicker) {
                        jQuery(dateInput).datepicker('setDate', dateObj);

                        // Trigger the changeDate event to ensure all linked elements update
                        jQuery(dateInput).trigger('changeDate');
                    }
                })();
                """
                driver.execute_script(js_code)
            except Exception as e:
                logging.error(f"An error occurred while executing the JavaScript code: {e}")
                # Optionally, save the page source and screenshot for debugging
                page_source = driver.page_source
                with open(f"{system['name']}_js_error_page_source.html", 'w', encoding='utf-8') as f:
                    f.write(page_source)
                logging.info(f"Page source saved to '{system['name']}_js_error_page_source.html'.")
                driver.save_screenshot(f"{system['name']}_js_error_screenshot.png")
                logging.info(f"Screenshot saved to '{system['name']}_js_error_screenshot.png'.")
                # Record the failure
                test_results.append({'name': system['name'], 'status': 'Failed', 'reason': 'JavaScript execution error'})
                continue  # Move to the next system

            time.sleep(2)

            # Click on the 'Search' button
            logging.info("Clicking on the 'Search' button.")
            try:
                search_button = driver.find_element(By.XPATH, '//a[@id="search"]')
                driver.execute_script("arguments[0].click();", search_button)
            except NoSuchElementException:
                logging.error("Search button not found.")
                # Optionally, save the page source and screenshot for debugging
                page_source = driver.page_source
                with open(f"{system['name']}_search_error_page_source.html", 'w', encoding='utf-8') as f:
                    f.write(page_source)
                logging.info(f"Page source saved to '{system['name']}_search_error_page_source.html'.")
                driver.save_screenshot(f"{system['name']}_search_error_screenshot.png")
                logging.info(f"Screenshot saved to '{system['name']}_search_error_screenshot.png'.")
                # Record the failure
                test_results.append({'name': system['name'], 'status': 'Failed', 'reason': 'Search button not found'})
                continue  # Move to the next system

            # Wait for the results to load
            logging.info("Waiting for the results to load.")
            time.sleep(5)  # Adjust as necessary based on page load time

            # Search for the text "Notifications report tool (" and extract the number
            logging.info('Searching for the text "Notifications report tool (" on the page.')
            page_source = driver.page_source

            # Use regex to find the number after "Notifications report tool ("
            match = re.search(r'Notifications report tool \((\d+)\)', page_source)
            if match:
                report_notifications = int(match.group(1))
                logging.info(f"Number of notifications in report: {report_notifications}")
            else:
                # Check if 'No results' message is present
                logging.info("Checking for 'No results' message.")
                no_results_elements = driver.find_elements(By.CSS_SELECTOR, 'p.panel-body.bg-info')
                if no_results_elements:
                    no_results_text = no_results_elements[0].text.strip()
                    if no_results_text == 'No results':
                        logging.info("No results found. Number of notifications in report: 0")
                        report_notifications = 0
                    else:
                        logging.warning(f"Unexpected message: '{no_results_text}'")
                        report_notifications = None
                else:
                    logging.error("Could not find 'Notifications report tool (' with a number following it on the page.")
                    report_notifications = None

            if report_notifications is None:
                logging.error("Could not determine the number of notifications in the report.")
                # Record the failure
                test_results.append({'name': system['name'], 'status': 'Failed', 'reason': 'Notification count extraction failed'})
                continue  # Skip to the next system

            # Expected number of notifications after closing one
            expected_notifications = remembered_initial_count - 1 if remembered_initial_count > 0 else 0

            # Compare the remembered number to the report number
            if remembered_number == expected_notifications == report_notifications:
                logging.info(f"Test Passed for {system['name']}: The number of notifications matches after closing one notification.")
                test_results.append({'name': system['name'], 'status': 'Passed'})
            else:
                logging.info(f"Test Failed for {system['name']}: The number of notifications does not match.")
                logging.info(f"Remembered number: {remembered_number}, Expected number: {expected_notifications}, Reported number: {report_notifications}")
                test_results.append({
                    'name': system['name'],
                    'status': 'Failed',
                    'reason': 'Notification count mismatch',
                    'details': f"Remembered: {remembered_number}, Expected: {expected_notifications}, Reported: {report_notifications}"
                })

            # Clear cookies to ensure clean session for next system
            logging.info("Clearing cookies for next system.")
            driver.delete_all_cookies()

        except Exception as e:
            logging.error(f"An error occurred while testing {system['name']}: {e}")
            test_results.append({'name': system['name'], 'status': 'Failed', 'reason': str(e)})

    # Close the browser after all systems have been tested
    logging.info("Closing the browser.")
    driver.quit()

    # Generate Test Summary
    logging.info("--- Test Summary ---")
    passed_systems = [result['name'] for result in test_results if result['status'] == 'Passed']
    failed_systems = [result for result in test_results if result['status'] == 'Failed']

    if len(passed_systems) == len(systems):
        logging.info("ALL SYSTEMS PASSED THE TEST.")
    else:
        if passed_systems:
            logging.info(f"PASSED SYSTEMS ({len(passed_systems)}): {', '.join(passed_systems)}")
        if failed_systems:
            logging.info(f"FAILED SYSTEMS ({len(failed_systems)}):")
            for failure in failed_systems:
                reason = failure.get('reason', 'No reason provided')
                details = failure.get('details', '')
                logging.info(f" - {failure['name']}: {reason}")
                if details:
                    logging.info(f"   Details: {details}")

    # Step 2 & 3: If any system fails, return exit code 1
    if failed_systems:
        sys.exit(1)

if __name__ == '__main__':
    main()
