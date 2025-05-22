import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse, parse_qs
import re

# Configure logging to include the time, level, and message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

test_results = []

# Set up the WebDriver (Ensure the appropriate driver is installed and in PATH)
driver = webdriver.Chrome()  # Or webdriver.Firefox(), etc.
driver.maximize_window()
wait = WebDriverWait(driver, 30)  # Increased wait time for better reliability

# Function to check if the page has login fields
def is_logged_in(driver):
    try:
        driver.find_element(By.ID, 'login_name')
        return False  # Login field found, not logged in
    except:
        return True  # Login field not found, logged in

# Function to extract PO ID from PO Editor page
def extract_po_id(driver):
    try:
        title_element = driver.find_element(By.ID, 'title_page_name')
        title_text = title_element.text.strip()
        logging.info(f'Page title: {title_text}')
        # Extract PO ID using regex
        match = re.search(r'PO Editor\. PO:\s*(\d+)', title_text)
        if match:
            po_id = match.group(1)
            logging.info(f'Extracted PO ID: {po_id}')
            return po_id
        else:
            logging.error('Could not extract PO ID from page title.')
            return None
    except Exception as e:
        logging.error(f'Error extracting PO ID: {e}')
        return None

# Define the systems and their details
systems = [
    {
        'name': 'Sovamax',
        'login_url': 'https://stage15.office.sovasystem.com/sage/',
        'username': 'victor.moisei@mteam.md',
        'password': '12',  # Replace with your actual password
        'po_editor_urls': [
            'https://stage15.office.sovasystem.com/sage/index.cfm?page_id=839&po_id=228438',
            'https://stage15.office.sovasystem.com/sage/index.cfm?page_id=839&po_id=228437'
        ]
    },
    {
        'name': 'RA',
        'login_url': 'https://stage15.office.ratrading.eu/sage/index.cfm?page_id=830&company_id=516488',
        'username': 'victor.moisei@mteam.md',
        'password': '12',  # Replace with your actual password
        'po_editor_urls': [
            'https://stage15.office.ratrading.eu/sage/index.cfm?page_id=839&po_id=44444',
            'https://stage15.office.ratrading.eu/sage/index.cfm?page_id=839&po_id=44443'
        ]
    },
    {
        'name': 'Eminia',
        'login_url': 'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=830&company_id=410568',
        'username': 'victor.moisei@mteam.md',
        'password': '12',  # Replace with your actual password
        'po_editor_urls': [
            'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=839&po_id=132520',
            'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=839&po_id=132519'
        ]
    },
    {
        'name': 'Lanius',
        'login_url': 'https://stage15.office.laniustoys.com/sage/index.cfm?page_id=830&company_id=161169',
        'username': 'victor.moisei@mteam.md',
        'password': '12',  # Replace with your actual password
        'po_editor_urls': [
            'https://stage15.office.laniustoys.com/sage/index.cfm?page_id=839&po_id=41620',
            'https://stage15.office.laniustoys.com/sage/index.cfm?page_id=839&po_id=41619'
        ]
    },
    {
        'name': 'DbReactor',
        'login_url': 'https://stage15.office.dbreactor.com/sage/index.cfm?page_id=830&company_id=114606',
        'username': 'victor.moisei@mteam.md',
        'password': '12',  # Replace with your actual password
        'po_editor_urls': [
            'https://stage15.office.dbreactor.com/sage/index.cfm?page_id=839&po_id=614',
            'https://stage15.office.dbreactor.com/sage/index.cfm?page_id=839&po_id=613'
        ]
    },
    {
        'name': 'Atlas',
        'login_url': 'https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=830&company_id=183241',
        'username': 'victor.moisei@mteam.md',
        'password': '12',  # Replace with your actual password
        'po_editor_urls': [
            'https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=839&po_id=233',
            'https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=839&po_id=234'
        ]
    },
    {
        'name': 'Horus',
        'login_url': 'https://stage15.office.horustrading.eu/sage/index.cfm?page_id=830&company_id=93381',
        'username': 'victor.moisei@mteam.md',
        'password': '12',  # Replace with your actual password
        'po_editor_urls': [
            'https://stage15.office.horustrading.eu/sage/index.cfm?page_id=839&po_id=737',
            'https://stage15.office.horustrading.eu/sage/index.cfm?page_id=839&po_id=736'
        ]
    },
    {
        'name': 'ARO',
        'login_url': 'https://stage15.office.arotrading.eu/sage/index.cfm?page_id=830&company_id=431345',
        'username': 'victor.moisei@mteam.md',
        'password': '12',  # Replace with your actual password
        'po_editor_urls': [
            'https://stage15.office.arotrading.eu/sage/index.cfm?page_id=839&po_id=3',
            'https://stage15.office.arotrading.eu/sage/index.cfm?page_id=839&po_id=2'
        ]
    }
]

