import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from time import sleep
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variables for tracking order numbers
po_number = None
so_number = None
test_results = {
    "po_test": {
        "number": None,
        "notifications": {
            "manager": {"checked": False, "found": False},
            "team_lead": {"checked": False, "found": False}
        }
    },
    "so_test": {
        "number": None,
        "notifications": {
            "sales_manager": {"checked": False, "found": False},
            "sales_rep": {"checked": False, "found": False}
        }
    }
}

# URL Constants
PO_URL = "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=830&company_id=67301"
SO_URL = "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=830&company_id=410593"
ADMIN_URL = "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=752"
NOTIFICATION_URL = "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=442"

def setup_driver():
    logging.info("Setting up the Chrome driver in headless mode")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')  # Новый синтаксис для headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome(options=options)

def login(driver, username, password, url=None):
    """
    Enhanced login function that handles different URLs for different workflows
    """
    logging.info(f"Logging in as {username}")
    if url:
        driver.get(url)
    try:
        username_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "login_name")))
        password_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "password")))
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()
        logging.info("Login successful")
        return True
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        return False

def check_notifications(driver, order_number):
    logging.info(f"Starting notification check for order number: {order_number}")
    try:
        notification_bell = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "notification_bell"))
        )
        notification_bell.click()
        logging.info("Clicked notification bell")
        sleep(3)

        notification_wrapper = driver.find_element(By.CLASS_NAME, "notification-wrapper")
        notifications = driver.find_elements(By.CSS_SELECTOR, ".b-container ul li")
        logging.info(f"Found {len(notifications)} notifications")

        for notification in notifications:
            notification_text = notification.text
            logging.info(f"Found notification text: {notification_text}")
            if order_number in notification_text and "has been canceled" in notification_text:
                logging.info(f"Found matching cancellation notification for order {order_number}")
                return True

        logging.warning(f"No matching notification found for order {order_number}")
        return False
    except Exception as e:
        logging.error(f"Error checking notifications: {str(e)}")
        return False

# PO-specific functions
def create_po_workflow(driver):
    try:
        # Generate Lead - click on initial button
        logging.info("Clicking Generate Lead button")
        generate_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btnMini3.nonico[href*='page_id=621']"))
        )
        generate_button.click()

        # Switch to new window
        logging.info("Switching to new window")
        wait = WebDriverWait(driver, 30)
        wait.until(lambda d: len(d.window_handles) > 1)

        # Store all window handles
        all_handles = driver.window_handles

        # Switch to the newest window (last handle)
        driver.switch_to.window(all_handles[-1])
        logging.info(f"Switched to window: {driver.current_url}")

        # Create Lead - find and click submit button with explicit wait
        logging.info("Looking for Create button")
        create_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary[type='submit']"))
        )
        logging.info("Clicking Create button")
        driver.execute_script("arguments[0].click();", create_button)
        sleep(15)

        # Create PO - find and click create_po button
        logging.info("Looking for Create PO button")
        create_po_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "create_po"))
        )
        logging.info("Clicking Create PO button")
        driver.execute_script("arguments[0].click();", create_po_button)
        sleep(5)

        # Confirm PO creation
        logging.info("Looking for Confirm PO button")
        create_confirm_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.create-po-btn"))
        )
        logging.info("Clicking Confirm PO button")
        driver.execute_script("arguments[0].click();", create_confirm_button)
        sleep(8)

        # Get PO number
        logging.info("Looking for PO number")
        po_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'text-nowrap')]/b[text()='PO:']/parent::div"))
        )
        number = po_element.text.replace('PO:', '').strip()
        logging.info(f"Successfully created PO number: {number}")
        test_results["po_test"]["number"] = number
        return number

    except Exception as e:
        logging.error(f"Error in PO workflow: {str(e)}")
        # Print the current URL to help with debugging
        try:
            logging.error(f"Current URL when error occurred: {driver.current_url}")
        except:
            logging.error("Could not get current URL")
        return None

