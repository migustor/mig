import logging
import time
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # Добавляем импорт Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import sys

class LoginTestScript:
    def __init__(self, headless: bool = True):  # Добавляем параметр headless
        # Настройка ChromeOptions
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless=new')  # Включаем headless режим
            chrome_options.add_argument('--disable-gpu')  # Отключаем GPU (рекомендуется для headless)
            chrome_options.add_argument('--no-sandbox')  # Отключаем sandbox
            chrome_options.add_argument('--disable-dev-shm-usage')  # Используем /tmp вместо /dev/shm
            chrome_options.add_argument('--window-size=1920,1080')  # Устанавливаем размер окна

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

        # Конфигурация систем и их лидов
        self.systems_config = {
            'Eminia': {
                'base_url': 'stage15.office.eminiasystem.com',
                'leads': {57930: 57931, 57931: 57930},
                'credentials': {
                    'username': 'dmitri.dubkovetki@mteam.md',
                    'password': '12'
                }
            },
            'Lanius': {
                'base_url': 'stage15.office.laniustoys.com',
                'leads': {41997: 41998, 41998: 41997},
                'credentials': {
                    'username': 'dmitri.dubkovetki@mteam.md',
                    'password': '12'
                }
            },
            'Atlas': {
                'base_url': 'stage15.office.atlastradingworld.com',
                'leads': {4490: 4491, 4491: 4490},
                'credentials': {
                    'username': 'dmitri.dubkovetki@mteam.md',
                    'password': '12'
                }
            },
            'DB': {
                'base_url': 'stage15.office.dbreactor.com',
                'leads': {4195: 4196, 4196: 4195},
                'credentials': {
                    'username': 'dmitri.dubkovetki@mteam.md',
                    'password': '12'
                }
            },
            'Horus': {
                'base_url': 'stage15.office.horustrading.eu',
                'leads': {8702: 8703, 8703: 8702},
                'credentials': {
                    'username': 'dmitri.dubkovetki@mteam.md',
                    'password': '12'
                }
            },
            'AGAVA': {
                'base_url': 'stage15.office.agavasystem.com',
                'leads': {10657: 10660, 10660: 10657},
                'credentials': {
                    'username': 'dmitri.dubkovetki@mteam.md',
                    'password': '12'
                }
            },
            'RA': {
                'base_url': 'stage15.office.ratrading.eu',
                'leads': {121389: 121390, 121390: 121389},
                'credentials': {
                    'username': 'dmitri.dubkovetki@mteam.md',
                    'password': '12'
                }
            }
        }

        self.test_results = {}

        # Инициализация результатов для всех систем
        for system_name, system_config in self.systems_config.items():
            self.test_results[system_name] = {}
            for lead_id in system_config['leads'].keys():
                self.test_results[system_name][lead_id] = {
                    'login': {'success': False},
                    'page_load': {'success': False},
                    'button_click': {'success': False},
                    'move_to_lead_check': {'success': False},
                    'lead_input': {'success': False},
                    'autocomplete_select': {'success': False},
                    'save_click': {'success': False}
                }

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def wait_for_element(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> bool:
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            return element
        except Exception as e:
            logging.error(f"Element not found or not clickable: {selector}")
            raise e

    def login(self, system_name: str):
        try:
            logging.info(f"Attempting login for {system_name}")
            system_config = self.systems_config[system_name]
            first_lead = list(system_config['leads'].keys())[0]

            url = f"https://{system_config['base_url']}/sage/index.cfm?page_id=621&lead_id={first_lead}&phase=edit"
            self.driver.get(url)

            username_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "login_name"))
            )
            password_input = self.driver.find_element(By.ID, "password")

            username_input.send_keys(system_config['credentials']['username'])
            password_input.send_keys(system_config['credentials']['password'])

            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            time.sleep(3)
            # Set login success for all leads in this system
            for lead_id in system_config['leads'].keys():
                self.test_results[system_name][lead_id]['login']['success'] = True
            logging.info(f"Login successful for {system_name}")
            return True

        except Exception as e:
            logging.error(f"Login failed for {system_name}: {str(e)}")
            return False

    def process_lead(self, system_name: str, lead_id: int):
        try:
            system_config = self.systems_config[system_name]
            target_lead_id = system_config['leads'][lead_id]

            lead_url = f"https://{system_config['base_url']}/sage/index.cfm?page_id=621&lead_id={lead_id}&phase=edit"
            logging.info(f"Processing lead {lead_id} with target transfer to {target_lead_id} in {system_name}")
            self.driver.get(lead_url)

            logging.info("Waiting 10 seconds for page load...")
            time.sleep(10)
            self.test_results[system_name][lead_id]['page_load']['success'] = True

            # Click initial moveItems button
            logging.info("Finding and clicking moveItems button...")
            move_items_btn = self.wait_for_element('button.btn.btn-primary.btn-block[onclick="moveItems()"]')
            self.driver.execute_script("arguments[0].scrollIntoView(true);", move_items_btn)
            time.sleep(1)
            move_items_btn.click()
            self.test_results[system_name][lead_id]['button_click']['success'] = True

            # Wait for modal to appear and click first radio button label
            logging.info("Waiting for first radio button (Move only items not in PO)...")
            time.sleep(2)
            first_radio_label = self.wait_for_element('label[for="move_item_option_4"]')
            self.driver.execute_script("arguments[0].scrollIntoView(true);", first_radio_label)
            self.driver.execute_script("arguments[0].click();", first_radio_label)
            logging.info("Clicked first radio button")
            time.sleep(1)

            # Click second radio button label
            logging.info("Clicking second radio button (Move items to another lead)...")
            second_radio_label = self.wait_for_element('label[for="move_item_to_another_lead"]')
            self.driver.execute_script("arguments[0].scrollIntoView(true);", second_radio_label)
            self.driver.execute_script("arguments[0].click();", second_radio_label)
            self.test_results[system_name][lead_id]['move_to_lead_check']['success'] = True
            logging.info("Clicked second radio button")
            time.sleep(1)

            # Handle lead ID input
            logging.info(f"Preparing to input target_lead_id: {target_lead_id}")
            lead_input = self.wait_for_element('#move_to_lead_id')
            self.driver.execute_script("arguments[0].scrollIntoView(true);", lead_input)

            # Clear and focus the input
            self.driver.execute_script("arguments[0].value = '';", lead_input)
            self.driver.execute_script("arguments[0].focus();", lead_input)

            # Type the lead ID
            logging.info("Entering lead ID...")
            target_id_str = str(target_lead_id)
            for char in target_id_str:
                lead_input.send_keys(char)
                self.driver.execute_script("""
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                """, lead_input)
                time.sleep(0.1)

            self.test_results[system_name][lead_id]['lead_input']['success'] = True

            # Wait for autocomplete and select option
            logging.info("Waiting for autocomplete dropdown (2 seconds)...")
            time.sleep(2)

            autocomplete_option = self.wait_for_element(f'.typeahead li[data-value="{target_lead_id}"] a')
            self.driver.execute_script("arguments[0].click();", autocomplete_option)
            self.test_results[system_name][lead_id]['autocomplete_select']['success'] = True

            # Click save button
            logging.info("Clicking save button...")
            save_button = self.wait_for_element('button.btn.btn-primary.text-uppercase[onclick="$(\'#move_items_form\').submit();"]')
            self.driver.execute_script("arguments[0].click();", save_button)
            self.test_results[system_name][lead_id]['save_click']['success'] = True

            logging.info("Waiting 5 seconds after save...")
            time.sleep(5)

            logging.info(f"Process completed successfully for lead {lead_id} in {system_name}")
            return True

        except Exception as e:
            logging.error(f"Processing lead {lead_id} in {system_name} failed: {str(e)}")
            return False

    def generate_summary(self) -> str:
        summary = "\n=== TEST EXECUTION SUMMARY ===\n"

        for system_name, system_results in self.test_results.items():
            summary += f"\n{system_name} System Results"
            summary += "\n" + "=" * 50 + "\n"

            for lead_id, lead_results in system_results.items():
                target_lead_id = self.systems_config[system_name]['leads'][lead_id]
                summary += f"\nLead ID: {lead_id} (Transfer to: {target_lead_id})\n"
                summary += "-" * 40 + "\n"

                # Login Status
                icon = "[+]" if lead_results['login']['success'] else "[-]"
                summary += f"{icon} Login attempt: {'Successful' if lead_results['login']['success'] else 'Failed'}\n"

                # Page Load Status
                icon = "[+]" if lead_results['page_load']['success'] else "[-]"
                summary += f"{icon} Page load: {'Completed' if lead_results['page_load']['success'] else 'Failed'}\n"

                # Element Checks and Actions
                summary += "\nElement Checks and Actions:\n"
                for check in ['button_click', 'move_to_lead_check', 'lead_input', 'autocomplete_select', 'save_click']:
                    icon = "[+]" if lead_results[check]['success'] else "[-]"
                    status = 'Successful' if lead_results[check]['success'] else 'Failed'
                    summary += f"{icon} {check.replace('_', ' ').title()}: {status}\n"

            summary += "\n" + "=" * 50 + "\n"

        logging.info(summary)
        return summary

    def run_test(self):
        try:
            for system_name in self.systems_config.keys():
                logging.info(f"\nStarting tests for {system_name} system")

                if not self.login(system_name):
                    logging.error(f"Login failed for {system_name}, skipping this system")
                    continue

                for lead_id in self.systems_config[system_name]['leads'].keys():
                    if not self.process_lead(system_name, lead_id):
                        logging.error(f"Test failed for lead {lead_id} in {system_name}")
                        continue
                    logging.info(f"Completed processing lead {lead_id} in {system_name}")

                logging.info(f"Completed tests for {system_name} system")

            summary = self.generate_summary()
            self.driver.quit()
            return summary
        except Exception as e:
            logging.error(f"Test execution failed: {str(e)}")
            self.driver.quit()
            sys.exit(1)

if __name__ == "__main__":
    test = LoginTestScript(headless=True)
    test.run_test()
