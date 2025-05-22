# /common/pages/page_442/workflow/create_company/create_company_actions.py
"""
Workflow for company creation across multiple projects.
"""
import random
import string
import importlib
import time
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def create_company(driver, project_name, timeouts=None):
    """
    Creates a new company and returns the URL of the newly created company.
    Supports different projects through dynamic imports.
    
    Args:
        driver: Selenium WebDriver
        project_name: Project name (e.g., "ra_eu", "sm_us")
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        str: URL of the newly created company or None in case of error
    """
    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    company_timeout = timeouts.get("company", 25)
    navigation_timeout = timeouts.get("navigation", 25)

    try:
        # Dynamically import locators for the specified project
        try:
            locators_module = importlib.import_module(f"projects.{project_name}.pages.page_442.locators")
            Loc = getattr(locators_module, "CompanyCreationLocators")
        except (ImportError, AttributeError):
            return None
            
        # Dynamically import page URL for the specified project
        try:
            page_info_module = importlib.import_module(f"projects.{project_name}.pages.page_442.page_info")
            get_page_442_url = getattr(page_info_module, "get_page_442_url")
        except (ImportError, AttributeError):
            return None

        # Get URL for company creation page
        system_url = get_page_442_url(project_name)
        create_url = f"{system_url}&phase=new"
        driver.get(create_url)
        time.sleep(2)  # Allow time for initial page load

        # Wait for page to load and company name input element
        wait = WebDriverWait(driver, company_timeout)
        company_name_input = wait.until(
            EC.element_to_be_clickable(Loc.COMPANY_NAME_FIELD)
        )

        # Generate company data
        company_data = {
            'name': 'test' + ''.join(random.choices(string.ascii_letters + string.digits, k=5)),
            'address': 'test' + ''.join(random.choices(string.ascii_letters + string.digits, k=5)),
            'city': 'test' + ''.join(random.choices(string.ascii_letters + string.digits, k=5)),
            'postal_code': 'SW1W 0NY',
            'phone': ''.join(random.choices(string.digits, k=9)),
            'vat': 'GB' + ''.join(random.choices(string.digits, k=9))
        }

        # Fill in company name
        company_name_input.send_keys(company_data['name'])
        time.sleep(1)

        # Select country
        country_select = wait.until(
            EC.element_to_be_clickable(Loc.COUNTRY_INFO_DROPDOWN)
        )
        Select(country_select).select_by_value('224')  # United Kingdom
        time.sleep(1)

        # Select segmentation
        segmentation_select = wait.until(
            EC.element_to_be_clickable(Loc.SEGMENTATION_DROPDOWN)
        )
        Select(segmentation_select).select_by_value('1')
        time.sleep(1)

        # Fill in address
        address_input = wait.until(
            EC.element_to_be_clickable(Loc.ADDRESS_LINE_ONE_FIELD)
        )
        address_input.send_keys(company_data['address'])
        time.sleep(1)

        # Fill in city
        city_input = wait.until(
            EC.element_to_be_clickable(Loc.CITY_FIELD)
        )
        city_input.send_keys(company_data['city'])
        time.sleep(1)

        # Fill in postal code
        postal_code_input = wait.until(
            EC.element_to_be_clickable(Loc.ADDRESS_POSTAL_CODE_FIELD)
        )
        postal_code_input.send_keys(company_data['postal_code'])
        time.sleep(1)

        # Fill in phone
        phone_input = wait.until(
            EC.element_to_be_clickable(Loc.CONTACT_PHONE_NUMBER_FIELD)
        )
        phone_input.send_keys(company_data['phone'])
        time.sleep(1)

        # Fill in VAT number (if field is available)
        try:
            vat_input = wait.until(
                EC.element_to_be_clickable(Loc.VAT_NUMBER_FIELD)
            )
            vat_input.send_keys(company_data['vat'])
            time.sleep(1)
        except TimeoutException:
            pass

        # Click create company button
        create_button = wait.until(
            EC.element_to_be_clickable(Loc.CREATE_COMPANY_BUTTON)
        )
        create_button.click()

        # Wait for new tab to open
        navigation_wait = WebDriverWait(driver, navigation_timeout)
        navigation_wait.until(lambda d: len(d.window_handles) > 1)

        # Switch to new tab
        new_window = driver.window_handles[-1]
        driver.switch_to.window(new_window)

        # Allow time for company page to load
        time.sleep(5)
        
        # Get URL of new company
        company_url = driver.current_url
        
        return company_url

    except (TimeoutException, Exception):
        return None