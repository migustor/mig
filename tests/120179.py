import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time
import sys
from typing import Dict, List

from login_utils import login
from avgfunc import setup_chrome_driver, wait_for_element

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def test_page_functionality(driver, url: str, project_name: str) -> Dict:
    """
    Tests specific page functionality including button clicks and clipboard operations.
    """
    result = {
        'name': project_name,
        'page_load': {'success': False, 'error': None},
        'start_button': {'success': False, 'error': None},
        'clipboard': {'success': False, 'error': None, 'copied_text': None},
        'company_change': {'success': False, 'error': None},
        'companies': [],
        'selected_company': None,
        'verification': {
            'company_name_verified': False,
            'status_verified': False,
            'errors': []
        }
    }

    try:
        # Navigate to page and wait for load
        logging.info(f"Navigating to {url}")
        driver.get(url)
        time.sleep(3)  # Added delay after initial page load

        # Wait for page load (max 10 seconds)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        result['page_load']['success'] = True

        # Click payment request start button
        try:
            start_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#payment_request_start'))
            )
            start_button.click()
            time.sleep(2)  # Added delay after clicking start button
            result['start_button']['success'] = True
        except Exception as e:
            result['start_button']['error'] = str(e)
            logging.error(f"Error clicking start button: {e}")

        # Test clipboard functionality
        try:
            # Get company name from link
            company_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a.company_name_link'))
            )
            company_full_name = company_link.text

            # Enhanced clipboard button handling
            def click_clipboard_button():
                try:
                    # First try to find by icon
                    clipboard_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a.clipboard i.fa-copy'))
                    )
                    parent_button = clipboard_button.find_element(By.XPATH, '..')
                except:
                    # Fallback to direct button selector
                    parent_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a.clipboard[data-clipboard-target="#payment_company"]'))
                    )

                # Scroll with offset and center alignment
                driver.execute_script("""
                    arguments[0].scrollIntoView({
                        behavior: 'smooth',
                        block: 'center',
                        inline: 'center'
                    });
                """, parent_button)
                time.sleep(2)  # Wait for scroll to complete

                try:
                    # Try regular click first
                    parent_button.click()
                except ElementClickInterceptedException:
                    # If intercepted, try JavaScript click
                    driver.execute_script("arguments[0].click();", parent_button)
                except Exception as e:
                    # If still fails, try clicking the icon directly
                    try:
                        icon = parent_button.find_element(By.CSS_SELECTOR, 'i.fa-copy')
                        driver.execute_script("arguments[0].click();", icon)
                    except:
                        raise e

            click_clipboard_button()
            time.sleep(1)  # Wait after clipboard operation

            # Company change functionality
            edit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btnMini3.change'))
            )
            edit_button.click()
            time.sleep(2)  # Added delay after clicking edit button

            # Get company list
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'payment_company'))
            )
            options = select_element.find_elements(By.TAG_NAME, 'option')

            # Process companies
            companies = []
            current_company = None
            for option in options:
                company_info = {
                    'value': option.get_attribute('value'),
                    'text': option.text,
                    'selected': option.is_selected()
                }
                companies.append(company_info)
                if company_info['selected']:
                    current_company = company_info

            # Select different company
            for option in options:
                if not option.is_selected():
                    option.click()
                    time.sleep(2)  # Пауза после выбора новой компании
                    selected_company = {
                        'value': option.get_attribute('value'),
                        'text': option.text
                    }
                    logging.info(f"Selected new company: {selected_company['text']}")
                    break

            # Нажимаем на первую кнопку сохранения (после выбора компании)
            try:
                save_mini_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btnMini3.save'))
                )
                save_mini_button.click()
                time.sleep(3)  # Пауза после первого сохранения
                logging.info("Clicked first save button (mini)")
            except Exception as e:
                logging.error(f"Error clicking first save button: {e}")

            # Ждем и нажимаем на основную кнопку SAVE
            time.sleep(2)  # Дополнительная пауза перед основным сохранением
            save_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'save_pr'))
            )
            save_button.click()
            time.sleep(4)  # Увеличенная пауза после основного сохранения

            # Click Stop
            stop_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'payment_request_stop'))
            )
            stop_button.click()
            time.sleep(3)  # Increased delay after clicking stop

            # Open new tab and verify changes
            original_window = driver.current_window_handle
            driver.execute_script("window.open(arguments[0]);", url)
            time.sleep(3)  # Increased delay after opening new tab

            # Switch to new tab
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)
                    break

            time.sleep(2)  # Additional delay after switching tab

            # Verification function
            def verify_changes():
                try:
                    new_company_link = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a.company_name_link'))
                    )
                    if new_company_link.text == selected_company['text']:
                        result['verification']['company_name_verified'] = True
                        logging.info(f"Company name verification - Success")
                    else:
                        result['verification']['errors'].append(
                            f"Company name mismatch. Expected: {selected_company['text']}, Got: {new_company_link.text}"
                        )

                    start_button = driver.find_element(By.ID, 'payment_request_start')
                    result['verification']['status_verified'] = True
                    return True

                except Exception as e:
                    logging.error(f"Error during verification: {str(e)}")
                    return False

            # First verification attempt
            if not verify_changes():
                logging.info("First verification attempt failed. Retrying...")
                time.sleep(3)
                driver.refresh()
                time.sleep(3)
                verify_changes()

            # Clean up
            driver.close()
            driver.switch_to.window(original_window)

            # Update results
            result['clipboard']['success'] = True
            result['clipboard']['copied_text'] = company_full_name
            result['companies'] = companies
            result['selected_company'] = selected_company if 'selected_company' in locals() else None

        except Exception as e:
            result['clipboard']['error'] = str(e)
            logging.error(f"Error in clipboard/company change process: {e}")

    except Exception as e:
        result['page_load']['error'] = str(e)
        logging.error(f"Error in page load: {e}")

    return result

