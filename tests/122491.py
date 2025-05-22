import os
import logging
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.common.exceptions import TimeoutException


load_dotenv()


log_messages = []


class ListHandler(logging.Handler):
    def emit(self, record):
        log_messages.append(self.format(record))


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


list_handler = ListHandler()
list_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
list_handler.setFormatter(formatter)
logging.getLogger().addHandler(list_handler)

# Configure webdriver options
script_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = script_dir  # Path to download files
chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True,
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

# chrome_options.add_argument("--headless")


driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)  


driver.maximize_window()


username = os.getenv("USERNAMEALEX")
password = os.getenv("PASSWORDALEX")

if not username or not password:
    logging.error(
        "Please set the USERNAMEALEX and PASSWORDALEX variables in your .env file"
    )
    driver.quit()
    exit(1)

def is_number(s):
    try:
        float(s.replace('€', '').replace(',', '').strip())
        return True
    except ValueError:
        return False

def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

def login_to_system(login_url):
    try:
        driver.get(login_url)
        logging.info(f"Navigated to login page: {login_url}")

        # Enter username
        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "login_name"))
        )
        username_field.clear()
        username_field.send_keys(username)
        logging.info("Username entered.")

        # Enter password
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        logging.info("Password entered.")

        # Click the "Submit" button
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        logging.info("Login button clicked.")

        # Wait for the URL to change after login
        wait.until(EC.url_contains("sage/index.cfm"))
        logging.info("Successfully logged in.")

    except TimeoutException:
        logging.error("Timeout while trying to log in. Check your credentials or the stability of the page.", exc_info=True)
        raise  

    except Exception as e:
        logging.error(f"Error during login: {e}", exc_info=True)
        raise  

