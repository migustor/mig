import os
import logging
import time
import random
import json
import sys  # <-- нужно импортировать sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from selenium.webdriver.common.action_chains import ActionChains

# Load environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set up options for the web driver
script_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = script_dir  # Path for downloading files
chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True,
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
# chrome_options.add_argument("--headless")  # если нужен headless-режим

# Initialize the web driver
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 1000)  # Wait up to 1000 seconds

# Maximize the browser window
driver.maximize_window()

# Get credentials from environment variables
username = os.getenv("USERNAMEALEX")
password = os.getenv("PASSWORDALEX")

if not username or not password:
    logging.error(
        "Please set the variables USERNAMEDIM and PASSWORDDIM in your .env file"
    )
    driver.quit()
    sys.exit(1)

# Флаги для отслеживания результатов
column_current_sp_promo_found = False
column_current_sp_found = False
column_arriving_po_found = False

# Флаг общего статуса теста
test_failed = False

# Function for logging into the system
def login_to_system(login_url):
    try:
        # Navigate to the login page
        driver.get(login_url)
        logging.info(f"Navigated to login page: {login_url}")

        time.sleep(1)  # Wait 1 second before the next action

        # Enter username
        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "login_name"))
        )
        username_field.clear()
        username_field.send_keys(username)
        logging.info("Username entered.")

        time.sleep(1)

        # Enter password
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        logging.info("Password entered.")

        time.sleep(1)

        # Click the "Submit" button
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        logging.info("Login button clicked.")

        time.sleep(2)  # Wait 2 seconds to complete the login process

    except Exception as e:
        logging.error(f"Error during login: {e}", exc_info=True)
        driver.quit()
        sys.exit(1)

