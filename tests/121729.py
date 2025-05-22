import os
import logging
import time
import json
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)

def load_page_with_retries(driver, url, locator, max_tries=3, wait_timeout=20):

    wait = WebDriverWait(driver, wait_timeout)
    for attempt in range(1, max_tries + 1):
        driver.get(url)
        try:
            wait.until(EC.presence_of_element_located(locator))
            logging.info(f"Page loaded successfully on attempt {attempt}: {url}")
            return  # If found, just exit the function (success)
        except TimeoutException:
            logging.warning(f"Attempt {attempt}/{max_tries}: element {locator} not found on {url}. Retrying...")

    raise Exception(f"Failed to load {url} and locate {locator} after {max_tries} attempts.")


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Credentials from .env
USERNAME = os.getenv("USERNAMEALEX")
PASSWORD = os.getenv("PASSWORDALEX")

if not USERNAME or not PASSWORD:
    logging.error("USERNAMEALEX and PASSWORDALEX environment variables are not set in the .env file")
    sys.exit(1)

# List of systems (domains) to check
SYSTEMS = [
    "stage15.office.sovamaxusa.com", 
    "stage15.office.ratrading.eu",
    "stage15.office.agavasystem.com",
    "stage15.office.eminiasystem.com",
    "stage15.office.laniustoys.com",
    "stage15.office.dbreactor.com",
    "stage15.office.horustrading.eu",
    "stage15.office.atlastradingworld.com",
    "stage15.office.sovasystem.com",
]


def create_webdriver():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = script_dir

    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # chrome_options.add_argument("--headless")  # Uncomment to run in headless mode

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.implicitly_wait(100)  # Implicit wait
    return driver


def login_to_system(driver, login_url):

    try:
        # Instead of a single driver.get(...), we do repeated load attempts
        load_page_with_retries(
            driver,
            url=login_url,
            locator=(By.ID, "login_name"),  # we consider "login_name" as the element to confirm page loaded
            max_tries=3,
            wait_timeout=20
        )
        logging.info(f"Login page opened (final): {login_url}")

        # Now fill in credentials
        username_field = driver.find_element(By.ID, "login_name")
        username_field.clear()
        username_field.send_keys(USERNAME)

        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(PASSWORD)

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        logging.info("Clicked on the 'Login' button.")

        time.sleep(3)  # Wait a bit for login to process

    except Exception as e:
        logging.error(f"Error during login at {login_url}: {e}", exc_info=True)
        raise


def go_to_search_page(driver, page22_url):

    attempts = 3
    wait_timeout = 15

    for attempt in range(1, attempts + 1):
        try:
            # 1) Загрузить/убедиться, что страница page22_url отображается
            load_page_with_retries(
                driver,
                url=page22_url,
                locator=(By.ID, "items_in_stock_1"),  # ждем появления радио-кнопки
                max_tries=3,
                wait_timeout=wait_timeout
            )
            logging.info(f"Navigated to the search page (final): {page22_url} (attempt {attempt})")

            # 2) Клик по радио-кнопке
            label_element = driver.find_element(By.CSS_SELECTOR, "label[for='items_in_stock_1']")
            label_element.click()
            logging.info("Clicked on the 'items_in_stock_1' radio button.")

            # 3) Клик по кнопке поиска
            search_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary[type='submit']")
            search_button.click()
            logging.info("Clicked on the search button.")

            # 4) Ждём появления колонки "Item ID"
            WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "//th[@class='text-center' and normalize-space()='Item ID']"))
            )
            logging.info("Search results are loaded (found the 'Item ID' header).")

            # Если добрались сюда — значит мы нашли нужную колонку; выходим из функции
            return

        except TimeoutException as e:

            logging.warning(
                f"Attempt {attempt}/{attempts}: 'Item ID' header not found after pressing Search. Retrying..."
            )
            if attempt < attempts:

                driver.refresh()
                time.sleep(3)
            else:
                raise Exception(f"Couldn't load Item ID header after {attempts} attempts on {page22_url}") from e

        except Exception as e:
            if attempt < attempts:
                logging.warning(f"Attempt {attempt} failed with error {e}. Refreshing page.")
                driver.refresh()
                time.sleep(3)
            else:
                raise
def go_to_search_page(driver, page22_url):

    attempts = 3
    wait_timeout = 20

    for attempt in range(1, attempts + 1):
        try:
            # 1) Загрузить/убедиться, что страница page22_url отображается
            load_page_with_retries(
                driver,
                url=page22_url,
                locator=(By.ID, "items_in_stock_1"),  # ждем появления радио-кнопки
                max_tries=3,
                wait_timeout=wait_timeout
            )
            logging.info(f"Navigated to the search page (final): {page22_url} (attempt {attempt})")

            # 2) Клик по радио-кнопке
            label_element = driver.find_element(By.CSS_SELECTOR, "label[for='items_in_stock_1']")
            label_element.click()
            logging.info("Clicked on the 'items_in_stock_1' radio button.")

            # 3) Клик по кнопке поиска
            search_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary[type='submit']")
            search_button.click()
            logging.info("Clicked on the search button.")

            # 4) Ждём появления колонки "Item ID"
            WebDriverWait(driver, wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "//th[@class='text-center' and normalize-space()='Item ID']"))
            )
            logging.info("Search results are loaded (found the 'Item ID' header).")

            # Если добрались сюда — значит мы нашли нужную колонку; выходим из функции
            return

        except TimeoutException as e:

            logging.warning(
                f"Attempt {attempt}/{attempts}: 'Item ID' header not found after pressing Search. Retrying..."
            )
            if attempt < attempts:

                driver.refresh()
                time.sleep(3)
            else:
                raise Exception(f"Couldn't load Item ID header after {attempts} attempts on {page22_url}") from e

        except Exception as e:
            # Если другая ошибка (не TimeoutException),
            # можно сразу кидать дальше или тоже перезапустить
            if attempt < attempts:
                logging.warning(f"Attempt {attempt} failed with error {e}. Refreshing page.")
                driver.refresh()
                time.sleep(3)
            else:
                raise


