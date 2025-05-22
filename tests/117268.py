from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import sys
from login_utils import login
from typing import Dict
from config import PROJECTS

# Маппинг специфических URL-параметров для каждого проекта
PROJECT_URLS = {
    "sm_usa": "index.cfm?page_id=714&proxy_set_id=&item_id=19303",
    "ra_trading": "index.cfm?page_id=714&item_id=5143",
    "agava_trading": "index.cfm?page_id=714&item_id=93420",
    "sm_eu": "index.cfm?page_id=714&item_id=37489",
    "eminia": "index.cfm?page_id=714&item_id=21194583&dummy=",
    "atlas_trading": "index.cfm?page_id=714&item_id=46479",
    "horus": "index.cfm?page_id=714&item_id=74851",
    "db_reactor": "index.cfm?page_id=714&item_id=619",
    "lanius": "index.cfm?page_id=714&item_id=199981"
}

class ProjectChecker:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.all_results = {}
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def check_surplus_sales_element(self, project_name: str) -> bool:
        """
        Проверяет наличие заголовка Surplus Sales и связанных элементов
        """
        try:
            element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//h4[contains(., 'Surplus Sales')]//span[@class='glyphicon glyphicon-chevron-up pull-right open']"
                ))
            )
            self.all_results[project_name]["access_rights"]["surplus_sales"] = "Full Access"
            self.all_results[project_name]["sections"]["surplus_sales"]["table_present"] = True
            return True
        except (TimeoutException, NoSuchElementException):
            self.all_results[project_name]["access_rights"]["surplus_sales"] = "No Access"
            self.all_results[project_name]["sections"]["surplus_sales"]["table_present"] = False
            logging.error(f"{project_name}: Surplus Sales element not found")
            return False

    def select_all_time(self, project_name: str) -> bool:
        """
        Выбирает опцию "All Time" в селекте
        """
        try:
            time_selector = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "sales_date_diff"))
            )
            select = Select(time_selector)
            select.select_by_value("0")
            self.all_results[project_name]["sections"]["surplus_sales"]["features"]["time_selector_present"] = True
            logging.info(f"{project_name}: Successfully selected 'All Time' option")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logging.error(f"{project_name}: Failed to select 'All Time': {str(e)}")
            return False

    def check_status_column(self, project_name: str) -> bool:
        """
        Проверяет наличие колонки Status в таблице
        """
        try:
            status_header = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[@class='tablesorter-header-inner'][contains(text(), 'Status')]"
                ))
            )
            self.all_results[project_name]["sections"]["surplus_sales"]["features"]["status_column_present"] = True
            logging.info(f"{project_name}: Status column found in the table")
            return True
        except (TimeoutException, NoSuchElementException):
            logging.error(f"{project_name}: Status column not found in the table")
            return False

    def initialize_project_results(self, project_name: str):
        """
        Инициализирует структуру результатов для проекта
        """
        self.all_results[project_name] = {
            "access_rights": {},
            "sections": {
                "surplus_sales": {
                    "table_present": False,
                    "columns_data": {},
                    "features": {
                        "status_column_present": False,
                        "time_selector_present": False
                    }
                }
            }
        }

    def check_project(self, project_name: str) -> bool:
        """
        Проверяет конкретный проект
        """
        self.initialize_project_results(project_name)
        logging.info(f"\nChecking project: {project_name}")

        try:
            # Логинимся в проект
            if not login(self.driver, project_name, "ml"):
                logging.error(f"{project_name}: Failed to login")
                return False

            # Получаем URL для проекта
            base_url = PROJECTS[project_name]["login_url"]
            specific_url = PROJECT_URLS[project_name]
            target_url = f"{base_url}{specific_url}"

            self.driver.get(target_url)

            # Проверяем элементы
            if not self.check_surplus_sales_element(project_name):
                return False

            if not self.select_all_time(project_name):
                return False

            # Ждем обновления таблицы
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "surplus_sales_table"))
            )

            if not self.check_status_column(project_name):
                return False

            return True

        except Exception as e:
            logging.error(f"{project_name}: An error occurred: {str(e)}")
            return False

    def run_all_checks(self):
        """
        Выполняет проверку всех проектов из PROJECT_URLS
        """
        has_failures = False

        try:
            for project_name in PROJECT_URLS.keys():
                project_status = self.check_project(project_name)
                if not project_status:
                    has_failures = True

            # Генерируем общий summary
            summary = self.generate_full_summary()
            print(summary)

            if has_failures:
                sys.exit(1)

        except Exception as e:
            logging.error(f"Critical error occurred: {str(e)}")
            sys.exit(1)
        finally:
            self.driver.quit()

    def generate_full_summary(self) -> str:
        """
        Генерирует полный отчет по всем проектам
        """
        summary = "\n=== PROJECTS TEST SUMMARY ===\n"

        for project_name, results in self.all_results.items():
            summary += f"\n{project_name.upper()}:\n"
            summary += "------------------------\n"

            # Access Rights Summary
            summary += "Access Status:\n"
            for section, status in results["access_rights"].items():
                icon = "[+]" if status == "Full Access" else "[-]"
                summary += f"{icon} {section.upper()}: {status}\n"

            # Features Summary
            summary += "\nFeatures Status:\n"
            features = results["sections"]["surplus_sales"]["features"]

            if results["sections"]["surplus_sales"]["table_present"]:
                summary += "[+] Surplus Sales heading: PRESENT\n"
            else:
                summary += "[-] Surplus Sales heading: NOT FOUND\n"

            if features.get("status_column_present"):
                summary += "[+] Status column: PRESENT\n"
            else:
                summary += "[-] Status column: NOT FOUND\n"

            if features.get("time_selector_present"):
                summary += "[+] Time selector: PRESENT\n"
            else:
                summary += "[-] Time selector: NOT FOUND\n"

            summary += "\n"

        return summary

if __name__ == "__main__":
    checker = ProjectChecker()
    checker.run_all_checks()
