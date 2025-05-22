import os
import sys
import time
import glob
import logging
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("script.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def wait_for_file_download(directory, timeout=60):
    """Wait for a file to be downloaded to the specified directory."""
    logging.info("Waiting for XLS file to be downloaded...")
    seconds = 0
    while seconds < timeout:
        files = glob.glob(os.path.join(directory, "*.xls"))
        if files:
            return files[0]
        time.sleep(1)
        seconds += 1
    return None

def login_to_system(driver, wait, login_url, username, password):
    try:
        # Navigate to the logout page to ensure we are logged out
        driver.get(login_url)
        logging.info(f"Navigated to page: {login_url}")

        # Wait for the username input field and enter the username
        logging.info("Waiting for the username input field")
        username_field = wait.until(EC.presence_of_element_located((By.ID, "login_name")))
        username_field.clear()
        username_field.send_keys(username)
        logging.info("Username entered.")

        # Wait for the password input field and enter the password
        logging.info("Waiting for the password input field")
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        logging.info("Password entered.")

        # Click the "Submit" button
        logging.info("Waiting for the login button")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        logging.info("Clicked the login button.")

    except Exception as e:
        logging.error(f"Error during login: {e}", exc_info=True)
        raise  # Re-raise the exception to be handled in the calling function

def process_system(system):

    result = {
        'system_name': system['name'],
        'report_url': system['report_url'],
        'values_from_page': None,
        'values_from_file': None,
        'match': None,
        'message': ''
    }

    try:
        # Initialize WebDriver for each system
        # Set up Chrome options for automatic file download
        chrome_options = Options()
        prefs = {
            "download.default_directory": system['download_dir'],
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # Uncomment the following line if you want to run the browser in headless mode
        # chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 30)  # Wait up to 30 seconds

        username = system['username']
        password = system['password']

        if not username or not password:
            logging.error(f"Please set the username and password for {system['name']}")
            driver.quit()
            return result

        # Login to the system
        logging.info(f"Logging into {system['name']}")
        login_to_system(driver, wait, system['login_url'], username, password)
        logging.info(f"Login successful for {system['name']}")

        # Navigate to the report page
        logging.info(f"Navigating to the report page: {system['report_url']}")
        driver.get(system['report_url'])

        # ================ NEW / CHANGED PART: SET DATE VIA JS ==================
        # Ожидаем, что элемент с ID "datepicker_from" присутствует на странице
        logging.info("Waiting for the date_from element (ID=datepicker_from)")
        date_input = wait.until(EC.presence_of_element_located((By.ID, "datepicker_from")))

        # Выполняем JavaScript, чтобы проставить нужную дату, скажем 01-Oct-2024
        # Можно выбрать любую нужную логику (год, месяц). Пример: 01-Oct-2024
        # или если нужна текущая дата, см. пример на старый код.
        logging.info("Setting date range using JavaScript for 01-Oct-2024")
        js_code = """
        (function() {
            var dateInput = document.getElementById('datepicker_from');
            // Строка в формате day-MonName-YYYY
            // Для октября: "01-Oct-2024"
            var dateString = "01-Oct-2024";
            dateInput.value = dateString;

            // Если на странице используется jQuery Datepicker или Bootstrap Datepicker:
            // подстраховываемся, чтобы дата проставилась внутри самого плагина
            // Замените при необходимости .datepicker(...) на актуальный метод,
            // если у вас точно jQuery UI datepicker или Bootstrap datepicker.
            if (window.jQuery && jQuery().datepicker) {
                // Для jQuery UI datepicker:
                jQuery(dateInput).datepicker('setDate', new Date(2024, 9, 1)); 
                jQuery(dateInput).trigger('changeDate'); 
            } else if (window.jQuery && jQuery().fn.datepicker) {
                // Для Bootstrap datepicker (часто используется .fn.datepicker)
                jQuery(dateInput).datepicker('setDate', new Date(2024, 9, 1)); 
                jQuery(dateInput).trigger('changeDate');
            }
        })();
        """
        driver.execute_script(js_code)
        time.sleep(2)  # Дадим время календарю/JS обновить внутреннее состояние


        # Теперь кликаем "Submit" (как и было ранее)
        logging.info("Waiting for the 'Submit' button")
        submit_button = wait.until(
            EC.element_to_be_clickable((By.ID, "search"))
        )
        logging.info("Clicking the 'Submit' button")
        submit_button.click()

        # Wait for either the table to load or "No results" message
        logging.info("Waiting for the table to load or 'No results' message")
        try:
            # Wait for the table header element
            table_header = wait.until(
                EC.presence_of_element_located((By.XPATH, "//th[text()='Conversation Duration']"))
            )
            logging.info("Table loaded successfully")

            logging.info("Retrieving values from the last text-right column in each row")
            rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
            values_from_page = []
            for row in rows:
                # Ищем первую ячейку <td> (чтобы проверить, нет ли там 'Total:')
                tds_all = row.find_elements(By.CSS_SELECTOR, "td")
                if not tds_all:
                    continue  # Строка без <td> пропускается на всякий случай

                first_cell_text = tds_all[0].text.strip()
                if "Total:" in first_cell_text:
                    # Пропускаем эту строку
                    continue

                # Для остальных строк берём последнюю ячейку с классом text-right
                tds_right = row.find_elements(By.CSS_SELECTOR, "td.text-right")
                if tds_right:
                    last_td_value = tds_right[-1].text.strip()
                    values_from_page.append(last_td_value)

            logging.info(f"Values retrieved from the page: {values_from_page}")
            result['values_from_page'] = values_from_page

            # Click the "Export to spreadsheet" button
            logging.info("Waiting for the 'Export to spreadsheet' button")
            export_button = wait.until(
                EC.element_to_be_clickable((By.ID, "export"))
            )
            logging.info("Clicking the 'Export to spreadsheet' button")
            export_button.click()

            # Wait for the download link to appear
            logging.info("Waiting for the download link to appear")
            result_div = wait.until(
                EC.presence_of_element_located((By.ID, "result"))
            )
            download_link_element = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='result']//a"))
            )
            download_link = download_link_element.get_attribute('href')
            logging.info(f"Download link obtained: {download_link}")

            # Click the link to download the file
            logging.info("Clicking the download link")
            download_link_element.click()

            # Wait for the file to be downloaded
            downloaded_file = wait_for_file_download(system['download_dir'])
            if downloaded_file:
                logging.info(f"File downloaded: {downloaded_file}")
            else:
                logging.error("File download did not complete within the expected time")
                result['message'] = "File download timeout"
                driver.quit()
                return result

            # Read the XLS file using pandas
            logging.info("Reading the XLS file using pandas")
            df = pd.read_excel(downloaded_file)

            # Check if the "Conversation Duration" column exists
            if "Conversation Duration" in df.columns:
                logging.info("Column 'Conversation Duration' found in the XLS file")
                values_from_file = df["Conversation Duration"].astype(str).str.strip().tolist()
                logging.info(f"Values from the XLS file: {values_from_file}")
                result['values_from_file'] = values_from_file
            else:
                logging.error("Column 'Conversation Duration' not found in the XLS file")
                result['message'] = "Column 'Conversation Duration' not found in XLS"
                driver.quit()
                return result

            # Compare values from the page and the file
            if values_from_page == values_from_file:
                logging.info(f"Conversation Duration from the page and the XLS file match for {system['name']}")
                result['match'] = True
            else:
                logging.error(f"Conversation Duration from the page and the XLS file DO NOT match for {system['name']}")
                result['match'] = False
                result['message'] = "Conversation Duration do not match"

        except TimeoutException:
            # Table did not load, check for "No results" message
            logging.info("Table did not load, checking for 'No results' message")
            try:
                no_results_message = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='result']//div[contains(@class, 'info-div') and contains(text(), 'No results')]"))
                )
                logging.info(f"No results found for the specified date in {system['name']}")
                result['message'] = "No results found for the specified date"
                result['match'] = None
                # Skip to next system
                return result

            except TimeoutException:
                # Neither table nor "No results" message found, raise exception
                logging.error("Neither table nor 'No results' message found")
                raise

    except Exception as e:
        logging.exception(f"An error occurred during processing of {system['name']}")
        result['message'] = str(e)
    finally:
        logging.info(f"Closing the browser for {system['name']}")
        driver.quit()
        return result

