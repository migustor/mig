from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from typing import Tuple
import logging
import time

SITES = {
    "RA Trading": {
        "url": "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=714&item_id=14708",
        "username": "maxim.lupan@mteam.md",
        "password": "12"
    },
    "Lanius": {
        "url": "https://stage15.office.laniustoys.com/sage/index.cfm?page_id=714&item_id=199981",
        "username": "maxim.lupan@mteam.md",
        "password": "12"
    },
    "DB Reactor": {
        "url": "https://stage15.office.dbreactor.com/sage/index.cfm?page_id=714&item_id=45960",
        "username": "maxim.lupan@mteam.md",
        "password": "12"
    },
    "Horus": {
        "url": "https://stage15.office.horustrading.eu/sage/index.cfm?page_id=714&item_id=95618",
        "username": "maxim.lupan@mteam.md",
        "password": "12"
    },
    "Eminia": {
        "url": "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=714&item_id=10354716",
        "username": "maxim.lupan@mteam.md",
        "password": "12",
        "default_values": {
            "lead_date_diff": "24",    # 2 years
            "sales_date_diff": "6",     # 6 months
            "presale_statistics_date_diff": "6"  # 6 months (updated from date_diff)
        }
    }
}

class SPMPageTester:
    def __init__(self):
        self.setup_logging()
        self.driver = self.setup_driver()
        self.main_window = None
        self.verification_window = None
        self.test_states = {}
        self.initial_states = {}
        self.current_site = None

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--headless=new')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-application-cache')  # Отключаем кеш

        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd('Network.clearBrowserCache', {})  # Очищаем кеш браузера
        return driver

    def wait_for_ajax(self):
        """Enhanced wait for AJAX with state check"""
        try:
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script("""
                return (window.jQuery === undefined || jQuery.active === 0) &&
                       document.readyState === 'complete';
            """))
        # Дополнительное ожидание для стабилизации
            time.sleep(6)
            return True
        except Exception as e:
            logging.warning(f"Wait for AJAX completion failed: {str(e)}")
            return False

    def open_verification_tab(self, url):
        """Open a new tab for verification"""
        self.driver.execute_script("window.open('');")
        self.verification_window = self.driver.window_handles[-1]
        self.driver.switch_to.window(self.verification_window)
        self.driver.get(url)
        time.sleep(2)

    def switch_to_main_tab(self):
        """Switch back to the main tab"""
        self.driver.switch_to.window(self.main_window)

    def switch_to_verification_tab(self):
        """Switch to the verification tab"""
        self.driver.switch_to.window(self.verification_window)

    def get_initial_state(self, element_id: str, is_checkbox: bool = False) -> any:
        """Get and store initial state of an element"""
        if is_checkbox:
            state = self.driver.execute_script(f"return document.getElementById('{element_id}').checked")
        else:
            state = self.driver.execute_script(f"return document.getElementById('{element_id}').value")
        self.initial_states[element_id] = state
        logging.info(f"Stored initial state for {element_id}: {state}")
        return state

    def toggle_checkbox_js(self, checkbox_id, function_name) -> bool:
        """Toggle checkbox to opposite state and verify it's saved"""
        try:
            wait = WebDriverWait(self.driver, 20)
            logging.info(f"Waiting for checkbox {checkbox_id} to be present...")
            wait.until(EC.presence_of_element_located((By.ID, checkbox_id)))

            # Получаем текущее состояние и меняем на противоположное
            toggle_script = f"""
            const checkbox = document.getElementById('{checkbox_id}');
            const currentState = checkbox.checked;
            const newState = !currentState;

            // Меняем на противоположное состояние
            checkbox.checked = newState;

            // Вызываем события
            ['change', 'click', 'input'].forEach(eventName => {{
                const event = new Event(eventName, {{ bubbles: true }});
                checkbox.dispatchEvent(event);
            }});

            // Вызываем функцию обратного вызова
            if (typeof {function_name} === 'function') {{
                {function_name}();
            }}

            return {{
                initialState: currentState,
                newState: newState
            }};
            """

            result = self.driver.execute_script(toggle_script)
            logging.info(f"Initial state: {result['initialState']}, Changed to: {result['newState']}")

            # Ждем завершения AJAX
            self.wait_for_ajax()
            time.sleep(6)  # Дополнительное время для обработки

            # Проверяем, что состояние изменилось на желаемое
            final_state = self.driver.execute_script(f"""
                const checkbox = document.getElementById('{checkbox_id}');
                return checkbox.checked;
            """)

            # Сохраняем новое состояние для последующей проверки
            self.test_states[checkbox_id] = final_state

            logging.info(f"Final state of {checkbox_id}: {final_state}")
            return final_state

        except Exception as e:
            logging.error(f"Error toggling checkbox {checkbox_id}: {str(e)}", exc_info=True)
            if not hasattr(self, 'test_states'):
                self.test_states = {}
            self.test_states[checkbox_id] = None
            return False

    def toggle_select_js(self, select_id, function_name) -> str:
        """Change select to next available value using JavaScript"""
        initial_value = self.get_initial_state(select_id)

        js_script = f"""
        const select = document.getElementById('{select_id}');
        const currentValue = select.value;
        const options = Array.from(select.options).map(opt => opt.value);
        const currentIndex = options.indexOf(currentValue);
        const nextValue = options[(currentIndex + 1) % options.length];
        return {{
            initial: currentValue,
            nextValue: nextValue
        }};
        """

        state = self.driver.execute_script(js_script)

        change_script = f"""
        const select = document.getElementById('{select_id}');
        select.value = '{state['nextValue']}';
        const event = new Event('change', {{ bubbles: true }});
        select.dispatchEvent(event);
        if (typeof {function_name} === 'function') {{
            {function_name}();
        }}
        return select.value;
        """
        new_value = self.driver.execute_script(change_script)
        logging.info(f"Changed {select_id} from {initial_value} to {new_value}")

        self.wait_for_ajax()
        time.sleep(6)

        # For Eminia, use default values where applicable
        if self.current_site == "Eminia" and select_id in SITES["Eminia"]["default_values"]:
            self.test_states[select_id] = SITES["Eminia"]["default_values"][select_id]
        else:
            # For other sites or non-default values, expect initial state
            self.test_states[select_id] = initial_value

        return new_value

    def verify_element_state(self, element_id: str, is_checkbox: bool = False) -> bool:
        """Verify element state in verification tab with improved reliability"""
        expected_state = self.test_states.get(element_id)
        if expected_state is None:
            logging.error(f"No stored state found for element {element_id}")
            return False

        try:
            logging.info(f"Starting verification for {element_id}")
            verify_script = f"""
            try {{
                const element = document.getElementById('{element_id}');
                if (!element) return {{ exists: false }};

                const style = window.getComputedStyle(element);
                return {{
                    exists: true,
                    visible: style.display !== 'none' && style.visibility !== 'hidden',
                    enabled: !element.disabled,
                    value: {'element.checked' if is_checkbox else 'element.value'}
                }};
            }} catch (error) {{
                return {{ error: error.message }};
            }}
            """

            # Try verification multiple times
            max_retries = 3
            for attempt in range(max_retries):
                element_state = self.driver.execute_script(verify_script)
                logging.info(f"Verification attempt {attempt + 1} for {element_id}: {element_state}")

                if element_state.get('error'):
                    logging.warning(f"Verification error on attempt {attempt + 1}: {element_state['error']}")
                    if attempt == max_retries - 1:
                        raise Exception(element_state['error'])
                    time.sleep(1)
                    continue

                if not element_state.get('exists'):
                    if attempt == max_retries - 1:
                        raise Exception(f"Element {element_id} not found")
                    time.sleep(1)
                    continue

                actual_state = element_state.get('value')
                logging.info(f"Verifying {element_id}: actual={actual_state}, expected={expected_state}")
                return str(actual_state) == str(expected_state)

            return False

        except Exception as e:
            logging.error(f"Error verifying element {element_id}: {str(e)}", exc_info=True)
            return False

    def login(self, username: str, password: str, url: str) -> bool:
        """Handle login for specific site"""
        logging.info(f"Attempting to login as {username} at {url}")
        try:
            self.driver.get(url)
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "login_name"))
            )
            password_input = self.driver.find_element(By.ID, "password")

            username_input.clear()
            username_input.send_keys(username)
            password_input.clear()
            password_input.send_keys(password)

            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            time.sleep(3)
            logging.info("Login successful")
            return True
        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            return False

    def test_site_features(self, site_name: str, site_config: dict):
        """Test all features for a site"""
        try:
            self.main_window = self.driver.current_window_handle
            self.test_states = {}
            self.initial_states = {}
            self.current_site = site_name

            logging.info("Modifying values in main tab...")

            # Test 1: Not shipped sales orders (checkbox)
            new_state = self.toggle_checkbox_js('not_shipped', 'showAllSurplusSales')
            logging.info(f"Modified 'not_shipped' checkbox to: {new_state}")

            # Test 2: Surplus sales statistics (dropdown)
            new_value = self.toggle_select_js('sales_date_diff', 'showAllSurplusSales')
            logging.info(f"Modified 'sales_date_diff' select to: {new_value}")

            # Test 3: Lead history statistics (dropdown)
            new_value = self.toggle_select_js('lead_date_diff', 'PriorlLeadHistory')
            logging.info(f"Modified 'lead_date_diff' select to: {new_value}")

            # Test 4: Surplus sales statistics section
            new_state = self.toggle_checkbox_js('not_shipped_statistics', 'showAllSurplusSalesStatistics')

            # Test 5: Only for Eminia - Pre-sale Statistics
            if site_name == "Eminia":
                new_value = self.toggle_select_js('presale_statistics_date_diff', 'showPresaleStatisticsHistory')
            else:
                # For other sites, use the regular date_diff
                new_value = self.toggle_select_js('date_diff', 'showAllSurplusSalesStatistics')

            # Open verification tab and verify values
            logging.info("Opening verification tab...")
            self.open_verification_tab(site_config['url'])

            # Base results that apply to all sites
            results = {
                'not_shipped': self.verify_element_state('not_shipped', is_checkbox=True),
                'sales_date_diff': self.verify_element_state('sales_date_diff'),
                'lead_date_diff': self.verify_element_state('lead_date_diff'),
                'not_shipped_statistics': self.verify_element_state('not_shipped_statistics', is_checkbox=True),
            }

            # Add specific tests based on site
            if site_name == "Eminia":
                results['presale_statistics_date_diff'] = self.verify_element_state('presale_statistics_date_diff')
            else:
                results['date_diff'] = self.verify_element_state('date_diff')

            return results

        except Exception as e:
            logging.error(f"Error during site testing: {str(e)}")
            # Return appropriate error results based on site
            if site_name == "Eminia":
                return {
                    'not_shipped': False,
                    'sales_date_diff': False,
                    'lead_date_diff': False,
                    'not_shipped_statistics': False,
                    'presale_statistics_date_diff': False
                }
            else:
                return {
                    'not_shipped': False,
                    'sales_date_diff': False,
                    'lead_date_diff': False,
                    'not_shipped_statistics': False,
                    'date_diff': False
                }