# SO-specific functions
def create_so_workflow(driver):
    try:
        # Generate Sales Order
        generate_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btnMini3.nonico[href*='page_id=888'][href*='phase=new']"))
        )
        generate_button.click()
        wait = WebDriverWait(driver, 30)
        wait.until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[-1])

        # Create Sales Order
        create_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "surplus_order_btn"))
        )
        create_button.click()
        sleep(5)

        # Get SO number
        so_number_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-md-8 p.form-control-static"))
        )
        number = so_number_element.text.strip()
        logging.info(f"Created SO number: {number}")
        test_results["so_test"]["number"] = number
        return number
    except Exception as e:
        logging.error(f"Error in SO workflow: {str(e)}")
        return None

def cancel_po(driver):
    try:
        status_select = Select(WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "status_id"))
        ))
        status_select.select_by_value("34")
        sleep(2)

        update_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "result"))
        )
        update_button.click()
        sleep(5)
        return True
    except Exception as e:
        logging.error(f"Error canceling PO: {str(e)}")
        return False

def cancel_so(driver):
    try:
        cancel_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "cancel_order"))
        )
        cancel_button.click()
        sleep(2)

        reason_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "cancel_reason"))
        )
        reason_field.clear()
        reason_field.send_keys("TEST")
        sleep(2)

        send_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(@class, 'btn-primary')]"))
        )
        send_button.click()
        return True
    except Exception as e:
        logging.error(f"Error canceling SO: {str(e)}")
        return False

def run_admin_workflow(driver):
    """
    Enhanced admin workflow function with more reliable button clicking
    """
    try:
        if not login(driver, "dmitri.dubkovetki@mteam.md", "12", ADMIN_URL):
            return False
        sleep(5)

        # Click show button
        logging.info("Clicking 'Show' button")
        show_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "search_job_list"))
        )
        show_button.click()
        sleep(3)

        # Find notification hub updater row
        logging.info("Looking for Notification Hub Updater row")
        notification_row = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//tr[contains(., 'Notification Hub Updater')]"))
        )
        logging.info("Found Notification Hub Updater row")

        # Find and hover over tools button
        tools_button = notification_row.find_element(By.CSS_SELECTOR, "div.dropdown-hower a.btn-md")
        logging.info("Found tools button")

        # Create and perform hover action
        actions = ActionChains(driver)
        actions.move_to_element(tools_button).perform()
        logging.info("Hovering over tools button")
        sleep(3)  # Wait for dropdown to appear

        # Try to run the updater using JavaScript click
        try:
            logging.info("Attempting to click run button using JavaScript")
            run_button = driver.find_element(By.ID, "manual_run_link_145")
            driver.execute_script("arguments[0].click();", run_button)
            logging.info("Successfully clicked run button")
            sleep(15)  # Wait for action to complete
            return True

        except Exception as e:
            logging.error(f"Failed to click run button: {str(e)}")
            return False

    except Exception as e:
        logging.error(f"Error in admin workflow: {str(e)}")
        try:
            logging.error(f"Current URL when error occurred: {driver.current_url}")
        except:
            logging.error("Could not get current URL")
        return False

def generate_test_summary():
    has_errors = False
    summary = "\n=============== TEST EXECUTION SUMMARY ===============\n"

    # PO Test Summary
    summary += "\n[Purchase Order Test]\n"
    if test_results['po_test']['number'] is None:
        summary += "[FAILED] PO Creation Failed\n"
        has_errors = True
    else:
        summary += f"[SUCCESS] PO Number: {test_results['po_test']['number']}\n"

    summary += "\nNotifications:\n"
    # Manager notification
    if not test_results['po_test']['notifications']['manager']['found']:
        summary += "[FAILED] Manager Notification Not Found\n"
        has_errors = True
    else:
        summary += "[SUCCESS] Manager Notification Found\n"

    # Team lead notification
    if not test_results['po_test']['notifications']['team_lead']['found']:
        summary += "[FAILED] Team Lead Notification Not Found\n"
        has_errors = True
    else:
        summary += "[SUCCESS] Team Lead Notification Found\n"

    # SO Test Summary
    summary += "\n[Sales Order Test]\n"
    if test_results['so_test']['number'] is None:
        summary += "[FAILED] SO Creation Failed\n"
        has_errors = True
    else:
        summary += f"[SUCCESS] SO Number: {test_results['so_test']['number']}\n"

    summary += "\nNotifications:\n"
    # Sales manager notification
    if not test_results['so_test']['notifications']['sales_manager']['found']:
        summary += "[FAILED] Sales Manager Notification Not Found\n"
        has_errors = True
    else:
        summary += "[SUCCESS] Sales Manager Notification Found\n"

    # Sales rep notification
    if not test_results['so_test']['notifications']['sales_rep']['found']:
        summary += "[FAILED] Sales Rep Notification Not Found\n"
        has_errors = True
    else:
        summary += "[SUCCESS] Sales Rep Notification Found\n"

    summary += "\n=============== TEST EXECUTION COMPLETE ===============\n"

    if has_errors:
        summary += "\n[OVERALL STATUS: FAILED]\n"
    else:
        summary += "\n[OVERALL STATUS: SUCCESS]\n"

    return summary, has_errors

