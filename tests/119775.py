import os
import sys
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configure driver and options
script_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = script_dir  # Path for file downloads
chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)  # Wait up to 30 seconds

username = os.getenv('USERNAMEDIM')
password = os.getenv('PASSWORDDIM')

if not username or not password:
    logging.error("Please set the USERNAMEDIM and PASSWORDDIM variables in your .env file")
    driver.quit()
    exit(1)

# Login to the system
def login_to_system(login_url):
    try:
        # Navigate to the login page
        driver.get(login_url)
        logging.info(f"Navigated to login page: {login_url}")

        # Enter username and password
        username_field = wait.until(EC.presence_of_element_located((By.ID, "login_name")))
        username_field.clear()
        username_field.send_keys(username)
        logging.info("Username entered.")

        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        logging.info("Password entered.")

        # Click the "Submit" button
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        logging.info("Clicked the login button.")

    except Exception as e:
        logging.error(f"Error during login: {e}")
        driver.quit()
        exit(1)

# Functions for processing tables
def get_column_sum(table, column_index):
    rows = table.find_elements(By.TAG_NAME, "tr")
    column_sum = 0
    for row in rows[1:-1]:  # Skip header and last row with total sum
        try:
            cell_value = row.find_elements(By.TAG_NAME, "td")[column_index].text.strip().replace('€', '').replace('$', '').replace(',', '')
            column_sum += float(cell_value)
        except:
            continue
    return column_sum  # возвращаем без округления, чтобы при необходимости можно было делать округление в самих check-функциях

def get_total_sum(table_id, total_xpath):
    table = driver.find_element(By.ID, table_id)
    total_sum = float(table.find_element(By.XPATH, total_xpath).text.strip().replace('€', '').replace('$', '').replace(',', ''))
    return total_sum  # аналогично возвращаем без округления

def is_table_empty(table_id):
    try:
        empty_row = driver.find_element(By.XPATH, f"//table[@id='{table_id}']//td[@class='dataTables_empty']")
        if empty_row.is_displayed():
            logging.info(f"No data in table {table_id}.")
            return True
    except:
        return False

def open_all_hidden_tables_with_js(chevron_xpath):
    try:
        # Find all elements matching the XPath
        chevron_elements = driver.find_elements(By.XPATH, chevron_xpath)

        # Iterate over each element and click using JavaScript
        for chevron_element in chevron_elements:
            driver.execute_script("arguments[0].click();", chevron_element)
            logging.info("Hidden table opened via JS.")
    except Exception as e:
        logging.error(f"Error opening hidden tables: {e}")

# Universal function for table checks
def check_table(check_function_name, errors, **params):
    if check_function_name == 'check_po_amount_table':
        check_po_amount_table(errors=errors, **params)
    elif check_function_name == 'check_sale_value_table':
        check_sale_value_table(errors=errors, **params)
    elif check_function_name == 'check_po_and_received_mb_table':
        check_po_and_received_mb_table(errors=errors, **params)
    else:
        error_message = f"Unknown check function: {check_function_name}"
        errors.append(error_message)
        logging.error(error_message)

def check_po_amount_table(table_id, po_amount_index, po_amount_total_xpath, errors):
    try:
        table = wait.until(EC.presence_of_element_located((By.ID, table_id)))

        if is_table_empty(table_id):
            return  # Skip check if table is empty

        # "PO Amount"
        po_amount_sum = get_column_sum(table, po_amount_index)
        # Сразу округляем до двух знаков
        po_amount_sum_rounded = round(po_amount_sum, 2)

        # Получаем итоговую сумму и тоже округляем
        po_amount_total = get_total_sum(table_id, po_amount_total_xpath)
        po_amount_total_rounded = round(po_amount_total, 2)

        # Логируем значения для наглядности
        logging.info(f"Table {table_id}: Calculated PO Amount sum = {po_amount_sum} (rounded to {po_amount_sum_rounded}), "
                     f"Total sum = {po_amount_total} (rounded to {po_amount_total_rounded})")

        # Сравниваем уже округлённые значения
        if po_amount_sum_rounded != po_amount_total_rounded:
            error_message = (
                f"PO Amount sum {po_amount_sum_rounded} does not match total sum {po_amount_total_rounded} "
                f"in table {table_id}"
            )
            errors.append(error_message)
            logging.error(error_message)
        else:
            logging.info(f"Table {table_id}: PO Amount sum is correct")
    except Exception as e:
        error_message = f"Error checking table {table_id}: {e}"
        errors.append(error_message)
        logging.error(error_message)

