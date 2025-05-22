from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import logging
from login_utils import login

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class RequestCreatorTest:
    def __init__(self):
        self.results = {}
        self.projects = {
            "ra_trading": "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=925&phase=edit&id=14279",
            "lanius": "https://stage15.office.laniustoys.com/sage/index.cfm?page_id=925&phase=edit&id=2512",
            "db_reactor": "https://stage15.office.dbreactor.com/sage/index.cfm?page_id=925&phase=edit&id=734",
            "argon": "https://stage15.office.argontrading.de/sage/index.cfm?page_id=925&phase=edit&id=1",
            "atlas_trading": "https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=925&phase=edit&id=629",
            "agava_trading": "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=925&phase=edit&id=2",
            "aro": "https://stage15.office.arotrading.eu/sage/index.cfm?page_id=925&phase=edit&id=1",
            "horus": "https://stage15.office.horustrading.eu/sage/index.cfm?page_id=925&phase=edit&id=1600",
            "roc": "https://stage15.office.roctrading.de/sage/index.cfm?page_id=925&phase=edit&id=1"
        }

    def generate_test_summary(self):
        """
        Генерирует общий отчет по всем проектам
        """
        summary = "\n=== TEST SUMMARY ===\n"

        for project, result in self.results.items():
            summary += f"\n{project.upper()}:\n"
            if result.get("error"):
                summary += f"[-] Error: {result['error']}\n"
            else:
                summary += f"[+] Creator in UI: {result.get('creator_ui', 'Not found')}\n"
                summary += f"[+] Creator in logs: {result.get('creator_log', 'Not found')}\n"
                if result.get('match'):
                    summary += "[+] Creator info matches\n"
                else:
                    summary += "[-] Creator info mismatch\n"

        successful = sum(1 for r in self.results.values() if not r.get("error") and r.get("match"))
        total = len(self.projects)

        summary += f"\n=== TOTAL RESULTS ===\n"
        summary += f"Success: {successful}/{total}\n"
        summary += "=================\n"
        return summary

    def check_project(self, project_name, driver):
        """Проверка отдельного проекта"""
        try:
            # Вход в систему
            assert login(driver, project_name, "ml"), f"Failed to login to {project_name}"
            logging.info(f"Successfully logged in to {project_name}")

            # Переход на целевую страницу
            driver.get(self.projects[project_name])
            logging.info(f"Navigating to {self.projects[project_name]}")

            # Проверяем информацию о создателе в UI
            creator_info = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[contains(text(), 'Created by:')]/../div/p[@class='form-control-static']"
                ))
            )
            creator_name_ui = creator_info.text.strip()
            logging.info(f"Found creator in UI: {creator_name_ui}")

            # Находим и кликаем на панель с логами
            log_panel = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "div[class*='panel-heading'][class*='click-me_']"
                ))
            )
            log_panel.click()
            logging.info("Clicked on logs panel")
            time.sleep(1)

            # Получаем ID таблицы логов
            panel_id = log_panel.get_attribute('id')
            table_id = panel_id.replace('log_spoiler_', 'activity_log_table_')

            # Проверяем логи
            log_entry = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    f"#{table_id} tbody tr:nth-child(2) td:nth-child(2)"
                ))
            )
            creator_name_log = log_entry.text.strip()
            logging.info(f"Found creator in logs: {creator_name_log}")

            # Сохраняем результаты
            self.results[project_name] = {
                "creator_ui": creator_name_ui,
                "creator_log": creator_name_log,
                "match": creator_name_ui == creator_name_log
            }

            # Чистим куки перед следующим проектом
            driver.delete_all_cookies()

        except Exception as e:
            logging.error(f"Error testing {project_name}: {str(e)}")
            self.results[project_name] = {"error": str(e)}

    def test_all_projects(self):
        """Тестирование всех проектов"""
        driver = webdriver.Chrome()
        try:
            for project_name in self.projects:
                logging.info(f"\n{'='*50}\nTesting {project_name.upper()}\n{'='*50}")
                self.check_project(project_name, driver)

            logging.info("\nAll projects tested")
            logging.info(self.generate_test_summary())

        except Exception as e:
            logging.error(f"Critical error during testing: {str(e)}")
        finally:
            driver.quit()

if __name__ == "__main__":
    test = RequestCreatorTest()
    test.test_all_projects()