def get_two_item_ids(driver):

    attempts = 3
    for attempt in range(1, attempts + 1):
        try:
            rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'search_results_detail_')]")
            item_ids = []
            for row in rows:
                row_id = row.get_attribute("id")  # e.g., "search_results_detail_4806"
                if row_id and row_id.startswith("search_results_detail_"):
                    _, _, numeric_id = row_id.partition("search_results_detail_")
                    item_ids.append(numeric_id)
                if len(item_ids) == 2:
                    break

            if len(item_ids) >= 2:
                logging.info(f"Found item_ids on attempt {attempt}: {item_ids}")
                return item_ids
            else:
                # Not enough item_ids, maybe reload the page or wait
                logging.warning(f"Attempt {attempt}/{attempts}: Could not find 2 item_ids. Retrying...")
                # Можно сделать короткую паузу или обновить страницу:
                driver.refresh()
                time.sleep(3)
        except Exception as e:
            logging.warning(f"Attempt {attempt}/{attempts} failed to find item_ids: {e}")
            driver.refresh()
            time.sleep(3)

    raise ValueError("Could not find 2 item_ids in the search results after multiple attempts.")


def search_item_ids_on_other_page(driver, page589_url, item_ids):

    results = []
    all_in_stock = True
    try:
        if len(item_ids) < 2:
            raise ValueError("Need at least 2 item_ids to perform the check.")

        modified_url = f"{page589_url}&search_item_id={item_ids[0]}&duplicate_item_id={item_ids[1]}"

        load_page_with_retries(
            driver,
            url=modified_url,
            locator=(By.XPATH, "//th[contains(@class,'comfirstrow')]"),
            max_tries=3,
            wait_timeout=20
        )
        logging.info(f"Navigated to page (final): {modified_url}")

        # Now we do the In Stock checks
        time.sleep(5)  # short pause for the dynamic content to load

        for index, item in enumerate(item_ids):
            # Determine label: original vs duplicate
            item_type = "Original Item ID" if index == 0 else "Duplicate Item ID"

            xpath_for_item_block = (
                f"//th[contains(@class,'comfirstrow')]"
                f"//p[contains(text(),'{item}')]"
                f"//span[contains(text(),'In Stock')]"
            )
            elements = driver.find_elements(By.XPATH, xpath_for_item_block)
            if elements:
                msg = f"For {item_type} = ({item}) => 'In Stock' FOUND"
                logging.info(msg)
                results.append(msg)
            else:
                msg = f"For {item_type} = ({item}) => 'In Stock' NOT FOUND!"
                logging.warning(msg)
                results.append(msg)
                all_in_stock = False

        return results, all_in_stock

    except Exception as e:
        logging.error(f"Error while checking item_ids on {page589_url}: {e}", exc_info=True)
        raise


def test_single_system(domain):

    driver = create_webdriver()
    test_results = []
    all_in_stock_for_this_system = True
    try:
        login_url = f"https://{domain}/sage/?logout"
        page22_url = f"https://{domain}/sage/index.cfm?page_id=22"
        page589_url = f"https://{domain}/sage/index.cfm?page_id=589"

        # 1. Login (with retries)
        login_to_system(driver, login_url)
        # 2. Go to the search page (22) (with retries)
        go_to_search_page(driver, page22_url)
        # 3. Get 2 item_ids (up to 3 tries inside get_two_item_ids)
        item_ids = get_two_item_ids(driver)
        # 4. On page 589, check 'In Stock' (with retries)
        results, all_in_stock = search_item_ids_on_other_page(driver, page589_url, item_ids)

        test_results.append(f"SUCCESS: Retrieved item_ids: {item_ids}")
        test_results.extend(results)

        if not all_in_stock:
            all_in_stock_for_this_system = False

    except Exception as e:
        msg = f"ERROR in system {domain}: {e}"
        logging.error(msg)
        test_results.append(msg)
        all_in_stock_for_this_system = False

    finally:
        driver.quit()

    return test_results, all_in_stock_for_this_system


def main():

    overall_results = {}
    all_good = True

    for domain in SYSTEMS:
        logging.info(f"=== Starting test for system: {domain} ===")
        results_for_domain, system_ok = test_single_system(domain)
        overall_results[domain] = results_for_domain
        if not system_ok:
            all_good = False
        logging.info(f"=== Test finished for system: {domain} ===\n")

    # Print TEST SUMMARY
    print("\n\n===== TEST SUMMARY =====")
    for domain, results in overall_results.items():
        print(f"--- {domain} ---")
        for line in results:
            print(f"   {line}")
    print("===== END OF SUMMARY =====")

    # If at least one system is missing "In Stock", exit with code 1
    if not all_good:
        print("ERROR: In some systems the inscription (In Stock) is not displayed correctly on the page!")
        sys.exit(1)
    else:
        print("SUCCESS: In all systems the inscription (In Stock) is displayed correctly on the page!")


if __name__ == "__main__":
    main()
