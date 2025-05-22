import os
import logging
import time
import random
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# WebDriver options setup
script_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = script_dir
chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)

username = os.getenv('USERNAMEALEX')
password = os.getenv('PASSWORDALEX')

if not username or not password:
    logging.error("Please set USERNAMEALEX and PASSWORDALEX in your .env file.")
    driver.quit()
    exit(1)

test_summary = {}

def login_to_system(login_url):
    driver.get(login_url)
    logging.info(f"Navigated to login page: {login_url}")
    time.sleep(1)

    username_field = wait.until(EC.presence_of_element_located((By.ID, "login_name")))
    username_field.clear()
    username_field.send_keys(username)
    logging.info("Username entered.")
    time.sleep(1)

    password_field = driver.find_element(By.ID, "password")
    password_field.clear()
    password_field.send_keys(password)
    logging.info("Password entered.")
    time.sleep(1)

    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()
    logging.info("Login button clicked.")
    time.sleep(2)

def fill_company_form():
    # Filling the new company form
    company_name_input = driver.find_element(By.ID, 'company_name')
    random_chars = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))
    company_name = 'test' + random_chars
    company_name_input.send_keys(company_name)
    logging.info(f'Field "company_name" filled with: {company_name}')
    time.sleep(1)

    country_select = Select(driver.find_element(By.ID, 'country_info'))
    country_select.select_by_value('224')
    logging.info('"United Kingdom UK" selected.')
    time.sleep(1)

    segmentation_select = Select(driver.find_element(By.ID, 'segmentation_id'))
    segmentation_select.select_by_value('1')
    logging.info('"Car Service" option selected in "segmentation_id".')
    time.sleep(1)

    address_line_one_input = driver.find_element(By.ID, 'address_line_one')
    random_chars = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))
    address_line_one = 'test' + random_chars
    address_line_one_input.send_keys(address_line_one)
    logging.info(f'Field "address_line_one" filled with: {address_line_one}')
    time.sleep(1)

    city_input = driver.find_element(By.ID, 'city')
    random_chars = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))
    city = 'test' + random_chars
    city_input.send_keys(city)
    logging.info(f'Field "city" filled with: {city}')
    time.sleep(1)

    postal_code_input = driver.find_element(By.ID, 'address_postal_code')
    postal_code = 'SW1W 0NY'
    postal_code_input.send_keys(postal_code)
    logging.info(f'Field "address_postal_code" filled with: {postal_code}')
    time.sleep(1)

    phone_input = driver.find_element(By.NAME, 'contact_phone_number_1')
    phone_number = ''.join(random.choices('0123456789', k=9))
    phone_input.send_keys(phone_number)
    logging.info(f'Field "contact_phone_number_1" filled with: {phone_number}')
    time.sleep(1)

    email_adress_input = driver.find_element(By.NAME, 'contact_email')
    random_chars = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))
    email_adress = random_chars + '@gmail.com'
    email_adress_input.send_keys(email_adress)
    logging.info(f'Field "email_adress" filled with: {email_adress}')
    time.sleep(1)

    vat_input = driver.find_element(By.ID, 'vat_number')
    vat_number = 'GB' + ''.join(random.choices('0123456789', k=9))
    vat_input.send_keys(vat_number)
    logging.info(f'Field "vat_number" filled with: {vat_number}')
    time.sleep(1)

    create_button = driver.find_element(By.XPATH, '//button[text()="Create Company"]')
    create_button.click()
    logging.info('"Create Company" button clicked.')

def upload_file_and_process(file_name):
    # Wait for new tab
    wait.until(lambda d: len(d.window_handles) > 1)
    all_tabs = driver.window_handles
    driver.switch_to.window(all_tabs[-1])
    logging.info('Switched to the new tab after creating the company.')

    # Generate Lead
    generate_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btnMini3.nonico[href*='page_id=621']"))
    )
    generate_button.click()

    # Another new tab
    wait.until(lambda d: len(d.window_handles) > 2)
    all_tabs = driver.window_handles
    driver.switch_to.window(all_tabs[-1])
    logging.info('Switched to the tab opened after clicking "Generate Lead".')

    file_input = wait.until(EC.presence_of_element_located((By.ID, 'browse_document')))
    file_path = os.path.join(script_dir, file_name)
    file_input.send_keys(file_path)
    logging.info(f'File {file_path} selected successfully.')

    create_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary[type='submit']"))
    )
    create_button.click()

    # After clicking "Create Lead" wait for "Try to process automatically"
    process_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-xs.btn-flat.btn-success.xml5.parse-button.process-file-link.file-form-button-width"))
    )
    process_button.click()
    logging.info('"Try to process automatically" button clicked.')

    # Click on "Save configuration" button
    save_config_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.huge_button[type='submit']"))
    )
    save_config_button.click()
    logging.info('"Save column configuration" button clicked.')

