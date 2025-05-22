from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
def log_example_function(data: List[str]) -> Dict[str, int]:
    """
    Пример функции с логированием, которая считает длины строк.

    Args:
        data (List[str]): Список строк для обработки.

    Returns:
        Dict[str, int]: Словарь с длинами строк.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Начало выполнения функции log_example_function")

    results = {}
    try:
        for item in data:
            logging.debug(f"Обработка элемента: {item}")
            results[item] = len(item)
        logging.info("Функция успешно завершена")
    except Exception as e:
        logging.error(f"Ошибка при выполнении функции: {str(e)}")
        raise

    return results
# Настройка логирования

def setup_chrome_driver(headless=True, download_dir=None):
    """Unified Chrome driver setup with configurable options"""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    if download_dir:
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False
        }
        options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=options)

def wait_for_element(driver, selector, by=By.CSS_SELECTOR, timeout=10):
    """Universal element wait function"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )
def verify_table_content(driver, table_selector: str) -> dict:
    """
    Проверяет содержимое таблицы и возвращает результаты проверки

    Args:
        driver: WebDriver instance
        table_selector: CSS selector таблицы

    Returns:
        dict: Результаты проверки с ключами:
            - is_present: bool
            - headers: list
            - rows: list
            - error: str или None
    """
    try:
        results = {
            "is_present": False,
            "headers": [],
            "rows": [],
            "error": None
        }

        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, table_selector))
        )
        results["is_present"] = True

        # Получаем заголовки
        headers = table.find_elements(By.TAG_NAME, "th")
        results["headers"] = [h.text.strip() for h in headers]

        # Получаем строки
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            results["rows"].append([cell.text.strip() for cell in cells])

        return results

    except Exception as e:
        results["error"] = str(e)
        return results

def fill_form(driver, form_data: dict) -> dict:
    """
    Заполняет форму данными

    Args:
        driver: WebDriver instance
        form_data: dict с парами id_элемента:значение

    Returns:
        dict: Результаты заполнения с ключами:
            - success: bool
            - filled_fields: list
            - failed_fields: list
            - error: str или None
    """
    results = {
        "success": True,
        "filled_fields": [],
        "failed_fields": [],
        "error": None
    }

    try:
        for element_id, value in form_data.items():
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, element_id))
                )
                element.clear()
                element.send_keys(value)
                results["filled_fields"].append(element_id)
            except Exception:
                results["failed_fields"].append(element_id)
                results["success"] = False

        return results

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        return results

def navigate_through_tabs(driver, tab_selectors: list) -> dict:
    """
    Проверяет навигацию по вкладкам

    Args:
        driver: WebDriver instance
        tab_selectors: list CSS селекторов вкладок

    Returns:
        dict: Результаты навигации с ключами:
            - success: bool
            - accessed_tabs: list
            - failed_tabs: list
            - error: str или None
    """
    results = {
        "success": True,
        "accessed_tabs": [],
        "failed_tabs": [],
        "error": None
    }

    try:
        for selector in tab_selectors:
            try:
                tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                tab.click()
                time.sleep(1)  # Ждем загрузку содержимого
                results["accessed_tabs"].append(selector)
            except Exception:
                results["failed_tabs"].append(selector)
                results["success"] = False

        return results

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        return results

def verify_element_states(driver, elements_config: dict) -> dict:
    """
    Проверяет состояния элементов (видимость, активность, значения)

    Args:
        driver: WebDriver instance
        elements_config: dict с конфигурацией элементов вида:
            {
                "element_id": {
                    "type": "visible|clickable|present",
                    "expected_value": value  # опционально
                }
            }

    Returns:
        dict: Результаты проверки с ключами:
            - success: bool
            - verified_elements: list
            - failed_elements: list
            - error: str или None
    """
    results = {
        "success": True,
        "verified_elements": [],
        "failed_elements": [],
        "error": None
    }

    try:
        for element_id, config in elements_config.items():
            try:
                if config["type"] == "visible":
                    element = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.ID, element_id))
                    )
                elif config["type"] == "clickable":
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, element_id))
                    )
                else:
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, element_id))
                    )

                if "expected_value" in config:
                    if element.get_attribute("value") == config["expected_value"]:
                        results["verified_elements"].append(element_id)
                    else:
                        results["failed_elements"].append(element_id)
                        results["success"] = False
                else:
                    results["verified_elements"].append(element_id)

            except Exception:
                results["failed_elements"].append(element_id)
                results["success"] = False

        return results

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        return results

def handle_modal_dialog(driver, action: str, form_data: dict = None) -> dict:
    """
    Обрабатывает модальные окна

    Args:
        driver: WebDriver instance
        action: str - действие (accept|dismiss|fill)
        form_data: dict - данные для заполнения формы в модальном окне

    Returns:
        dict: Результаты обработки с ключами:
            - success: bool
            - action_performed: str
            - error: str или None
    """
    results = {
        "success": True,
        "action_performed": None,
        "error": None
    }

    try:
        dialog = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-dialog"))
        )

        if action == "accept":
            accept_button = dialog.find_element(By.CSS_SELECTOR, ".btn-primary")
            accept_button.click()
            results["action_performed"] = "accept"
        elif action == "dismiss":
            dismiss_button = dialog.find_element(By.CSS_SELECTOR, ".btn-secondary")
            dismiss_button.click()
            results["action_performed"] = "dismiss"
        elif action == "fill" and form_data:
            for element_id, value in form_data.items():
                element = dialog.find_element(By.ID, element_id)
                element.clear()
                element.send_keys(value)
            results["action_performed"] = "fill"

        return results

    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
        return results
