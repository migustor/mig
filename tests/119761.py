import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import time

# Login credentials
LOGIN_EMAIL = "dmitri.dubkovetki@mteam.md"
PASSWORD = "12"

# Target systems with specific links
systems = [
    {
        'name': 'RA',
        'login_url': 'https://stage15.office.ratrading.eu/sage/index.cfm?page_id=442',
        'check_url': 'https://stage15.office.ratrading.eu/sage/index.cfm?page_id=714&item_id=239'
    },
    {
        'name': 'Sovamax',
        'login_url': 'https://stage15.office.sovasystem.com/sage/index.cfm?page_id=442',
        'check_url': 'https://stage15.office.sovasystem.com/sage/index.cfm?page_id=714&item_id=239'
    },
    {
        'name': 'Atlas',
        'login_url': 'https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=442',
        'check_url': 'https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=714&item_id=239'
    },
    {
        'name': 'Eminia',
        'login_url': 'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=442',
        'check_url': 'https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=714&proxy_set_id=2&item_id='
    },
    {
        'name': 'Lanius',
        'login_url': 'https://stage15.office.laniustoys.com/sage/index.cfm?page_id=442',
        'check_url': 'https://stage15.office.laniustoys.com/sage/index.cfm?page_id=714&item_id=239'
    },
    {
        'name': 'DbReactor',
        'login_url': 'https://stage15.office.dbreactor.com/sage/index.cfm?page_id=442',
        'check_url': 'https://stage15.office.dbreactor.com/sage/index.cfm?page_id=714&item_id=239'
    },
    {
        'name': 'Horus',
        'login_url': 'https://stage15.office.horustrading.eu/sage/index.cfm?page_id=442',
        'check_url': 'https://stage15.office.horustrading.eu/sage/index.cfm?page_id=714&item_id=239'
    },
    {
        'name': 'SovamaxUSA',
        'login_url': 'https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=442',
        'check_url': 'https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=714&item_id=239'
    }
]

# Dictionary to store test results
test_results = {}
test_failed = False  # Flag to track if any test failed

def login_and_check(system):
    """
    Logs in to the specified system and checks the Surplus Sales and Demand Overview elements.
    Returns a dict: {
        "Surplus Sales Clickable": bool,
        "Demand Overview Clickable": bool
    } 
    or raises TimeoutException/ElementNotInteractableException if something fails.
    """
    driver = webdriver.Chrome()  # Using Chrome WebDriver
    wait = WebDriverWait(driver, 15)  # 15-second wait might help with slower pages
    try:
        # 1) Navigate to login page
        driver.get(system['login_url'])
        time.sleep(2)  # Just in case there's a quick load or redirect

        # 2) Enter login details
        wait.until(EC.presence_of_element_located((By.ID, "login_name"))).send_keys(LOGIN_EMAIL)
        wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD + Keys.RETURN)

        # 3) Go to the check URL
        driver.get(system['check_url'])
        time.sleep(2)  # A short pause to ensure the page starts loading

        # 4) Wait for the two elements we need
        surplus_sales = wait.until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Surplus Sales')]"))
        )
        demand_overview = wait.until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Demand Overview')]"))
        )

        # Build results dictionary
        result = {
            "Surplus Sales Clickable": surplus_sales.is_enabled(),
            "Demand Overview Clickable": demand_overview.is_enabled()
        }
        return result

    finally:
        # Always quit the driver in this function
        driver.quit()

def check_system(system):
    """
    Retries the entire process (login + check) if TimeoutException or ElementNotInteractableException
    is thrown, up to max_retries.
    """
    global test_failed
    max_retries = 3

    print(f"Processing {system['name']}...")

    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            print(f"  - Attempt {attempt} of {max_retries}...")
            result = login_and_check(system)

            # If we got here, it means we successfully logged in and found elements
            test_results[system['name']] = result
            print(f"    Surplus Sales: {'Clickable' if result['Surplus Sales Clickable'] else 'Not Clickable'}")
            print(f"    Demand Overview: {'Clickable' if result['Demand Overview Clickable'] else 'Not Clickable'}")

            # Mark test as failed if either element is not clickable
            if not result['Surplus Sales Clickable'] or not result['Demand Overview Clickable']:
                print("    Test Failed")
                test_failed = True
            return  # Stop retrying—this system is done

        except (TimeoutException, ElementNotInteractableException) as e:
            last_exception = e
            print(f"    Attempt {attempt} failed with error: {e}")
            if attempt < max_retries:
                print("    Retrying the entire flow...")
            else:
                print("    Max retries reached. This system test failed.")
                test_results[system['name']] = {
                    "Surplus Sales Clickable": False,
                    "Demand Overview Clickable": False
                }
                print("    Test Failed")
                test_failed = True


# Iterate through all systems
for system in systems:
    check_system(system)

# Print summary
print("\nTest Summary:")
for system_name, result in test_results.items():
    print(f"{system_name}:")
    print(f"  - Surplus Sales Clickable: {'Yes' if result['Surplus Sales Clickable'] else 'No'}")
    print(f"  - Demand Overview Clickable: {'Yes' if result['Demand Overview Clickable'] else 'No'}")

# Raise exception or exit if any test failed, otherwise print success
if test_failed:
    print("\nOne or more tests have failed. Check the logs for details.")
    sys.exit(1)
else:
    print("\nAll tests passed successfully!")
