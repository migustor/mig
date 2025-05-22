import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, JavascriptException
from time import sleep

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    logging.info("Setting up the Chrome driver.")
    options = webdriver.ChromeOptions()
    return webdriver.Chrome(options=options)

def login(driver, username, password):
    logging.info(f"Logging in as {username}")
    driver.get("https://stage5.office.sovasystem.com/sage/index.cfm?page_id=864")
    try:
        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login_name")))
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()
        logging.info("Login successful.")
    except TimeoutException:
        logging.error(f"Timeout occurred while logging in for user {username}")

def select_date(driver, from_date, to_date):
    logging.info(f"Selecting dates: from {from_date} to {to_date}")
    try:
        from_date_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "date_between_from_1")))
        to_date_input = driver.find_element(By.ID, "date_between_to_1")

        driver.execute_script("arguments[0].removeAttribute('readonly')", from_date_input)
        driver.execute_script("arguments[0].removeAttribute('readonly')", to_date_input)

        from_date_input.clear()
        from_date_input.send_keys(from_date)
        to_date_input.clear()
        to_date_input.send_keys(to_date)

        logging.info("Dates selected successfully.")
    except Exception as e:
        logging.error(f"Error occurred while selecting dates: {str(e)}")

def select_po_combined_status(driver):
    logging.info("Selecting only 'PO Combined' status.")
    try:
        multi_select_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "po_status")))
        multi_select_button.click()
        logging.info("Multi-select dropdown 'po_status' clicked.")

        multi_select_container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'multiSelectOptions') and contains(@style, 'visibility: visible')]"))
        )
        logging.info("Multi-select options container for 'po_status' is now visible.")

        select_all_checkbox = multi_select_container.find_element(By.XPATH, "//input[@name='po_status_selectAll' and @value='all']")
        if select_all_checkbox.is_selected():
            select_all_checkbox.click()
            logging.info("'Select All' checkbox clicked to deselect all statuses.")

        po_combined_checkbox = multi_select_container.find_element(By.XPATH, "//input[@name='po_status' and @value='352']")
        if not po_combined_checkbox.is_selected():
            po_combined_checkbox.click()
            logging.info("'PO Combined' status selected.")

        sleep(3)

        submit_button = driver.find_element(By.ID, "submit_btn")
        submit_button.click()
        logging.info("Submit button clicked after selecting 'PO Combined'.")

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@title, 'Contact Attempt Screen')]")))
        logging.info("Page loaded successfully after clicking 'Submit'.")
    except Exception as e:
        logging.error(f"Error occurred while selecting PO Combined status: {str(e)}")

def open_first_three_links(driver):
    logging.info("Opening the first three links in new tabs.")
    try:
        links = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@title, "Contact Attempt Screen")]')))

        for link in links[:3]:
            href = link.get_attribute("href")
            driver.execute_script(f"window.open('{href}', '_blank');")
            logging.info(f"Opened link in new tab: {href}")

        # Wait for all tabs to load
        sleep(5)
    except Exception as e:
        logging.error(f"Error occurred while opening links: {str(e)}")

def handle_show_more_and_check_po(driver):
    logging.info("Processing Purchase Orders table.")

    current_url = driver.current_url
    found_po_combined = False

    while True:
        try:
            # Ожидание доступности кнопки
            show_more_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#legacy_po_show_more_activity_button a"))
            )

            # Проверка видимости и кликабельности кнопки
            if show_more_button.is_displayed() and show_more_button.is_enabled():
                # Прокрутка кнопки в область видимости
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more_button)
                sleep(1)

                # Клик по кнопке
                show_more_button.click()
                sleep(2)  # Ожидание загрузки данных
            else:
                break  # Кнопка больше недоступна

        except TimeoutException:
            break  # Кнопка не найдена
        except ElementClickInterceptedException:
            sleep(1)
            continue  # Повторная попытка клика
        except Exception as e:
            logging.error(f"Error while processing 'Show 10 more' button: {str(e)}")
            break

    # Поиск строк с "PO combined" статусом
    po_combined_rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'changing_data')]/td[contains(text(), 'PO combined')]")
    if po_combined_rows:
        logging.info(f"Found {len(po_combined_rows)} rows with 'PO combined' status.")
        found_po_combined = True
    else:
        logging.info("No rows with 'PO combined' status found.")

    logging.info("Finished processing Purchase Orders table.")

    return found_po_combined, current_url

def generate_test_summary(results):
    logging.info("Generating test summary.")
    summary = "== Test Summary ==\n"
    for found_po_combined, url in results:
        summary += f"Page URL: {url}\n'PO Combined' status found: {'Yes' if found_po_combined else 'No'}\n"
        summary += "------------------------------------------\n"
    logging.info("Test summary generated.")
    return summary

if __name__ == "__main__":
    driver = setup_driver()
    results = []

    try:
        login(driver, "dmitri.dubkovetki@mteam.md", "12")
        select_date(driver, "1-Jul-2020", "21-Oct-2024")
        select_po_combined_status(driver)
        open_first_three_links(driver)

        for tab_index in range(1, len(driver.window_handles)):
            driver.switch_to.window(driver.window_handles[tab_index])
            # Wait for the page to load
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'c1-left')]")))
            found_po_combined, current_url = handle_show_more_and_check_po(driver)
            results.append((found_po_combined, current_url))

        # Generate the test summary
        test_summary = generate_test_summary(results)
        logging.info("\n" + test_summary)

        sleep(10)
    except Exception as e:
        logging.error(f"An unexpected error occurred in the main script: {str(e)}")
    finally:
        driver.quit()