def main():
    # List of systems to process
    systems = [
        {
            'name': 'Eminia System',
            'login_url': 'https://stage15.office.eminiasystem.com/sage/?logout',
            'report_url': 'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=934',
            'username': os.getenv('USERNAMEDIM'),
            'password': os.getenv('PASSWORDDIM'),
            'download_dir': os.path.join(os.path.abspath("downloads"), "em_system")
        },
        {
            'name': 'RA System',
            'login_url': 'https://stage15.office.ratrading.eu/sage/?logout',
            'report_url': 'https://stage15.office.ratrading.eu/sage/index.cfm?page_id=934',
            'username': os.getenv('USERNAMEDIM'),
            'password': os.getenv('PASSWORDDIM'),
            'download_dir': os.path.join(os.path.abspath("downloads"), "ra_system")
        },
        {
            'name': 'SMEU System',
            'login_url': 'https://stage15.office.sovasystem.com/sage/?logout',
            'report_url': 'https://stage15.office.sovasystem.com/sage/index.cfm?page_id=934',
            'username': os.getenv('USERNAMEDIM'),
            'password': os.getenv('PASSWORDDIM'),
            'download_dir': os.path.join(os.path.abspath("downloads"), "smeu_system")
        },
    ]

    # Ensure download directories exist
    for system in systems:
        if not os.path.exists(system['download_dir']):
            os.makedirs(system['download_dir'])

    results = []

    # Process each system
    for system in systems:
        logging.info(f"\n=== Processing {system['name']} ===")
        result = process_system(system)
        results.append(result)
        logging.info(f"Finished processing {system['name']}\n")

    # Print summary
    logging.info("\n==== TEST SUMMARY ====")
    any_failures = False  # Флаг для отслеживания неудач

    for result in results:
        if result['match'] is None:
            # Например, случай "No results"
            logging.info(f"{result['system_name']}: {result['message']}")
        elif result['match']:
            # Всё ок
            logging.info(f"{result['system_name']}: SUCCESS Conversation Duration from the page and the XLS file match.")
        else:
            # match == False → не совпадает
            logging.warning(f"{result['system_name']}:FAILED Conversation Duration from the page and the XLS file DO NOT match.")
            any_failures = True

    # Если есть хотя бы один fail - завершаем скрипт с кодом ошибки
    if any_failures:
        sys.exit(1)

if __name__ == "__main__":
    main()