def check_sale_value_table(table_id, sale_value_index, sale_value_total_xpath, errors):
    try:
        table = wait.until(EC.presence_of_element_located((By.ID, table_id)))

        if is_table_empty(table_id):
            return  # Skip check if table is empty

        # Сумма по колонке "Sale Value" и её округление
        sale_value_sum = get_column_sum(table, sale_value_index)
        sale_value_sum_rounded = round(sale_value_sum, 2)

        # Итоговая сумма и её округление
        sale_value_total = get_total_sum(table_id, sale_value_total_xpath)
        sale_value_total_rounded = round(sale_value_total, 2)

        logging.info(f"Table {table_id}: Calculated Sale Value sum = {sale_value_sum} (rounded to {sale_value_sum_rounded}), "
                     f"Total sum = {sale_value_total} (rounded to {sale_value_total_rounded})")

        if sale_value_sum_rounded != sale_value_total_rounded:
            error_message = (
                f"Sale Value sum {sale_value_sum_rounded} does not match total sum {sale_value_total_rounded} "
                f"in table {table_id}"
            )
            errors.append(error_message)
            logging.error(error_message)
        else:
            logging.info(f"Table {table_id}: Sale Value sum is correct")
    except Exception as e:
        error_message = f"Error checking table {table_id}: {e}"
        errors.append(error_message)
        logging.error(error_message)

def check_po_and_received_mb_table(table_id, po_mb_index, received_mb_index, po_mb_total_xpath, received_mb_total_xpath, errors):
    try:
        table = wait.until(EC.presence_of_element_located((By.ID, table_id)))

        if is_table_empty(table_id):
            return  # Skip check if table is empty

        # Получаем суммы
        po_mb_sum = get_column_sum(table, po_mb_index)
        received_mb_sum = get_column_sum(table, received_mb_index)

        # Округляем полученные суммы
        po_mb_sum_rounded = round(po_mb_sum, 2)
        received_mb_sum_rounded = round(received_mb_sum, 2)

        # Получаем итоговые суммы и также округляем
        po_mb_total = get_total_sum(table_id, po_mb_total_xpath)
        received_mb_total = get_total_sum(table_id, received_mb_total_xpath)

        po_mb_total_rounded = round(po_mb_total, 2)
        received_mb_total_rounded = round(received_mb_total, 2)

        # Логируем
        logging.info(f"Table {table_id}: Calculated PO MB sum = {po_mb_sum} (rounded to {po_mb_sum_rounded}), "
                     f"Total sum = {po_mb_total} (rounded to {po_mb_total_rounded})")
        logging.info(f"Table {table_id}: Calculated Received MB sum = {received_mb_sum} (rounded to {received_mb_sum_rounded}), "
                     f"Total sum = {received_mb_total} (rounded to {received_mb_total_rounded})")

        # Сравниваем округлённые значения
        if po_mb_sum_rounded != po_mb_total_rounded:
            error_message = (
                f"PO MB sum {po_mb_sum_rounded} does not match total sum {po_mb_total_rounded} in table {table_id}"
            )
            errors.append(error_message)
            logging.error(error_message)
        else:
            logging.info(f"Table {table_id}: PO MB sum is correct")

        if received_mb_sum_rounded != received_mb_total_rounded:
            error_message = (
                f"Received MB sum {received_mb_sum_rounded} does not match total sum {received_mb_total_rounded} "
                f"in table {table_id}"
            )
            errors.append(error_message)
            logging.error(error_message)
        else:
            logging.info(f"Table {table_id}: Received MB sum is correct")
    except Exception as e:
        error_message = f"Error checking table {table_id}: {e}"
        errors.append(error_message)
        logging.error(error_message)