# Main script
try:
    sites = [
        {
            "name": "Stage15 Eminia",
            "login_url": "https://stage15.office.eminiasystem.com/sage/?logout",
            "test_url": "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=903&phase=edit&id=8144"
        },
        {
            "name": "stage15 Ratrading",
            "login_url": "https://stage15.office.ratrading.eu/sage/?logout",
            "test_url": "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=903&phase=edit&id=5425"
        },
        {
            "name": "stage15 Agava",
            "login_url": "https://stage15.office.agavasystem.com/sage/?logout",
            "test_url": "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=903&phase=edit&id=3612"
        },
        {
            "name": "stage15 Lanius",
            "login_url": "https://stage15.office.laniustoys.com/sage/?logout",
            "test_url": "https://stage15.office.laniustoys.com/sage/index.cfm?page_id=903&phase=edit&id=3469"
        },
        {
            "name": "stage15 DBReactor",
            "login_url": "https://stage15.office.dbreactor.com/sage/?logout",
            "test_url": "https://stage15.office.dbreactor.com/sage/index.cfm?page_id=903&phase=edit&id=161"
        },
        {
            "name": "stage15 Horus",
            "login_url": "https://stage15.office.horustrading.eu/sage/?logout",
            "test_url": "https://stage15.office.horustrading.eu/sage/index.cfm?page_id=903&phase=edit&id=175"
        },
        {
            "name": "stage15 Sova EU",
            "login_url": "https://stage15.office.sovasystem.com/sage/?logout",
            "test_url": "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=903&phase=edit&id=15887"
        }
    ]

    overall_test_results = {}

    for site in sites:
        site_name = site["name"]
        logging.info(f"=== Testing site: {site_name} ===")

        test_results = {}

        try:
            # Perform login
            login_url = site["login_url"]
            login_to_system(login_url)

            # Navigate to the test page
            test_url = site["test_url"]
            driver.get(test_url)
            logging.info(f"Navigated to test page: {test_url}")

            # Повторная загрузка страницы (до 3-х попыток) при неудаче
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    # Ожидаем появления таблицы
                    wait.until(EC.presence_of_element_located((By.ID, "assigned_po_so")))
                    logging.info("Table found on the page.")
                    break
                except TimeoutException:
                    logging.warning(
                        f"Table not found on attempt {attempt}/{max_retries}. Refreshing page..."
                    )
                    driver.refresh()
                    if attempt == max_retries:
                        logging.error(
                            f"Table not found after {max_retries} attempts. Skipping site {site_name}."
                        )
                        test_results["Error"] = f"Could not load table after {max_retries} attempts."
                        overall_test_results[site_name] = test_results
                        # Переходим к следующему сайту
                        raise TimeoutException(f"Table not found after {max_retries} attempts.")

            # Если мы здесь, значит таблица найдена
            # Find all sortable column headers
            sortable_headers = driver.find_elements(
                By.XPATH,
                '//table[@id="assigned_po_so"]//thead//td[contains(@class, "tablesorter-header") and not(contains(@class, "sorter-false"))]'
            )
            logging.info(f"Found {len(sortable_headers)} sortable columns.")

            # Get all headers to determine their indices
            all_headers = driver.find_elements(By.XPATH, '//table[@id="assigned_po_so"]//thead//td')
            header_indices = {hdr.text.strip(): idx for idx, hdr in enumerate(all_headers)}

            # Iterate over each sortable column
            for header in sortable_headers:
                column_name = header.text.strip()
                logging.info(f"Checking sorting for column: {column_name}")

                idx = header_indices.get(column_name)
                if idx is None:
                    logging.error(f"Column {column_name} not found in headers.")
                    continue

                # Scroll to the column header
                driver.execute_script("arguments[0].scrollIntoView();", header)

                # Dictionary to store results for this column
                column_result = {}

                for desired_state in ['ascending', 'descending']:
                    # Set desired sort state
                    attempts = 0
                    while True:
                        aria_sort = header.get_attribute("aria-sort")
                        if aria_sort == desired_state:
                            break
                        else:
                            header.click()
                            time.sleep(1)  # Wait for table update
                            attempts += 1
                            if attempts > 3:
                                logging.error(f"Unable to set {desired_state} sort for column {column_name}.")
                                column_result[desired_state] = "Sort failed (unable to set desired state)"
                                break

                    if attempts > 3:
                        # Unable to set desired sort state, skip checks
                        continue

                    # Collect data from the column
                    rows = driver.find_elements(By.XPATH, '//table[@id="assigned_po_so"]//tbody/tr[not(contains(@style, "display: none"))]')
                    if not rows:
                        logging.error("No rows found in the table after sorting.")
                        column_result[desired_state] = "Sort failed (no data)"
                        continue

                    data = []
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if not cells:
                            continue
                        first_cell = cells[0]
                        colspan = first_cell.get_attribute('colspan')
                        if colspan and int(colspan) >= 4:
                            # Totals row
                            continue
                        if idx < len(cells):
                            cell = cells[idx]
                            cell_text = clean_text(cell.get_attribute('textContent'))
                            data.append(cell_text)
                        else:
                            data.append('')

                    logging.info(f"{desired_state.capitalize()} data: {data}")

                    # Special handling for columns:
                    if column_name == 'Order#':
                        def extract_order_number(text):
                            match = re.match(r'(\d+)', text)
                            return int(match.group(1)) if match else 0
                        values = [extract_order_number(text) for text in data]
                        logging.info(f"{desired_state.capitalize()} values: {values}")
                        sorted_values = sorted(values, reverse=(desired_state=='descending'))
                        logging.info(f"Expected {desired_state} values: {sorted_values}")
                        column_result[desired_state] = "Sort passed" if values == sorted_values else "Sort failed"

                        if column_result[desired_state] == "Sort failed":
                            logging.error(f"Data in column {column_name} is not sorted in {desired_state} order.")

                    elif column_name == 'Company / Carrier':
                        def company_carrier_sort_key(text):
                            match = re.search(r'company(\d+)', text, re.IGNORECASE)
                            if match:
                                return (0, int(match.group(1)))
                            else:
                                return (1, text.lower())

                        key_values = [company_carrier_sort_key(x) for x in data]
                        logging.info(f"{desired_state.capitalize()} key values: {key_values}")

                        sorted_data = sorted(data, key=company_carrier_sort_key, reverse=(desired_state=='descending'))
                        logging.info(f"Expected {desired_state} data: {sorted_data}")

                        column_result[desired_state] = "Sort passed" if data == sorted_data else "Sort failed"
                        if column_result[desired_state] == "Sort failed":
                            logging.error(f"Data in column {column_name} is not sorted in {desired_state} order.")

                    elif column_name == 'Ship. Offer':
                        values = []
                        for text in data:
                            t = text.strip()
                            if t == '-':
                                continue
                            v = float(t.replace('€', '').replace(',', '').strip())
                            values.append(v)
                        logging.info(f"{desired_state.capitalize()} values: {values}")
                        sorted_values = sorted(values, reverse=(desired_state=='descending'))
                        logging.info(f"Expected {desired_state} values: {sorted_values}")
                        column_result[desired_state] = "Sort passed" if values == sorted_values else "Sort failed"
                        if column_result[desired_state] == "Sort failed":
                            logging.error(f"Data in column {column_name} is not sorted in {desired_state} order.")

                    elif column_name == 'Problem type':
                        def problem_type_key(x):
                            x = x.strip()
                            if desired_state == 'ascending':
                                return (0, x.lower()) if x != '' else (1,'')
                            else:
                                return (1, x.lower()) if x != '' else (0,'')

                        sorted_data = sorted(data, key=problem_type_key, reverse=(desired_state=='descending'))
                        logging.info(f"Expected {desired_state} data: {sorted_data}")
                        column_result[desired_state] = "Sort passed" if data == sorted_data else "Sort failed"
                        if column_result[desired_state] == "Sort failed":
                            logging.error(f"Data in column {column_name} is not sorted in {desired_state} order.")

                    else:
                        # Standard processing
                        is_numeric = all(is_number(text) for text in data if text not in ['', '-'])

                        if is_numeric:
                            values = [
                                float(text.replace('€', '').replace(',', '').strip()) 
                                if text not in ['', '-'] else 0.0 
                                for text in data
                            ]
                            logging.info(f"{desired_state.capitalize()} values: {values}")
                            sorted_values = sorted(values, reverse=(desired_state=='descending'))
                            logging.info(f"Expected {desired_state} values: {sorted_values}")
                            column_result[desired_state] = "Sort passed" if values == sorted_values else "Sort failed"
                            if column_result[desired_state] == "Sort failed":
                                logging.error(f"Data in column {column_name} is not sorted in {desired_state} order.")
                        else:
                            sorted_data = sorted(data, key=lambda x: x.lower(), reverse=(desired_state=='descending'))
                            logging.info(f"Expected {desired_state} data: {sorted_data}")
                            column_result[desired_state] = "Sort passed" if data == sorted_data else "Sort failed"
                            if column_result[desired_state] == "Sort failed":
                                logging.error(f"Data in column {column_name} is not sorted in {desired_state} order.")

                test_results[column_name] = column_result

            overall_test_results[site_name] = test_results

        except Exception as e:
            logging.error(f"An error occurred while testing site {site_name}: {e}", exc_info=True)
            overall_test_results[site_name] = {"Error": str(e)}
            continue

    logging.info("=== OVERALL TEST SUMMARY ===")
    initial_length = len(log_messages)  # Сохраняем текущую длину логов

    all_tests_passed = True
    failed_sites = []

    for site_name, site_results in overall_test_results.items():
        site_passed = True
        logging.info(f"Site: {site_name}")
        if "Error" in site_results:
            logging.info(f"  Error occurred: {site_results['Error']}")
            all_tests_passed = False
            failed_sites.append(site_name)
            continue

        for column, results in site_results.items():
            for sort_order, result in results.items():
                if result != "Sort passed":
                    site_passed = False
                    all_tests_passed = False
                    logging.info(f"  Column '{column}' - {sort_order.capitalize()} sort: {result}")
        if site_passed:
            logging.info(f"  All sorting tests passed for {site_name}")
        else:
            failed_sites.append(site_name)
        logging.info("")

    if all_tests_passed:
        logging.info("All pages passed the sorting tests successfully.")
    else:
        logging.info("Some pages failed the sorting tests.")
        logging.info("Pages with issues:")
        for site in failed_sites:
            logging.info(f" - {site}")

    # Теперь анализируем только новые логи, появившиеся после initial_length
    summary_logs = log_messages[initial_length:]
    summary_logs_str = "\n".join(summary_logs).lower()

    # Если в итоговых логах обнаружено "failed", генерируем исключение
    if "failed" in summary_logs_str:
        raise Exception("Found 'failed' in final summary logs.")

    driver.quit()

except Exception as e:
    logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    driver.quit()
