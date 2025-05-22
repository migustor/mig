from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import time
import sys
import os
from datetime import datetime
import uuid

# Импорт функций управления драйвером из driver_setup
from common.utils.driver_setup import setup_chrome_driver, release_driver, with_driver

TEST_ID = f"123320_test_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Настройка директории для скриншотов
screenshot_dir = r"J:\PUB5\E2E_Testing"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Упрощенные таймауты для разных операций
TIMEOUTS = {
    "login": 15,         # Таймаут для элементов логина
    "page_load": 40,     # Таймаут для загрузки страницы
    "elements": 30,      # Таймаут для элементов страницы
    "toolbox": 30,       # Таймаут для элементов тулбокса
    "navigation": 30,    # Таймаут для элементов навигации
    "totals": 20         # Таймаут для элементов с итогами
}

def take_error_screenshot(driver, name, project_name=None):
    """Делает скриншот страницы при ошибке"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if project_name:
        filename = os.path.join(SCREENSHOT_DIR, f"error_{project_name}_{name}_{timestamp}.png")
    else:
        filename = os.path.join(SCREENSHOT_DIR, f"error_{name}_{timestamp}.png")
    
    try:
        driver.save_screenshot(filename)
        logging.info(f"Error screenshot saved to {filename}")
        return filename
    except Exception as e:
        logging.error(f"Failed to take error screenshot: {str(e)}")
        return None

@dataclass
class Project:
    name: str
    url: str
    restricted_user: str
    po_id: str
    
# Projects configuration
PROJECTS = [
    Project(
        name="Agava",
        url="https://stage15.office.agavasystem.com",
        restricted_user="user272167@mteam.test",
        po_id="4461"
    ),
    Project(
        name="Sova USA",
        url="https://stage15.office.sovamaxusa.com",
        restricted_user="user1161186@mteam.test",
        po_id="4441"
    ),
    Project(
        name="Eminia",
        url="https://stage15.office.eminiasystem.com",
        restricted_user="user383691@mteam.test",
        po_id="132642"
    ),
    Project(
        name="Lanius",
        url="https://stage15.office.laniustoys.com",
        restricted_user="user19129@mteam.test",
        po_id="41638"
    ),
    Project(
        name="DB Reactor",
        url="https://stage15.office.dbreactor.com",
        restricted_user="user83003@mteam.test",
        po_id="609"
    ),
    Project(
        name="Horus",
        url="https://stage15.office.horustrading.eu",
        restricted_user="user63226@mteam.test",
        po_id="715"
    ),
    Project(
        name="Atlas",
        url="https://stage15.office.atlastradingworld.com",
        restricted_user="user123825@mteam.test",
        po_id="221"
    ),
    Project(
        name="RA",
        url="https://stage15.office.ratrading.eu/",
        restricted_user="user253890@mteam.test",
        po_id="44556"
    )
]

# Admin configuration
ADMIN_USER = {
    "username": "maxim.lupan@mteam.md",
    "password": "12"
}

class CustomFormatter(logging.Formatter):
    def format(self, record):
        message = record.getMessage()
        if "Error processing toolbox" in message or "error_toolbox_error" in message:
            return ""
        return super().format(record)

def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    for handler in logging.getLogger().handlers:
        handler.setFormatter(CustomFormatter('%(asctime)s - %(levelname)s - %(message)s'))

def login(driver, username, password, project: Project) -> bool:
    """Login to specific project"""
    logging.info(f"Logging in as {username} to {project.name}")
    driver.get(f"{project.url}/sage/index.cfm?page_id=839&po_id={project.po_id}")
    try:
        username_input = WebDriverWait(driver, TIMEOUTS["login"]).until(
            EC.presence_of_element_located((By.ID, "login_name"))
        )
        password_input = WebDriverWait(driver, TIMEOUTS["login"]).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()
        logging.info("Login successful.")
        time.sleep(2)
        return True
    except TimeoutException:
        logging.error(f"Timeout occurred while logging in to {project.name}")
        take_error_screenshot(driver, "login_timeout", project.name)
        return False
    except Exception as e:
        logging.error(f"Error during login to {project.name}: {str(e)}")
        take_error_screenshot(driver, "login_error", project.name)
        return False

def generate_test_summary(project_results: Dict[str, Dict]) -> str:
    """Generates brief report of test results"""
    summary = "\n=== TEST SUMMARY ===\n"

    for project_name, result in project_results.items():
        summary += f"\n{project_name}:\n"

        if not result.get("login_success", False):
            summary += "[-] Login Failed\n"
            if result.get("error_screenshots"):
                summary += f"    - Error Screenshots: {', '.join(result.get('error_screenshots'))}\n"
            continue

        # Check main sections
        sections = {
            "TABS": result.get("restricted_tabs", []),
            "PANELS": result.get("restricted_panels", []),
            "BUTTONS": result.get("restricted_buttons", []),
            "COLUMNS": result.get("restricted_columns", []),
            "TOOLBOX": result.get("restricted_actions", []),
            "TOTALS": result.get("restricted_totals", [])
        }

        for section_name, violations in sections.items():
            if violations:
                summary += f"[-] {section_name}: Found {len(violations)} violation(s)\n"
            else:
                summary += f"[+] {section_name}: OK\n"

        # Overall project status
        if result.get("passed", False):
            summary += "[+] OVERALL: PASSED\n"
        else:
            summary += "[-] OVERALL: FAILED\n"
            if result.get("error_screenshots"):
                summary += f"    - Error Screenshots: {', '.join(result.get('error_screenshots'))}\n"

    return summary

def print_access_comparison(user1: str, user2: str, user1_data: Dict, user2_data: Dict):
    """Prints access rights comparison to console"""
    print(f"\n=== Access Rights Comparison between {user1} and {user2} ===")

    # Check restrictions for second user
    restricted_elements = validate_restricted_access(user2_data)
    if restricted_elements:
        print("\n VALIDATION FAILED!")
        print(f"\nRestricted elements found for user {user2}:")
        for element in restricted_elements:
            print(f"  • {element}")
        print("\nDetailed elements comparison:")

    # First display specific toolbox information
    print("\n=== Specific Toolbox Content (tools_36396) ===")
    print(f"\nActions available for {user1}:")
    for action in sorted(user1_data['specific_toolbox']):
        print(f"  • {action}")

    print(f"\nActions available for {user2}:")
    for action in sorted(user2_data['specific_toolbox']):
        print(f"  • {action}")

    specific_diff1 = set(user1_data['specific_toolbox']) - set(user2_data['specific_toolbox'])
    specific_diff2 = set(user2_data['specific_toolbox']) - set(user1_data['specific_toolbox'])

    if specific_diff1 or specific_diff2:
        print("\nDifferences in specific toolbox actions:")
        if specific_diff1:
            print(f"\nOnly in {user1}:")
            for action in sorted(specific_diff1):
                print(f"  • {action}")
        if specific_diff2:
            print(f"\nOnly in {user2}:")
            for action in sorted(specific_diff2):
                print(f"  • {action}")

    print("\n=== General Elements Comparison ===")

    element_types = {
        'buttons': 'Buttons',
        'tabs': 'Tabs',
        'panels': 'Panels',
        'table_columns': 'Table Columns',
        'inputs': 'Input Fields',
        'totals': 'Total Values'
    }

    for element_type, display_name in element_types.items():
        set1 = set(user1_data[element_type])
        set2 = set(user2_data[element_type])

        unique_to_user1 = set1 - set2
        unique_to_user2 = set2 - set1

        if unique_to_user1 or unique_to_user2:
            print(f"\n{display_name}:")

            if unique_to_user1:
                print(f"\nAvailable only for {user1}:")
                for item in sorted(unique_to_user1):
                    print(f"  • {item}")

            if unique_to_user2:
                print(f"\nAvailable only for {user2}:")
                for item in sorted(unique_to_user2):
                    print(f"  • {item}")

def check_project_access(driver, project: Project) -> Dict:
    """Check access rights for specific project"""
    print(f"\nTesting {project.name}...")
    results = {
        "name": project.name,
        "login_success": True,
        "passed": True,
        "error_screenshots": []
    }

    # Store original handle
    main_window = driver.current_window_handle
    admin_elements = None

    # Step 1: Login as admin in main tab
    try:
        if login(driver, ADMIN_USER["username"], ADMIN_USER["password"], project):
            admin_elements = get_page_elements(driver, project.name)
            # Log out from main tab after collecting admin elements
            driver.delete_all_cookies()
            driver.get("about:blank")
        else:
            results["login_success"] = False
            results["passed"] = False
            return results
    except Exception as e:
        logging.error(f"Error during admin check for {project.name}: {str(e)}")
        screenshot_path = take_error_screenshot(driver, "admin_error", project.name)
        if screenshot_path:
            results.setdefault("error_screenshots", []).append(screenshot_path)
        results["login_success"] = False
        results["passed"] = False
        return results

    # Step 2: Login as restricted user in main tab
    try:
        if login(driver, project.restricted_user, "12", project):
            restricted_elements = get_page_elements(driver, project.name)
            # Check for restricted access
            violation_checks = validate_restricted_access(restricted_elements)
            if violation_checks:
                results["passed"] = False
                # Take screenshot when violations found
                screenshot_path = take_error_screenshot(driver, "restricted_access", project.name)
                if screenshot_path:
                    results.setdefault("error_screenshots", []).append(screenshot_path)
                
                # Group violations by type
                for violation in violation_checks:
                    if "tab found" in violation:
                        results.setdefault("restricted_tabs", []).append(violation)
                    elif "panel found" in violation:
                        results.setdefault("restricted_panels", []).append(violation)
                    elif "button found" in violation:
                        results.setdefault("restricted_buttons", []).append(violation)
                    elif "column found" in violation:
                        results.setdefault("restricted_columns", []).append(violation)
                    elif "toolbox action found" in violation:
                        results.setdefault("restricted_actions", []).append(violation)
                    elif "total value found" in violation:
                        results.setdefault("restricted_totals", []).append(violation)
            
            # Clear session for next project
            driver.delete_all_cookies()
            driver.get("about:blank")
        else:
            results["login_success"] = False
            results["passed"] = False
    except Exception as e:
        logging.error(f"Error in restricted user check for {project.name}: {str(e)}")
        screenshot_path = take_error_screenshot(driver, "restricted_user_error", project.name)
        if screenshot_path:
            results.setdefault("error_screenshots", []).append(screenshot_path)
        results["login_success"] = False
        results["passed"] = False

    return results

def get_specific_toolbox_content(driver, project_name=None) -> List[str]:
    """Get content of specific toolbox"""
    toolbox_actions = []
    try:
        toolbox = WebDriverWait(driver, TIMEOUTS["toolbox"]).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.floatRight#tools_36396"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", toolbox)
        time.sleep(2)
        cog_icon = toolbox.find_element(By.CSS_SELECTOR, ".dropdown-hower a")
        actions = webdriver.ActionChains(driver)
        actions.move_to_element(cog_icon).perform()
        time.sleep(2)
        menu_items = WebDriverWait(driver, TIMEOUTS["toolbox"]).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.floatRight#tools_36396 .dropdown-menu li a"))
        )
        for item in menu_items:
            action_text = item.get_attribute('title') or item.text.strip()
            if action_text:
                toolbox_actions.append(action_text)
    except Exception as e:
        # Simply return empty list without logging or taking screenshots
        pass
    return toolbox_actions

def validate_restricted_access(elements: Dict[str, List[str]]) -> List[str]:
    """Check for presence of restricted elements"""
    restricted_elements = []

    # Check restricted tabs
    restricted_tabs = {"Lead Notes", "Chat Logistics", "Claim PO Notes"}
    for tab in elements['tabs']:
        if any(r_tab.lower() in tab.lower() for r_tab in restricted_tabs):
            restricted_elements.append(f"Restricted tab found: {tab}")

    # Check restricted panels (exact match for Transactions)
    restricted_panels = {"PO Related Files", "PO Actions", "Transactions"}
    for panel in elements['panels']:
        if panel.strip() == "Transactions":
            restricted_elements.append(f"Restricted panel found: {panel}")
        elif any(r_panel.lower() in panel.lower() for r_panel in {"PO Related Files", "PO Actions"}):
            restricted_elements.append(f"Restricted panel found: {panel}")

    # Check restricted buttons
    restricted_buttons = {"Recalculate", "Remove Selected", "Move Items to Another PO"}
    for button in elements['buttons']:
        if any(r_button.lower() in button.lower() for r_button in restricted_buttons):
            restricted_elements.append(f"Restricted button found: {button}")

    # Check restricted columns
    restricted_columns = {"Max Buy", "Price", "Ext. Price"}
    for column in elements['table_columns']:
        if any(r_col.lower() in column.lower() for r_col in restricted_columns):
            restricted_elements.append(f"Restricted column found: {column}")

    # Check restricted toolbox actions
    restricted_actions = {"Delete Item from PO"}
    for action in elements['specific_toolbox']:
        if any(r_action.lower() in action.lower() for r_action in restricted_actions):
            restricted_elements.append(f"Restricted toolbox action found: {action}")

    # Check restricted total values
    restricted_totals = {"Total Surplus Max Buy Value", "Total PO Value"}
    for total in elements['totals']:
        if any(r_total.lower() in total.lower() for r_total in restricted_totals):
            restricted_elements.append(f"Restricted total value found: {total}")

    return restricted_elements

def get_page_elements(driver, project_name=None) -> Dict[str, List[str]]:
    """Collect information about available page elements"""
    elements_info = {
        'buttons': [],
        'tabs': [],
        'panels': [],
        'table_columns': [],
        'specific_toolbox': [],
        'inputs': [],
        'totals': []
    }

    try:
        WebDriverWait(driver, TIMEOUTS["page_load"]).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        
        try:
            buttons = WebDriverWait(driver, TIMEOUTS["elements"]).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
            )
            elements_info['buttons'] = [btn.text or btn.get_attribute('value') or btn.get_attribute('id')
                                      for btn in buttons if btn.text or btn.get_attribute('value') or btn.get_attribute('id')]
        except TimeoutException:
            logging.error("Timeout while finding buttons")
            if project_name:
                take_error_screenshot(driver, "buttons_timeout", project_name)
        
        try:
            tabs = WebDriverWait(driver, TIMEOUTS["navigation"]).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".nav-tabs li a"))
            )
            elements_info['tabs'] = [tab.text.strip() for tab in tabs if tab.text.strip()]
        except TimeoutException:
            logging.error("Timeout while finding tabs")
            if project_name:
                take_error_screenshot(driver, "tabs_timeout", project_name)
        
        try:
            panels = WebDriverWait(driver, TIMEOUTS["elements"]).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".panel-heading h4"))
            )
            elements_info['panels'] = [panel.text.strip() for panel in panels if panel.text.strip()]
        except TimeoutException:
            logging.error("Timeout while finding panels")
            if project_name:
                take_error_screenshot(driver, "panels_timeout", project_name)
        
        try:
            table_headers = WebDriverWait(driver, TIMEOUTS["elements"]).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".table th"))
            )
            elements_info['table_columns'] = [header.text.strip() for header in table_headers if header.text.strip()]
        except TimeoutException:
            logging.error("Timeout while finding table headers")
            if project_name:
                take_error_screenshot(driver, "headers_timeout", project_name)
        
        elements_info['specific_toolbox'] = get_specific_toolbox_content(driver, project_name)
        
        try:
            inputs = WebDriverWait(driver, TIMEOUTS["elements"]).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
            )
            elements_info['inputs'] = [inp.get_attribute('id') or inp.get_attribute('name')
                                     for inp in inputs if inp.get_attribute('id') or inp.get_attribute('name')]
        except TimeoutException:
            logging.error("Timeout while finding inputs")
            if project_name:
                take_error_screenshot(driver, "inputs_timeout", project_name)
        
        total_elements = [
            ("total_line_items", "Total # of Line Items"),
            ("total_po_shipp_weight", "Total weight (kg)"),
            ("total_nbr_of_units", "Total # of Units"),
            ("total_mb", "Total Surplus Max Buy Value"),
            ("total_po_value", "Total PO Value")
        ]
        
        for element_id, label in total_elements:
            try:
                element = WebDriverWait(driver, TIMEOUTS["totals"]).until(
                    EC.presence_of_element_located((By.ID, element_id))
                )
                if element.is_displayed():
                    elements_info['totals'].append(f"{label}: {element.text}")
            except TimeoutException:
                continue
            except Exception as e:
                logging.error(f"Error finding total element {element_id}: {str(e)}")
                continue
    except Exception as e:
        logging.error(f"Error collecting page elements: {str(e)}")
        if project_name:
            take_error_screenshot(driver, "page_elements_error", project_name)
            
    return elements_info

def main():
    setup_logging()
    project_results = {}
    has_failures = False

    # Get driver with test_id
    driver = setup_chrome_driver(headless=True, test_id=TEST_ID)
    logger.info(f"Starting test execution with ID: {TEST_ID}")
    
    try:
        for project in PROJECTS:
            logger.info(f"Testing project: {project.name}")
            project_results[project.name] = check_project_access(driver, project)
            if not project_results[project.name]["passed"]:
                has_failures = True
                logger.error(f"Project {project.name} failed validation")
                if "error_screenshots" in project_results[project.name]:
                    for screenshot in project_results[project.name]["error_screenshots"]:
                        logger.info(f"Error screenshot: {screenshot}")

        summary = generate_test_summary(project_results)
        print(summary)
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        sys.exit(1)
    finally:
        release_driver(driver)

    if has_failures:
        sys.exit(1)
    else:
        print("All projects passed validation!")
        sys.exit(0)

if __name__ == "__main__":
    main()