# List of pages and checks
pages = [
    {
        'login_url': "https://stage15.office.sovasystem.com/sage/?logout",
        'page_url': "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=992",
        'checks': [
            {
                'function': 'check_po_and_received_mb_table',
                'params': {
                    'table_id': 'po_received_stocked',
                    'po_mb_index': 8,
                    'received_mb_index': 9,
                    'po_mb_total_xpath': ".//td[@style='border-left: none;border-right: none;font-weight: bold;'][1]",
                    'received_mb_total_xpath': ".//td[@style='border-left: none;font-weight: bold;'][1]"
                }
            },
            {
                'function': 'check_po_and_received_mb_table',
                'params': {
                    'table_id': 'po_is_problem',
                    'po_mb_index': 8,
                    'received_mb_index': 9,
                    'po_mb_total_xpath': ".//td[@style='border-left: none;border-right: none;font-weight: bold;'][1]",
                    'received_mb_total_xpath': ".//td[@style='border-left: none;font-weight: bold;'][1]"
                }
            }
        ]
    },
    {
        'login_url': "https://stage15.office.sovamaxusa.com/sage/?logout",
        'page_url': "https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=992",
        'checks': [
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_received_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_is_problem',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_without_eusell_price',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_not_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            }
        ]
    },
    {
        'login_url': "https://stage15.office.agavasystem.com/sage/?logout",
        'page_url': "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=992",
        'checks': [
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_received_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_is_problem',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_without_eusell_price',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_not_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            }
        ]
    },
    {
        'login_url': "https://stage15.office.ratrading.eu/sage/?logout",
        'page_url': "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=992",
        'checks': [
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_received_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_is_problem',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_without_eusell_price',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_not_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            }
        ]
    },
    {
        'login_url': "https://stage15.office.dbreactor.com/sage/?logout",
        'page_url': "https://stage15.office.dbreactor.com/sage/index.cfm?page_id=992",
        'checks': [
            
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_received_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_is_problem',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_without_eusell_price',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_not_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            }
        ]
    },
    {
        'login_url': "https://stage15.office.horustrading.eu/sage/?logout",
        'page_url': "https://stage15.office.horustrading.eu/sage/index.cfm?page_id=992",
        'checks': [
            
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_received_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_is_problem',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_without_eusell_price',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_not_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            }
        ]
    },
    {
        'login_url': "https://stage15.office.atlastradingworld.com/sage/?logout",
        'page_url': "https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=992",
        'checks': [
            
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_received_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_is_problem',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_without_eusell_price',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_not_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            }
        ]
    },
    {
        'login_url': "https://stage15.office.eminiasystem.com/sage/?logout",
        'page_url': "https://stage15.office.eminiasystem.com/crm/index.cfm?page_id=992",
        'checks': [
            {
                'function': 'check_sale_value_table',
                'params': {
                    'table_id': 'po_received_stocked',
                    'sale_value_index': 7,
                    'sale_value_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_sale_value_table',
                'params': {
                    'table_id': 'po_is_problem',
                    'sale_value_index': 7,
                    'sale_value_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_sale_value_table',
                'params': {
                    'table_id': 'po_without_eusell_price',
                    'sale_value_index': 7,
                    'sale_value_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_sale_value_table',
                'params': {
                    'table_id': 'po_not_stocked',
                    'sale_value_index': 7,
                    'sale_value_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            }
            
        ]
    },
    {
        'login_url': "https://stage15.office.laniustoys.com/sage/?logout",
        'page_url': "https://stage15.office.laniustoys.com/sage/index.cfm?page_id=992",
        'checks': [
            
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_received_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_is_problem',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_without_eusell_price',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            },
            {
                'function': 'check_po_amount_table',
                'params': {
                    'table_id': 'po_not_stocked',
                    'po_amount_index': 7,
                    'po_amount_total_xpath': ".//tr/td[@style='font-weight: bold;border-left: none;border-right: none;'][1]"
                }
            }
            
        ]
    },
    {
        'login_url': "https://stage15.office.arotrading.eu/sage/?logout",
        'page_url': "https://stage15.office.arotrading.eu/sage/index.cfm?page_id=992",
        'checks': [
            {
                'function': 'check_po_and_received_mb_table',
                'params': {
                    'table_id': 'po_received_stocked',
                    'po_mb_index': 8,
                    'received_mb_index': 9,
                    'po_mb_total_xpath': ".//td[@style='border-left: none;border-right: none;font-weight: bold;'][1]",
                    'received_mb_total_xpath': ".//td[@style='border-left: none;font-weight: bold;'][1]"
                }
            },
            {
                'function': 'check_po_and_received_mb_table',
                'params': {
                    'table_id': 'po_is_problem',
                    'po_mb_index': 8,
                    'received_mb_index': 9,
                    'po_mb_total_xpath': ".//td[@style='border-left: none;border-right: none;font-weight: bold;'][1]",
                    'received_mb_total_xpath': ".//td[@style='border-left: none;font-weight: bold;'][1]"
                }
            }
        ]
    },

        
]

summaries = []

# Main loop over pages
for page in pages:
    page['errors'] = []  # Initialize error list for the page
    login_to_system(page['login_url'])
    driver.refresh()
    driver.get(page['page_url'])
    driver.refresh()

    wait.until(EC.presence_of_element_located((By.ID, "po_received_stocked")))

    # Open hidden tables if necessary
    open_all_hidden_tables_with_js("//div[@class='panel-heading pointer']//i[@class='glyphicon glyphicon-chevron-up pull-right']")

    # Perform checks
    for check in page['checks']:
        check_table(check['function'], errors=page['errors'], **check['params'])

    # Form summary message for the page
    if not page['errors']:
        summary = f"All information on page {page['page_url']} is correct."
    else:
        summary = f"Failed Issues found on page {page['page_url']}:\n"
        for error in page['errors']:
            summary += f"- {error}\n"
    summaries.append(summary)

# Close the browser
driver.quit()

# Output summaries after processing all pages
logging.info("=== TEST SUMMARY ===")
for summary in summaries:
    logging.info(summary)
    
failure_found = any("Failed" in s for s in summaries)
if failure_found:
    
    sys.exit(1)