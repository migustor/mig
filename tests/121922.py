from typing import List, Dict
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from login_utils import login

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def setup_driver():
    """Настройка драйвера Chrome"""
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome(options=options)

def wait_for_element(driver, selector, by=By.CSS_SELECTOR, timeout=10):
    """Ожидание элемента на странице"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )

def check_multiselect(driver):
    """Проверка мультиселекта на странице по аналогии с JavaScript версией"""
    results = {
        "present": False,
        "options_total": 0,
        "working_options": 0,
        "non_working_options": 0,
        "options_details": [],
        "error": None
    }

    try:
        # Поиск select элемента по имени
        select_element = wait_for_element(
            driver,
            'select[name="assigned_to"]',
            By.CSS_SELECTOR,
            timeout=15
        )
        results["present"] = True

        # Получение всех опций
        options = select_element.find_elements(By.TAG_NAME, "option")
        results["options_total"] = len(options)

        if results["options_total"] == 0:
            results["error"] = "No options found in multiselect!"
            return results

        # Проверка каждой опции
        for index, option in enumerate(options):
            option_details = {
                "index": index + 1,
                "text": option.text,
                "working": False
            }

            # Получаем начальное состояние
            initial_state = option.is_selected()

            # Пытаемся изменить состояние
            driver.execute_script("arguments[0].selected = !arguments[0].selected", option)
            time.sleep(0.1)  # Небольшая пауза для стабильности

            # Проверяем, изменилось ли состояние
            final_state = option.is_selected()

            if initial_state != final_state:
                results["working_options"] += 1
                option_details["working"] = True
                logging.info(f"Option #{index + 1} ({option.text}) successfully toggled")
            else:
                results["non_working_options"] += 1
                logging.warning(f"Option #{index + 1} ({option.text}) failed to toggle")

            # Возвращаем в исходное состояние
            driver.execute_script("arguments[0].selected = arguments[1]", option, initial_state)

            results["options_details"].append(option_details)

        logging.info(f"Total options: {results['options_total']}")
        logging.info(f"Working options: {results['working_options']}")
        logging.info(f"Non-working options: {results['non_working_options']}")

    except Exception as e:
        results["error"] = str(e)
        logging.error(f"Error checking multiselect: {str(e)}")

    return results

def generate_summary(test_results):
    """Генерация подробного отчета о тестировании"""
    summary = "=== Test Summary ===\n\n"

    for result in test_results:
        summary += f"Test: {result['name']}\n"
        summary += "-" * 50 + "\n"

        # Логин
        summary += f"Login: {'[PASSED]' if result['login']['success'] else '[FAILED]'}\n"
        if result['login'].get('error'):
            summary += f"  Error: {result['login']['error']}\n"

        # Мультиселект
        multiselect = result.get('multiselect', {})
        summary += f"\nMultiselect Testing Results:\n"
        summary += f"Present: {'[YES]' if multiselect.get('present') else '[NO]'}\n"

        if multiselect.get('present'):
            summary += f"Total options: {multiselect['options_total']}\n"
            summary += f"Working options: {multiselect['working_options']}\n"
            summary += f"Non-working options: {multiselect['non_working_options']}\n"

            if multiselect.get('options_details'):
                summary += "\nDetailed Options Report:\n"
                for option in multiselect['options_details']:
                    summary += f"  Option #{option['index']}: {option['text']} - "
                    summary += f"{'[WORKING]' if option['working'] else '[NOT WORKING]'}\n"

        if multiselect.get('error'):
            summary += f"\nError: {multiselect['error']}\n"

        summary += "\n" + "=" * 50 + "\n\n"

    return summary

def main():
    driver = None
    test_results = []

    try:
        # Инициализация драйвера
        driver = setup_driver()

        # Логин в систему используя login_utils
        login_result = login(driver, "grafit", "ml")

        if login_result:
            # Переход на страницу с мультиселектом
            driver.get("https://stage15.office.grafit.md/sage/index.cfm?page_id=926")

            # Проверка мультиселекта
            multiselect_result = check_multiselect(driver)

            # Формирование результатов
            test_results.append({
                "name": "Grafit Multiselect Test",
                "login": {
                    "success": login_result,
                    "error": None
                },
                "multiselect": multiselect_result
            })

            # Генерация и вывод отчета
            summary = generate_summary(test_results)
            print(summary)

        else:
            logging.error("Login failed")

    except Exception as e:
        logging.error(f"Test execution failed: {str(e)}")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()