def main():
    has_error = False

    # PO Test (Buying workflow)
    driver = setup_driver()
    try:
        # Start with Buying Rep
        if login(driver, "user143287@mteam.test", "12", PO_URL):  # Silvia D (buying rep)
            global po_number
            po_number = create_po_workflow(driver)
            if po_number is None:
                logging.error("Failed to create PO")
                has_error = True
            elif not cancel_po(driver):
                logging.error("Failed to cancel PO")
                has_error = True
            else:
                logging.info(f"PO {po_number} created and canceled successfully")
        else:
            has_error = True
    except Exception as e:
        logging.error(f"Error in PO workflow: {str(e)}")
        has_error = True
    finally:
        driver.quit()

    # SO Test (Sales workflow)
    driver = setup_driver()
    try:
        # Start with Sales Rep
        if login(driver, "user439732@mteam.test", "12", SO_URL):  # Alexandr Sirbu (Sales Rep)
            global so_number
            so_number = create_so_workflow(driver)
            if so_number is None:
                logging.error("Failed to create SO")
                has_error = True
            elif not cancel_so(driver):
                logging.error("Failed to cancel SO")
                has_error = True
            else:
                logging.info(f"SO {so_number} created and canceled successfully")
        else:
            has_error = True
    except Exception as e:
        logging.error(f"Error in SO workflow: {str(e)}")
        has_error = True
    finally:
        driver.quit()

    # Admin workflow
    driver = setup_driver()
    try:
        if not run_admin_workflow(driver):
            logging.error("Admin workflow failed")
            has_error = True
    except Exception as e:
        logging.error(f"Error in admin workflow: {str(e)}")
        has_error = True
    finally:
        driver.quit()
        logging.info("Admin browser session closed")

    # Add pause after admin workflow
    logging.info("Waiting 25 seconds for notifications to process...")
    sleep(35)


# Check notifications
    notification_checks = [
        # PO Notifications (Buying)
        {
            "url": NOTIFICATION_URL,
            "username": "user51717@mteam.test",  # Dana (buying manager)
            "role": "manager",
            "order_type": "po_test",
            "order_number": po_number
        },
        {
            "url": NOTIFICATION_URL,
            "username": "user125900@mteam.test",  # Daniela P (Team Lead buying)
            "role": "team_lead",
            "order_type": "po_test",
            "order_number": po_number
        },
        # SO Notifications (Sales)
        {
            "url": NOTIFICATION_URL,
            "username": "user84031@mteam.test",  # Veronica Martiniuc (Sales Manager)
            "role": "sales_manager",
            "order_type": "so_test",
            "order_number": so_number
        },
        {
            "url": NOTIFICATION_URL,
            "username": "user89193@mteam.test",  # Natalia Sajin (Team lead Sales)
            "role": "sales_rep",
            "order_type": "so_test",
            "order_number": so_number
        }
    ]

    for check in notification_checks:
        driver = setup_driver()
        try:
            if login(driver, check["username"], "12", check["url"]):
                test_results[check["order_type"]]["notifications"][check["role"]]["checked"] = True
                notification_found = check_notifications(driver, check["order_number"])
                test_results[check["order_type"]]["notifications"][check["role"]]["found"] = notification_found
        except Exception as e:
            logging.error(f"Error checking notifications for {check['role']}: {str(e)}")
        finally:
            driver.quit()

    # Print summary and exit with appropriate code
    summary, summary_has_errors = generate_test_summary()
    print(summary)

    if has_error or summary_has_errors:
        logging.error("Test execution completed with errors")
        sys.exit(1)
    else:
        logging.info("Test execution completed successfully")
        sys.exit(0)
if __name__ == "__main__":
    main()