# Main script execution starts here
try:
    for system in systems:
        logging.info(f"Starting tests for system: {system['name']}")
        # Navigate to the login page
        driver.get(system['login_url'])
        logging.info(f'Navigated to {system["login_url"]}')
        
        # Wait for the login form to load
        login_name_input = wait.until(EC.visibility_of_element_located((By.ID, 'login_name')))
        login_name_input.clear()
        login_name_input.send_keys(system['username'])
        logging.info('Entered login name')
        
        password_input = driver.find_element(By.ID, 'password')
        password_input.clear()
        password_input.send_keys(system['password'])
        logging.info('Entered password')
        
        # Click on the Submit button
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"].btn.btn-info.btn-lg')
        submit_button.click()
        logging.info('Clicked on the Submit button')
        
        # Wait briefly to ensure login processing
        time.sleep(5)
        
        # Initialize variables for each system
        main_window = driver.current_window_handle
        po_editor_windows = []
        poim_windows = []
        status_bad_data_list = []
        po_ids = []
        
        # Open PO Editor pages in new tabs
        for po_url in system['po_editor_urls']:
            driver.execute_script(f'window.open("{po_url}", "_blank");')
            logging.info(f'Opened PO Editor page: {po_url}')
            po_editor_windows.append(driver.window_handles[-1])
        
        # Process each PO Editor page
        for idx, po_editor_window in enumerate(po_editor_windows, start=1):
            try:
                driver.switch_to.window(po_editor_window)
                logging.info(f'Switched to PO Editor page {idx} for system {system["name"]}')
                
                # Check if logged in
                if not is_logged_in(driver):
                    logging.error(f'Login fields found in PO Editor page {idx}. Login was not successful.')
                    test_results.append(f'{system["name"]} Test {idx}: Login was not successful on PO Editor page {idx}.')
                    raise Exception('Login failed.')
                
                # Extract PO ID from the page
                po_id = extract_po_id(driver)
                if not po_id:
                    test_results.append(f'{system["name"]} Test {idx}: Could not extract PO ID on PO Editor page {idx}.')
                    continue  # Skip to next iteration
                
                po_ids.append(po_id)
                
                # Find and click the GO to POIM button
                try:
                    go_to_poim_button = wait.until(EC.element_to_be_clickable((By.ID, 'go_to_poim')))
                    poim_url = go_to_poim_button.get_attribute('href')
                    logging.info(f'Found GO to POIM button with href: {poim_url}')
                    # Open POIM page in new tab
                    before_handles = set(driver.window_handles)
                    driver.execute_script(f'window.open("{poim_url}", "_blank");')
                    logging.info(f'Opened POIM page {idx} in new tab')
                    after_handles = set(driver.window_handles)
                    new_handles = after_handles - before_handles
                    poim_window = new_handles.pop()
                    poim_windows.append(poim_window)
                except Exception as e:
                    logging.error(f'Could not find GO to POIM button on PO Editor page {idx}: {e}')
                    test_results.append(f'{system["name"]} Test {idx}: GO to POIM button not found on PO Editor page {idx}')
                    continue  # Skip to next iteration
                
                # Switch to POIM page
                driver.switch_to.window(poim_window)
                logging.info(f'Switched to POIM page {idx}')
                
                # Extract POIM ID from URL
                poim_url_current = driver.current_url
                parsed_url = urlparse(poim_url_current)
                poim_id = parse_qs(parsed_url.query).get('id', [None])[0]
                logging.info(f'POIM ID for POIM page {idx}: {poim_id}')
                
                # Check the status on POIM page
                try:
                    wait.until(EC.visibility_of_element_located((By.XPATH, "//p[text()='Status:']")))
                    status_div = driver.find_element(By.XPATH, "//p[text()='Status:']/following-sibling::div[contains(@class, 'scr_data')]")
                    status_text = status_div.text.strip()
                    logging.info(f'Status in POIM page {idx}: {status_text}')
                    status_input = driver.find_element(By.NAME, 'status_id')
                    status_id_value = status_input.get_attribute('value')
                    logging.info(f'Status ID value: {status_id_value}')
                    
                    if 'Bad Data' in status_text or status_id_value == '272':
                        logging.info('Status is Bad Data')
                        status_bad_data_list.append(True)
                        test_results.append(f'{system["name"]} Test 1: Bad Data status found in PO ID {po_id}. Passed.')
                        
                        # Switch back to PO Editor page
                        driver.switch_to.window(po_editor_window)
                        logging.info(f'Switched back to PO Editor page {idx}')
                        
                        # Execute JavaScript to click the "Attach PO to existing invoice" button
                        try:
                            # Extract the onclick attribute's JavaScript code
                            attach_button = driver.find_element(By.ID, 'attach_po_to_existing_invoice')
                            onclick_script = attach_button.get_attribute('onclick')
                            logging.info(f'Onclick script: {onclick_script}')
                            
                            # Execute the JavaScript code directly
                            driver.execute_script(onclick_script)
                            logging.info('Executed onclick JavaScript to simulate "Attach PO to existing invoice" button click')
                            test_results.append(f'{system["name"]} Test 1: Attach button found and working correctly on PO ID {po_id}. Passed.')
                            
                            # Wait for the table to load
                            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'table.table.table-bordered.table-striped.xvalignmiddle')))
                            
                            # Check that the POIM ID (from the URL) is not present in the ID column
                            table = driver.find_element(By.CSS_SELECTOR, 'table.table.table-bordered.table-striped.xvalignmiddle')
                            rows = table.find_elements(By.TAG_NAME, 'tr')
                            poim_id_present = False
                            for row in rows[1:]:  # Skip the header row
                                cols = row.find_elements(By.TAG_NAME, 'td')
                                if cols:
                                    id_cell = cols[0]
                                    id_link = id_cell.find_element(By.TAG_NAME, 'a')
                                    id_text = id_link.text.strip()
                                    logging.info(f'Found ID in table: {id_text}')
                                    if id_text == poim_id:
                                        poim_id_present = True
                                        break
                            if not poim_id_present:
                                logging.info(f'Current POIM ID {poim_id} is not present in the ID column.')
                                test_results.append(f'{system["name"]} Test 1: The attach table has the correct data for POIM ID {poim_id}. Passed.')
                            else:
                                logging.error(f'Current POIM ID {poim_id} is present in the ID column.')
                                test_results.append(f'{system["name"]} Test 1: The attach table contains the current POIM ID {poim_id}. Failed.')
                            
                            # Close the PO Editor page tab
                            driver.close()
                            logging.info(f'Closed PO Editor page {idx}')
                            # Switch back to POIM page
                            driver.switch_to.window(poim_window)
                        except Exception as e:
                            logging.error(f'Error executing JavaScript to click "Attach PO to existing invoice" button on PO Editor page {idx}: {e}')
                            test_results.append(f'{system["name"]} Test 1: Attach button not found or not working on PO ID {po_id}. Failed.')
                        
                        # Since status is "Bad Data", skip the autocomplete test on this POIM page
                        logging.info(f'Skipping autocomplete test on POIM page {idx} due to Bad Data status.')
                        # Close the POIM page tab
                        driver.close()
                        logging.info(f'Closed POIM page {idx}')
                    else:
                        logging.info('Status is not Bad Data')
                        status_bad_data_list.append(False)
                        
                        # Switch back to PO Editor page
                        driver.switch_to.window(po_editor_window)
                        logging.info(f'Switched back to PO Editor page {idx}')
                        
                        # Attempt to click the "Attach invoice to new PO" button if it exists
                        try:
                            attach_new_po_button = driver.find_element(By.ID, 'attach_invoice_to_new_po')
                            onclick_script = attach_new_po_button.get_attribute('onclick')
                            logging.info(f'Onclick script for "Attach invoice to new PO" button: {onclick_script}')
                            
                            # Execute the JavaScript code directly
                            driver.execute_script(onclick_script)
                            logging.info('Executed onclick JavaScript to simulate "Attach invoice to new PO" button click')
                            test_results.append(f'{system["name"]} Test 2: Attach invoice to new PO button found and working on PO ID {po_id}. Passed.')
                            
                        except Exception as e:
                            logging.info(f'"Attach invoice to new PO" button not found on PO Editor page {idx}, which may be expected.')
                            test_results.append(f'{system["name"]} Test 2: "Attach invoice to new PO" button not present on PO Editor page {idx}. Skipped.')
                        
                        # Close the PO Editor page tab
                        driver.close()
                        logging.info(f'Closed PO Editor page {idx}')
                        # Switch back to POIM page
                        driver.switch_to.window(poim_window)
                        
                        # Perform the autocomplete test using Selenium
                        logging.info(f'Performing autocomplete test on POIM page {idx}')
                        
                        try:
                            # Wait for the autocomplete input field to be visible
                            autocomplete_input = wait.until(EC.visibility_of_element_located((By.ID, 'new_po_number_autocompleter')))
                            logging.info('Autocomplete input field is visible')
                            
                            # Retry mechanism
                            max_retries = 1
                            retry_count = 0
                            add_button_enabled = False
                            
                            while retry_count <= max_retries and not add_button_enabled:
                                # Click on the autocomplete field to focus
                                autocomplete_input.click()
                                logging.info('Clicked on the autocomplete input field to focus.')
                                
                                # Determine which PO ID to use
                                if idx == 2 and status_bad_data_list[0] and po_ids[0]:
                                    po_id_current = po_ids[0]  # Use PO ID from PO Editor page 1
                                    logging.info(f'Using PO ID from PO Editor page 1 for autocomplete: {po_id_current}')
                                else:
                                    po_id_current = po_ids[-1]  # Use PO ID from current PO Editor
                                    logging.info(f'Using PO ID from current PO Editor for autocomplete: {po_id_current}')
                                
                                # Clear the field if retrying
                                if retry_count > 0:
                                    autocomplete_input.clear()
                                    logging.info('Cleared the autocomplete input field for retry.')
                                
                                # Input the PO ID using send_keys, simulating typing
                                for char in po_id_current:
                                    autocomplete_input.send_keys(char)
                                    time.sleep(0.1)  # Simulate typing speed
                                logging.info(f'Typed PO ID: {po_id_current}')
                                
                                # Wait for 7 seconds
                                logging.info('Waiting for 7 seconds before pressing Enter.')
                                time.sleep(7)
                                
                                # Press Enter to select the autocomplete result
                                autocomplete_input.send_keys(Keys.RETURN)
                                logging.info('Pressed Enter after 7 seconds.')
                                time.sleep(2)
                                
                                # Wait until the ADD button is enabled, with a timeout of 10 seconds
                                try:
                                    add_button = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.ID, 'new_po_number_submit'))
                                    )
                                    logging.info('ADD button is now clickable')
                                    add_button_enabled = True
                                except TimeoutException:
                                    logging.error('ADD button did not become clickable in time.')
                                    retry_count += 1
                                    if retry_count <= max_retries:
                                        logging.info(f'Retrying autocomplete input. Attempt {retry_count} of {max_retries}.')
                                        continue  # Retry input
                                    else:
                                        test_results.append(f'{system["name"]} Test 2: Autocomplete test failed on POIM page {idx}. Failed.')
                                        # Close the POIM page tab
                                        driver.close()
                                        logging.info(f'Closed POIM page {idx}')
                                        break  # Exit the retry loop
                                
                                if add_button_enabled:
                                    # Check if the 'new_po_number' input field has been populated
                                    new_po_number_input = driver.find_element(By.ID, 'new_po_number')
                                    new_po_number_value = new_po_number_input.get_attribute('value')
                                    logging.info(f'new_po_number input value: "{new_po_number_value}"')
                                    
                                    if new_po_number_value.strip() != '':
                                        logging.info('new_po_number field has been populated.')
                                        test_results.append(f'{system["name"]} Test 2: Autocomplete test passed on POIM page {idx}. Passed.')
                                    else:
                                        logging.error('new_po_number field is still empty.')
                                        test_results.append(f'{system["name"]} Test 2: new_po_number field is empty after autocomplete on POIM page {idx}. Failed.')
                                    
                                    # Close the POIM page tab
                                    driver.close()
                                    logging.info(f'Closed POIM page {idx}')
                            
                            # End of while loop
                            
                        except Exception as e:
                            logging.error(f'Could not perform autocomplete test on POIM page {idx}: {e}')
                            test_results.append(f'{system["name"]} Test 2: Autocomplete test failed on POIM page {idx}. Failed.')
                            # Close the POIM page tab
                            driver.close()
                            logging.info(f'Closed POIM page {idx}')
                        
                except Exception as e:
                    logging.error(f'Error checking status on POIM page {idx}: {e}')
                    test_results.append(f'{system["name"]} Test {idx}: Error checking status on POIM page {idx}')
                    continue
                
            except Exception as e:
                logging.error(f'Error processing PO Editor page {idx}: {e}')
                test_results.append(f'{system["name"]} Test {idx}: Error processing PO Editor page {idx}')
                continue
        
        # Return to the main window before starting the next system
        driver.switch_to.window(main_window)
        logging.info(f'Completed tests for system: {system["name"]}')
        # Optionally, you can log out here if necessary

except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
finally:
    # Print test summary
    logging.info('Test Summary:')
    all_tests_passed = True  # Flag to determine if all important tests passed
    for result in test_results:
        logging.info(result)
        # Check for failed important tests
        if ('Failed' in result or 'Error' in result) and ('Test 1' in result or 'Test 2' in result):
            all_tests_passed = False

    # Print final message
    if all_tests_passed:
        logging.info('All tests passed successfully.')
    else:
        logging.info('Some tests failed. Please review the test summary.')
        # Exit with an error code if there's any "Failed" in results
        sys.exit(1)

    # Clean up
    try:
        driver.quit()
    except:
        pass
