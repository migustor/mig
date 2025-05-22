from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
import re
import threading
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Driver setup options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run Chrome in headless mode

# Function to perform testing on a set of links
def test_links(links, category_name, test_summaries):
    driver = webdriver.Chrome(options=options)
    try:
        # Perform login on the first link
        logging.info(f"Opening the first link in {category_name} and performing login...")
        driver.get(links[0])

        # Enter login and password
        logging.info("Entering login credentials...")
        login_field = driver.find_element(By.ID, "login_name")
        password_field = driver.find_element(By.ID, "password")

        login_field.send_keys("valeriu.bistritchi@mteam.md")
        password_field.send_keys("12")

        # Click the Submit button
        logging.info("Clicking the submit button...")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Iterate through each link and check for the button
        for index, link in enumerate(links):
            logging.info(f"Opening link {index + 1} ({category_name}): {link}")
            driver.get(link)

            # Extract project ID from the link
            project_id_match = re.search(r'project_id=([a-zA-Z0-9_]+)', link)
            project_id = project_id_match.group(1) if project_id_match else "Unknown"

            # Wait for the page to load completely
            logging.info("Waiting for the page to load...")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

            if category_name == "Child SO":
                # For the third category of links, wait for the specific element and then check for the absence of the return button
                try:
                    logging.info("Waiting for the panel to appear...")
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".panel.panel-default.so_document_file_div"))
                    )
                    logging.info("Panel appeared, checking for absence of the add_return_button_...")
                    driver.find_element(By.CSS_SELECTOR, "button[id^='add_return_button_']")
                    logging.error(f"{project_id} Return function found - FAILED")
                    test_summaries.append(f"{project_id} Return function found - FAILED")
                except TimeoutException:
                    logging.info(f"{project_id} Return function missing as expected - SUCCESS")
                    test_summaries.append(f"{project_id} Return function missing as expected - SUCCESS")
                except Exception:
                    logging.info(f"{project_id} Return function missing as expected - SUCCESS")
                    test_summaries.append(f"{project_id} Return function missing as expected - SUCCESS")
            else:
                # Для первых двух категорий ссылок, кнопка должна присутствовать
                logging.info("Checking for the presence of the add_return_button_...")

                max_attempts = 3
                attempt = 0
                found_button = False
    
                while attempt < max_attempts and not found_button:
                    try:
                        # Ждём появления элемента 20 секунд
                        add_return_button = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "button[id^='add_return_button_']"))
                        )
                        logging.info(f"{project_id} Return function found - SUCCESS")
                        test_summaries.append(f"{project_id} Return function found - SUCCESS")
                        found_button = True
                    except TimeoutException:
                        attempt += 1
                        # Если не достигли максимума попыток — перезагружаем страницу и пробуем снова
                        if attempt < max_attempts:
                            logging.warning(
                                f"Attempt {attempt}/{max_attempts}: Element not found. Reloading the page and retrying..."
                            )
                            driver.refresh()
                        else:
                            logging.error(f"{project_id} Return function missing - FAILED")
                            test_summaries.append(f"{project_id} Return function missing - FAILED")

    finally:
        # Close the driver
        logging.info(f"Closing the driver for {category_name}...")
        driver.quit()

# Links to be tested
links_solo = [
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=605056&project_id=sm_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=34316&project_id=sm_us&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=100430&project_id=ra_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=50202&project_id=ag_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=276283&project_id=et_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=87956&project_id=lt_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=1060&project_id=dr_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=793&project_id=ho_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=435&project_id=at_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=34&project_id=argon&order_type=so"
]

links_main = [
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=605057&project_id=sm_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=34317&project_id=sm_us&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=100431&project_id=ra_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=50203&project_id=ag_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=276284&project_id=et_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=87957&project_id=lt_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=1061&project_id=dr_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=794&project_id=ho_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=442&project_id=at_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=35&project_id=argon&order_type=so"
]

links_child = [
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=605058&project_id=sm_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=34318&project_id=sm_us&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=100432&project_id=ra_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=50204&project_id=ag_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=276285&project_id=et_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=87958&project_id=lt_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=1062&project_id=dr_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=795&project_id=ho_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=443&project_id=at_eu&order_type=so",
    "https://stage15.office.grafit.md/sage/index.cfm?page_id=907&so_id=36&project_id=argon&order_type=so"
]

# Start threads for each set of links
threads = []
test_summaries_solo = []
test_summaries_main = []
test_summaries_child = []

threads.append(threading.Thread(target=test_links, args=(links_solo, "Solo SO", test_summaries_solo)))
threads.append(threading.Thread(target=test_links, args=(links_main, "Main SO", test_summaries_main)))
threads.append(threading.Thread(target=test_links, args=(links_child, "Child SO", test_summaries_child)))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

# Print all test summaries at the end
logging.info("Printing all test summaries...")
print("\n=== FINAL TEST SUMMARY ===")
print("\n=== TEST SUMMARY for Solo SO ===")
for summary in test_summaries_solo:
    print(summary)
print("\n=== TEST SUMMARY for Main SO ===")
for summary in test_summaries_main:
    print(summary)
print("\n=== TEST SUMMARY for Child SO ===")
for summary in test_summaries_child:
    print(summary)

# Check for any failed tests and set exit code accordingly
if any("FAILED" in summary for summary in (test_summaries_solo + test_summaries_main + test_summaries_child)):
    sys.exit(1)