class MultiSiteTester:
    def __init__(self):
        self.results = {}
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )

    def test_site(self, site_name: str, site_config: dict):
        """Test a single site"""
        logging.info(f"\n{'='*50}")
        logging.info(f"Testing {site_name}")
        logging.info(f"URL: {site_config['url']}")
        logging.info(f"{'='*50}\n")

        try:
            tester = SPMPageTester()

            if not tester.login(site_config['username'], site_config['password'], site_config['url']):
                raise Exception("Login failed")

            site_results = tester.test_site_features(site_name, site_config)
            self.results[site_name] = site_results

            logging.info(f"\nResults for {site_name}:")
            for test_name, result in site_results.items():
                logging.info(f"{test_name}: {'PASS' if result else 'FAIL'}")
            logging.info("\n")

        except Exception as e:
            logging.error(f"Error testing {site_name}: {str(e)}")
            self.results[site_name] = {
                'not_shipped': False,
                'sales_date_diff': False,
                'lead_date_diff': False,
                'not_shipped_statistics': False,
                'presale_statistics_date_diff': False  # Updated to match new key
            }
        finally:
            try:
                tester.driver.quit()
            except:
                pass

    def run_all_sites(self):
        """Test all sites sequentially"""
        for site_name, config in SITES.items():
            self.test_site(site_name, config)
        self.print_summary()

    def print_summary(self):
        """Print final summary of all test results"""
        logging.info("\n\n" + "="*50)
        logging.info("FINAL TEST SUMMARY")
        logging.info("="*50)

        total_passed = 0
        total_tests = 0

        for site_name, results in self.results.items():
            logging.info(f"\n{site_name}:")
            site_passed = sum(1 for result in results.values() if result)
            site_total = len(results)
            total_passed += site_passed
            total_tests += site_total

            logging.info(f"Passed: {site_passed}/{site_total} tests")
            for test_name, result in results.items():
                logging.info(f"  {test_name}: {'PASS' if result else 'FAIL'}")

        logging.info("\n" + "="*50)
        logging.info(f"OVERALL: {total_passed}/{total_tests} tests passed")
        logging.info(f"Success rate: {(total_passed/total_tests)*100:.2f}%")
        logging.info("="*50 + "\n")


if __name__ == "__main__":
    multi_tester = MultiSiteTester()
    multi_tester.run_all_sites()