def run_tests() -> List[Dict]:
    """
    Runs tests for all systems and returns results
    """
    test_configs = [
        {
            'project': 'eminia',
            'url': 'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=864&preview_doc=1&payment_request_id=25021&phase=edit&id=15089'
        },
        {
            'project': 'sm_eu',
            'url': 'https://stage15.office.sovasystem.com/sage/index.cfm?page_id=866&preview_doc=1&payment_request_id=61921&phase=edit&id=239483'
        },
        {
            'project': 'ra_trading',
            'url': 'https://stage15.office.ratrading.eu/sage/index.cfm?page_id=864&preview_doc=1&payment_request_id=12679&phase=edit&id=7699'
        },
        {
            'project': 'agava_trading',
            'url': 'https://stage15.office.agavasystem.com/sage/index.cfm?page_id=864&preview_doc=1&payment_request_id=5244&phase=edit&id=3257'
        },
        {
            'project': 'sm_usa',
            'url': 'https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=864&preview_doc=1&payment_request_id=3863&phase=edit&id=3137'
        },
        {
            'project': 'horus',
            'url': 'https://stage15.office.horustrading.eu/sage/index.cfm?page_id=864&preview_doc=1&payment_request_id=490&phase=edit&id=243'
        }
    ]

    results = []
    driver = setup_chrome_driver(headless=True)

    try:
        for config in test_configs:
            project_result = {'name': config['project'], 'login': {'success': False}}

            login_success = login(driver, config['project'], "ml")
            project_result['login']['success'] = login_success

            if login_success:
                test_results = test_page_functionality(driver, config['url'], config['project'])
                project_result.update(test_results)
            else:
                logging.error(f"Login failed for {config['project']}")

            results.append(project_result)
            time.sleep(2)  # Added delay between projects

    finally:
        driver.quit()

    return results

def generate_summary(results: List[Dict]) -> str:
    """
    Generates a summary of test results
    Returns:
        str: Summary text and boolean indicating if any errors occurred
    """
    summary = "=== Test Execution Summary ===\n\n"
    has_errors = False

    for result in results:
        summary += f"Project: {result['name']}\n"
        summary += "-" * 50 + "\n"

        # Login results
        login_status = result['login']['success']
        summary += f"Login: {'[PASSED]' if login_status else '[FAILED]'}\n"
        if not login_status:
            has_errors = True

        if result['login']['success']:
            # Page load results
            page_load_status = result['page_load']['success']
            summary += f"Page Load: {'[PASSED]' if page_load_status else '[FAILED]'}\n"
            if result['page_load'].get('error'):
                has_errors = True
                summary += f"  Error: {result['page_load']['error']}\n"

            # Start button results
            start_button_status = result['start_button']['success']
            summary += f"Start Button: {'[PASSED]' if start_button_status else '[FAILED]'}\n"
            if result['start_button'].get('error'):
                has_errors = True
                summary += f"  Error: {result['start_button']['error']}\n"

            # Clipboard results
            clipboard_status = result['clipboard']['success']
            summary += f"Clipboard: {'[PASSED]' if clipboard_status else '[FAILED]'}\n"
            if result['clipboard']['success']:
                summary += f"  Copied Text: {result['clipboard']['copied_text']}\n"
            if result['clipboard'].get('error'):
                has_errors = True
                summary += f"  Error: {result['clipboard']['error']}\n"

            # Company change verification
            if 'verification' in result:
                summary += "\nVerification Results:\n"

                # Company name verification
                company_verified = result['verification']['company_name_verified']
                summary += f"Company Name Change: {'[PASSED]' if company_verified else '[FAILED]'}\n"
                if not company_verified:
                    has_errors = True

                # Status verification
                status_verified = result['verification']['status_verified']
                summary += f"Status Change: {'[PASSED]' if status_verified else '[FAILED]'}\n"
                if not status_verified:
                    has_errors = True

                # Errors in verification
                if result['verification']['errors']:
                    has_errors = True
                    summary += "Verification Errors:\n"
                    for error in result['verification']['errors']:
                        summary += f"  - {error}\n"

                # Show selected company
                if result.get('selected_company'):
                    summary += f"Selected Company: {result['selected_company']['text']}\n"

        summary += "\n"

    # Overall status
    summary += "=" * 50 + "\n"
    summary += f"Overall Status: {'[PASSED]' if not has_errors else '[FAILED]'}\n"

    return summary, has_errors

if __name__ == "__main__":
    logging.info("Starting test execution")
    results = run_tests()
    summary, has_errors = generate_summary(results)
    print(summary)
    logging.info("Test execution completed")

    if has_errors:
        logging.error("Tests completed with errors")
        sys.exit(1)
    else:
        logging.info("All tests passed successfully")
        sys.exit(0)