def check_regions(words_to_check, system_name, step_name="second"):
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(.,"Marketing region:")]'))
    )
    logging.info(f'Marketing region data page loaded on {step_name} step.')

    region_blocks = driver.find_elements(By.XPATH, '//div[contains(.,"Marketing region:")]')

    for block in region_blocks:
        spans = block.find_elements(By.TAG_NAME, 'span')
        if len(spans) >= 2:
            label_span = spans[0]
            value_span = spans[1]
            if "Marketing region:" in label_span.text:
                region_value = value_span.text.strip()
                style = value_span.get_attribute('style').lower()
                logging.info(f"Checking region '{region_value}' on {step_name} ")

                # Color check
                if region_value in words_to_check:
                    # Should be red
                    if 'red' in style:
                        logging.info(f'Region "{region_value}" is CORRECTLY displayed in red.')
                    else:
                        msg = f'FAILED: In system {system_name}, the region "{region_value}" should be red, but it is not!'
                        logging.info(msg)
                        test_summary[system_name].append(msg)
                else:
                    # Should not be red
                    if 'red' in style:
                        msg = f'FAILED: In system {system_name}, the region "{region_value}" should not be red, but it is!'
                        logging.info(msg)
                        test_summary[system_name].append(msg)
                    else:
                        logging.info(f'Region "{region_value}" is not in the list and is not red - all good.')
        else:
            logging.warning("A Marketing region block found, but it does not have two span elements.")

def next_steps_and_final_check(words_to_check, system_name):
    # After checking words, click "Save Quantities..."
    save_quantities_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.huge_button[value*='Save Quantities']"))
    )
    save_quantities_button.click()
    logging.info('"Save Quantities..." button clicked.')

    # "No items found, skip this step" (step 3)
    skip_step_3_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.huge_button[value='No items found, skip this step']"))
    )
    skip_step_3_button.click()
    logging.info('"No items found, skip this step" (step 3) clicked.')

    # "No items found, skip this step" (step 4)
    skip_step_4_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.huge_button[value='No items found, skip this step']"))
    )
    skip_step_4_button.click()
    logging.info('"No items found, skip this step" (step 4) clicked.')

    # "Add processed items to the lead"
    add_processed_items_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.medium_button.processed_btn[value='Add processed items to the lead']"))
    )
    add_processed_items_button.click()
    logging.info('"Add processed items to the lead" clicked.')

    # Repeat the word check on the final page
    check_regions(words_to_check, system_name, step_name="STEP 5 ")

def run_workflow(system_name, login_url, target_url, file_name, words_to_check):
    test_summary[system_name] = []  # Initialize list for this system's results
    
    login_to_system(login_url)
    driver.get(target_url)
    logging.info(f'Target page loaded: {target_url}')
    time.sleep(1)

    fill_company_form()
    upload_file_and_process(file_name)
    check_regions(words_to_check, system_name, step_name="STEP 2")
    next_steps_and_final_check(words_to_check, system_name)
    time.sleep(5)
    
def close_extra_tabs():
    all_tabs = driver.window_handles
    for i in range(len(all_tabs)-1, 0, -1):
        driver.switch_to.window(all_tabs[i])
        driver.close()
    driver.switch_to.window(driver.window_handles[0])

try:
    # First system (EU)
    eu_config = {
        "system_name": "EU",
        "login_url": "https://stage15.office.sovasystem.com/sage/?logout",
        "target_url": "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=442&phase=new",
        "file_name": "Doc_for_EU.xlsx",
        "words_to_check": ['USA', 'Asia', 'Australia', 'Canada', 'Latin']
    }

    run_workflow(**eu_config)
    
    close_extra_tabs()

    # Second system (USA)
    usa_config = {
        "system_name": "USA",
        "login_url": "https://stage15.office.sovamaxusa.com/sage/?logout",
        "target_url": "https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=442&phase=new",
        "file_name": "Doc_for_USA.xlsx",
        "words_to_check": ['Asia', 'Africa', 'Australia', 'CIS', 'EMEA', 'Europe', 'Non EU, MEA']
    }

    run_workflow(**usa_config)

except Exception as e:
    logging.error(f'An error occurred: {e}', exc_info=True)
finally:
    # Form the TEST SUMMARY report
    logging.info("============ TEST SUMMARY ============")
    all_problems = sum(len(issues) for issues in test_summary.values())
    if all_problems == 0:
        logging.info("All words in all systems are displayed correctly.")
    else:
        logging.info("Failed -> Problems found:")
        for system, issues in test_summary.items():
            if issues:
                logging.info(f"System {system}:")
                for issue in issues:
                    logging.info(f" - {issue}")
        
        # Так как мы вывели "Failed", вызываем sys.exit(1)
        sys.exit(1)

    driver.quit()
    logging.info('Web driver closed.')
