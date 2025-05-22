import logging
import time
import sys
from typing import Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def setup_driver():
    """Setup Chrome driver with options"""
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--headless')  # Раскомментируйте для запуска без UI
    return webdriver.Chrome(options=options)

def generate_summary(test_results: Dict) -> str:
    """Generate detailed test summary"""
    summary = "\n=== ALZURA SEARCH TEST SUMMARY ===\n"

    # Login section
    summary += "\nLogin Steps:"
    summary += f"\n[{'+'if test_results['login']['success'] else '-'}] Login to system"
    if test_results['login'].get('error'):
        summary += f"\n    Error: {test_results['login']['error']}"

    # Search Controls section
    summary += "\n\nSearch Controls:"
    summary += f"\n[{'+'if test_results['dropdown']['present'] else '-'}] Alzura option present in dropdown"
    summary += f"\n[{'+'if test_results['dropdown']['selected'] else '-'}] Alzura option successfully selected"
    if test_results['dropdown'].get('error'):
        summary += f"\n    Error: {test_results['dropdown']['error']}"

    # Search Input section
    summary += "\n\nSearch Operation:"
    summary += f"\n[{'+'if test_results['search']['input_filled'] else '-'}] Search input filled with order ID"
    summary += f"\n[{'+'if test_results['search']['submitted'] else '-'}] Search form submitted"
    if test_results['search'].get('error'):
        summary += f"\n    Error: {test_results['search']['error']}"

    # Results Verification section
    summary += "\n\nResults Verification:"
    summary += f"\n[{'+'if test_results['results']['link_present'] else '-'}] Alzura link found in results"
    summary += f"\n[{'+'if test_results['results']['correct_url'] else '-'}] Correct URL format: {test_results['results'].get('actual_url', 'N/A')}"
    summary += f"\n[{'+'if test_results['results']['order_id_in_text'] else '-'}] Order ID present in link text"
    if test_results['results'].get('error'):
        summary += f"\n    Error: {test_results['results']['error']}"

    # Overall Status
    all_passed = all([
        test_results['login']['success'],
        test_results['dropdown']['present'],
        test_results['dropdown']['selected'],
        test_results['search']['input_filled'],
        test_results['search']['submitted'],
        test_results['results']['link_present'],
        test_results['results']['correct_url'],
        test_results['results']['order_id_in_text']
    ])

    summary += f"\n\nOverall Test Status: {'[PASSED]' if all_passed else '[FAILED]'}"
    summary += "\n=================\n"

    return summary

def main():
    driver = None
    test_results = {
        'login': {'success': False},
        'dropdown': {'present': False, 'selected': False},
        'search': {'input_filled': False, 'submitted': False},
        'results': {
            'link_present': False,
            'correct_url': False,
            'order_id_in_text': False,
            'actual_url': None
        }
    }

    try:
        setup_logging()
        logging.info("Starting Alzura search test")

        driver = setup_driver()
        wait = WebDriverWait(driver, 10)

        # Шаг 1: Логин
        logging.info("Attempting login")
        driver.get("https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=973")
        username_input = wait.until(EC.presence_of_element_located((By.ID, "login_name")))
        password_input = driver.find_element(By.ID, "password")
        username_input.send_keys("maxim.lupan@mteam.md")
        password_input.send_keys("12")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(3)
        test_results['login']['success'] = True
        logging.info("Login successful")

        # Шаг 2: Выбор поиска Alzura
        logging.info("Selecting Alzura search option")
        dropdown = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#additional_search_criteria_type')
        ))
        select = Select(dropdown)
        test_results['dropdown']['present'] = 'Alzura order id' in [o.text for o in select.options]

        select.select_by_visible_text('Alzura order id')
        test_results['dropdown']['selected'] = (select.first_selected_option.text == 'Alzura order id')
        logging.info("Alzura search option selected")

        # Шаг 3: Поиск заказа
        order_id = "POE26309230424"
        logging.info(f"Searching for order: {order_id}")
        search_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#additional_search_criteria')
        ))
        search_input.clear()
        search_input.send_keys(order_id)
        test_results['search']['input_filled'] = True

        submit_button = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#submit_form')
        ))
        submit_button.click()
        test_results['search']['submitted'] = True

        time.sleep(8)

        # Шаг 4: Проверка результатов
        logging.info("Verifying search results")
        expected_url = f"https://supplier.alzura.com/de/de/orderhistory/details/order/{order_id}"
        link = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, f'a[href="{expected_url}"]')
        ))
        test_results['results']['link_present'] = True

        actual_url = link.get_attribute('href')
        test_results['results']['actual_url'] = actual_url
        test_results['results']['correct_url'] = (actual_url == expected_url)
        test_results['results']['order_id_in_text'] = (order_id in link.text)

        logging.info("All checks passed successfully!")
        print(generate_summary(test_results))
        return 0

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Test failed: {error_msg}")

        # Записываем ошибку в соответствующую секцию результатов
        if not test_results['login']['success']:
            test_results['login']['error'] = error_msg
        elif not test_results['dropdown']['selected']:
            test_results['dropdown']['error'] = error_msg
        elif not test_results['search']['submitted']:
            test_results['search']['error'] = error_msg
        else:
            test_results['results']['error'] = error_msg

        print(generate_summary(test_results))
        return 1

    finally:
        if driver:
            driver.quit()
            logging.info("Browser closed")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