try:
    # Perform login
    login_url = "https://stage15.office.eminiasystem.com/sage/?logout"
    login_to_system(login_url)
    """
    # Navigate to the product search page
    search_url = "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=22"
    driver.get(search_url)
    logging.info("Product search page loaded.")
    time.sleep(1)

    # Click the radio button with value="1" for "items_in_stock"
    items_in_stock_label = driver.find_element(
        By.XPATH, '//label[@for="items_in_stock_1"]'
    )
    items_in_stock_label.click()
    logging.info('Radio button "items_in_stock_1" selected by clicking on label.')
    time.sleep(1)
    
    # Click the "Show advanced settings" button
    show_advanced_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.additional_settings_show"))
    )
    show_advanced_button.click()
    logging.info('Button "Show advanced settings" clicked.')
    time.sleep(1)

    # Select value "=" in the dropdown
    pn_variations_select = Select(driver.find_element(By.ID, "pn_variations_comparation_code"))
    pn_variations_select.select_by_value("3")
    logging.info('Value "=" selected in "pn_variations_comparation_code".')
    time.sleep(1)

    # Enter the number "1" in the "pn_variations" field
    pn_variations_input = driver.find_element(By.ID, "pn_variations")
    pn_variations_input.clear()
    pn_variations_input.send_keys("1")
    logging.info('Value "1" entered in field "pn_variations".')
    time.sleep(1)
    

    # Click the "Search" button via JavaScript
    try:
        search_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        driver.execute_script("arguments[0].click();", search_button)
        logging.info('Button "Search" clicked.')
    except Exception as e:
        logging.error(f'Failed to click "Search" button: {e}', exc_info=True)
        driver.save_screenshot("error_clicking_search_button.png")
        raise

    time.sleep(1)

    # Wait for the results table to load
    try:
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "table.table.table-bordered.table-striped.xvalignmiddle")
            )
        )
        logging.info("Results table loaded.")
    except TimeoutException:
        logging.error("Results table did not load within the expected time.")
        driver.save_screenshot("error_waiting_for_results_table.png")
        raise

    time.sleep(1)

    # Extract value from the "Part Number" column of the first row
    try:
        part_number = driver.find_element(
            By.CSS_SELECTOR, "table.table.table-bordered.table-striped.xvalignmiddle tbody tr td:nth-child(3)"
        ).text.strip()
        logging.info(f'Value "Part Number" extracted: {part_number}')
    except Exception as e:
        logging.error(f'Failed to extract "Part Number": {e}', exc_info=True)
        driver.save_screenshot("error_extracting_part_number.png")
        raise
    """

    # Save the value for later use
    saved_part_number = "123110101113"
    time.sleep(1)

    # Now continue by navigating to the company creation page
    target_url = "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=442&phase=new"
    driver.get(target_url)
    logging.info("Target company creation page loaded.")
    time.sleep(1)

    # Fill in the "company_name" field
    company_name_input = driver.find_element(By.ID, 'company_name')
    random_chars = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))
    company_name = 'test' + random_chars
    company_name_input.send_keys(company_name)
    logging.info(f'Field "company_name" filled with value: {company_name}')
    time.sleep(1)

    # Select country "United Kingdom UK"
    country_select = Select(driver.find_element(By.ID, 'country_info'))
    country_select.select_by_value('224')
    logging.info('Country "United Kingdom UK" selected.')
    time.sleep(1)

    # Select option "Car Service"
    segmentation_select = Select(driver.find_element(By.ID, 'segmentation_id'))
    segmentation_select.select_by_value('9')
    logging.info('Option "Car Service" selected in "segmentation_id" field.')
    time.sleep(1)

    # Fill in the "address_line_one" field
    address_line_one_input = driver.find_element(By.ID, 'address_line_one')
    random_chars = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))
    address_line_one = 'test' + random_chars
    address_line_one_input.send_keys(address_line_one)
    logging.info(f'Field "address_line_one" filled with value: {address_line_one}')
    time.sleep(1)

    # Fill in the "city" field
    city_input = driver.find_element(By.ID, 'city')
    random_chars = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=5))
    city = 'test' + random_chars
    city_input.send_keys(city)
    logging.info(f'Field "city" filled with value: {city}')
    time.sleep(1)

    # Fill in the "address_postal_code" field
    postal_code_input = driver.find_element(By.ID, 'address_postal_code')
    postal_code = 'SW1W 0NY'
    postal_code_input.send_keys(postal_code)
    logging.info(f'Field "address_postal_code" filled with value: {postal_code}')
    time.sleep(1)

    # Fill in the "contact_phone_number_1" field
    phone_input = driver.find_element(By.NAME, 'contact_phone_number_1')
    phone_number = ''.join(random.choices('0123456789', k=9))
    phone_input.send_keys(phone_number)
    logging.info(f'Field "contact_phone_number_1" filled with value: {phone_number}')
    time.sleep(1)

    # Fill in the "vat_number" field
    vat_input = driver.find_element(By.ID, 'vat_number')
    vat_number = 'GB' + ''.join(random.choices('0123456789', k=9))
    vat_input.send_keys(vat_number)
    logging.info(f'Field "vat_number" filled with value: {vat_number}')
    time.sleep(1)

    # Click the "Create Company" button
    create_button = driver.find_element(By.XPATH, '//button[text()="Create Company"]')
    create_button.click()
    logging.info('Button "Create Company" clicked.')

    # Wait for new tab to appear
    wait.until(lambda d: len(d.window_handles) > 1)
    windows_after_create = driver.window_handles
    new_window = [window for window in windows_after_create if window != driver.current_window_handle][0]
    driver.switch_to.window(new_window)
    logging.info('Switched to new tab after creating company.')
    time.sleep(2)

    # Wait for the page to load and the "Generate Sales Order" link to appear
    generate_order_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Generate Sales Order')))
    logging.info('Link "Generate Sales Order" found.')
    time.sleep(1)

    # Click on the "Generate Sales Order" link
    generate_order_link.click()
    logging.info('Link "Generate Sales Order" clicked.')

    # Wait for new tab to open
    wait.until(lambda d: len(d.window_handles) > 2)
    windows_after_order = driver.window_handles
    new_order_window = [window for window in windows_after_order if window not in windows_after_create][0]
    driver.switch_to.window(new_order_window)
    logging.info('Switched to order creation tab.')
    time.sleep(2)

    # Click the "Create Sales Order" button
    create_order_button = wait.until(EC.element_to_be_clickable((By.ID, 'surplus_order_btn')))
    create_order_button.click()
    logging.info('Button "Create Sales Order" clicked.')
    time.sleep(2)

    # Wait for the new page to load with URL containing sales_order_id
    wait.until(EC.url_contains("page_id=888&sales_order_id="))
    logging.info('Order creation page loaded.')

    # Click on the element "Add More Items"
    try:
        add_more_items_element = driver.find_element(By.XPATH, '//h4[contains(text(), "Add More Items")]')
        driver.execute_script("arguments[0].click();", add_more_items_element)
        logging.info('Element "Add More Items" clicked.')
    except Exception as e:
        logging.error(f'Failed to click on element "Add More Items": {e}', exc_info=True)
        driver.save_screenshot("error_clicking_add_more_items.png")
        raise
    time.sleep(1)

    # Click on tab "Shopping Cart Items"
    try:
        shopping_cart_tab = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#shopping_cart" and contains(text(), "Shopping Cart Items")]')
            )
        )
        driver.execute_script("arguments[0].click();", shopping_cart_tab)
        logging.info('Tab "Shopping Cart Items" clicked.')
    except Exception as e:
        logging.error(f'Failed to click on tab "Shopping Cart Items": {e}', exc_info=True)
        driver.save_screenshot("error_clicking_shopping_cart_tab.png")
        raise
    time.sleep(1)

    # Enter the saved Part Number into the field
    try:
        part_number_textarea = driver.find_element(By.CSS_SELECTOR, "#shopping_cart textarea[name='item_part_number']")
        part_number_textarea.clear()
        part_number_textarea.send_keys(saved_part_number)
        logging.info(f'Part Number "{saved_part_number}" entered into field.')
    except Exception as e:
        logging.error(f'Failed to enter Part Number: {e}', exc_info=True)
        driver.save_screenshot("error_entering_part_number.png")
        raise
    time.sleep(1)

    # Click the "Search" button
    try:
        search_button = driver.find_element(By.ID, 'html_shopping_cart_button')
        driver.execute_script("arguments[0].click();", search_button)
        logging.info('Button "Search" clicked.')
    except Exception as e:
        logging.error(f'Failed to click "Search" button: {e}', exc_info=True)
        driver.save_screenshot("error_clicking_search_button_after_part_number.png")
        raise
    time.sleep(2)

    # Wait for the results table to load
    try:
        results_table = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "table.shopping_cart_result")
            )
        )
        logging.info("Product search results table loaded.")
    except TimeoutException:
        logging.error("Product search results table did not load.")
        driver.save_screenshot("error_waiting_for_shopping_cart_result_table.png")
        raise
    time.sleep(1)

    # Check for the presence of the "Current SP / Promo" column
    try:
        column_element = driver.find_element(
          By.XPATH, "//th[normalize-space(text())='Current SP / Promo']"
        )
        column_text = column_element.text.strip()
        if column_text == "Current SP / Promo":
            logging.info('Column "Current SP / Promo" is present in the product search table.')
            column_current_sp_promo_found = True
        else:
            logging.warning('Failed Column "Current SP / Promo" was not found in the product search table.')
            test_failed = True  # <-- флажок становится True при "Failed"
    except Exception as e:
        logging.error(f'Error checking table columns: {e}', exc_info=True)
        driver.save_screenshot("error_checking_table_headers.png")
        raise

    # Click the "Add" button inside the table (first found)
    try:
        add_button = driver.find_element(
            By.XPATH, "//form[contains(@id, 'add_shopping_cart_item_')]//button[contains(text(), 'Add')]"
        )
        driver.execute_script("arguments[0].click();", add_button)
        logging.info('Button "Add" clicked.')
    except Exception as e:
        logging.error(f'Failed to click "Add" button: {e}', exc_info=True)
        driver.save_screenshot("error_clicking_add_button.png")
        raise
    time.sleep(2)

    # Wait for the "List of Shopping Cart Items" table to appear
    try:
        shopping_cart_list_header = wait.until(
            EC.presence_of_element_located((By.ID, "list_of_shopping_cart_items"))
        )
        logging.info('Table "List of Shopping Cart Items" loaded.')
    except TimeoutException:
        logging.error('Table "List of Shopping Cart Items" did not load.')
        driver.save_screenshot("error_waiting_for_shopping_cart_items_list.png")
        raise

    time.sleep(1)

    # Wait for the table with class "shopping_cart_items_list" to appear
    try:
        shopping_cart_table = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "table.shopping_cart_items_list")
            )
        )
        logging.info('Table "shopping_cart_items_list" successfully found.')
    except TimeoutException:
        logging.error('Table "shopping_cart_items_list" did not load.')
        driver.save_screenshot("error_waiting_for_shopping_cart_items_table.png")
        raise
    time.sleep(1)

    # Check for the presence of columns "Current SP" and "Arriving PO"
    try:
        cart_table_headers = shopping_cart_table.find_elements(By.CSS_SELECTOR, "thead th")
        cart_header_texts = [header.text.strip() for header in cart_table_headers]

        if "Current SP" in cart_header_texts:
            logging.info('Column "Current SP" is present in the cart table.')
            column_current_sp_found = True
        else:
            logging.warning('Failed Column "Current SP" was not found in the cart table.')
            test_failed = True  # <-- флажок становится True при "Failed"

        if "Arriving PO" in cart_header_texts:
            logging.info('Column "Arriving PO" is present in the cart table.')
            column_arriving_po_found = True
        else:
            logging.warning('Failed Column "Arriving PO" was not found in the cart table.')
            test_failed = True  # <-- флажок становится True при "Failed"

    except Exception as e:
        logging.error(f'Error checking cart table columns: {e}', exc_info=True)
        driver.save_screenshot("error_checking_cart_table_headers.png")
        raise

except Exception as e:
    logging.error(f'An error occurred: {e}', exc_info=True)
    driver.save_screenshot("error_screenshot.png")
    test_failed = True
finally:
    # Close the driver
    driver.quit()
    logging.info('Web driver closed.')

    # === TEST SUMMARY ===
    logging.info("=== TEST SUMMARY ===")

    # Отчёт о "Current SP / Promo"
    if column_current_sp_promo_found:
        logging.info('Column "Current SP / Promo" was successfully found in the product search table.')
    else:
        logging.warning('Failed Column "Current SP / Promo" was not found in the product search table.')
        test_failed = True

    # Отчёт о "Current SP"
    if column_current_sp_found:
        logging.info('Column "Current SP" was successfully found in the cart table.')
    else:
        logging.warning('Failed Column "Current SP" was not found in the cart table.')
        test_failed = True

    # Отчёт о "Arriving PO"
    if column_arriving_po_found:
        logging.info('Column "Arriving PO" was successfully found in the cart table.')
    else:
        logging.warning('Failed Column "Arriving PO" was not found in the cart table.')
        test_failed = True

    # Если test_failed = True, завершаем скрипт с кодом ошибки.
    if test_failed:
        sys.exit(1)
