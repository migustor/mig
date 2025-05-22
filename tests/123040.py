import logging
import random
import string
import time
import os
import uuid  
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# Импортируем функции управления драйвером из driver_setup.py
from common.utils.driver_setup import setup_chrome_driver, release_driver
import sys
from typing import Dict

# Создаем уникальный ID для этого теста
TEST_ID = f"123040_test_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Создаем директорию для скриншотов
screenshot_dir = r"J:\PUB5\E2E_Testing"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Простые таймауты для разных операций
TIMEOUTS = {
    "login": 25,
    "document": 25,
    "part": 25, 
    "barcode": 35,
    "checkbox": 20,
    "page_load": 35
}

# Configuration constants
LOGIN_URL = "https://stage15.office.agavasystem.com/"
TARGET_URL = "https://stage15.office.agavasystem.com/euwhse/receive/enter_po_number.cfm"
USERNAME = "maxim.lupan@mteam.md"
PASSWORD = "12"
DOCUMENT_NUMBER = "4471"

def take_screenshot(driver, name, part_number=None):
    """Делает скриншот страницы с указанным именем"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if part_number:
        filename = os.path.join(SCREENSHOT_DIR, f"{part_number}_{name}_{timestamp}.png")
    else:
        filename = os.path.join(SCREENSHOT_DIR, f"{name}_{timestamp}.png")
        
    try:
        driver.save_screenshot(filename)
        logging.info(f"Screenshot saved to {filename}")
        return filename
    except Exception as e:
        logging.error(f"Failed to take screenshot: {str(e)}")
        return None

def login(driver, username, password, url):
    """Вход в систему с добавлением скриншота при ошибке"""
    logging.info(f"Logging in as {username}")
    driver.get(url)
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
        
        # Проверяем успешность входа
        WebDriverWait(driver, TIMEOUTS["login"]).until(
            EC.invisibility_of_element_located((By.ID, "login_name"))
        )
        
        logging.info("Login successful.")
        return True
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")
        take_screenshot(driver, "login_failed")
        return False

def enter_data(driver, document_number):
    """Ввод номера документа с добавлением скриншота при ошибке"""
    try:
        logging.info(f"Entering document number: {document_number}")
        document_input = WebDriverWait(driver, TIMEOUTS["document"]).until(
            EC.presence_of_element_located((By.ID, "document_number"))
        )
        document_input.send_keys(document_number)
        submit_button = driver.find_element(By.ID, "start_receiving")
        submit_button.click()
        
        # Ждем загрузки страницы
        WebDriverWait(driver, TIMEOUTS["page_load"]).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        logging.info("Data entered successfully.")
        return True
    except Exception as e:
        logging.error(f"Error entering data: {str(e)}")
        take_screenshot(driver, "document_input_failed")
        return False

def enter_part_number(driver, part_number):
    """Ввод номера детали с добавлением скриншота при ошибке"""
    try:
        logging.info(f"Entering part number: {part_number}")
        part_input = WebDriverWait(driver, TIMEOUTS["part"]).until(
            EC.presence_of_element_located((By.ID, "part_number"))
        )
        part_input.send_keys(part_number)
        submit_button = driver.find_element(By.ID, "register_product")
        submit_button.click()
        
        # Ждем загрузки страницы
        WebDriverWait(driver, TIMEOUTS["page_load"]).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        logging.info("Part number entered successfully.")
        return True
    except Exception as e:
        logging.error(f"Error entering part number: {str(e)}")
        take_screenshot(driver, "part_input_failed", part_number)
        return False

def generate_barcode():
    """Генерирует случайный штрих-код"""
    first_digit = str(random.randint(0, 9))
    random_letter = random.choice(string.ascii_uppercase)
    random_number = random.randint(0, 9999)
    return f"{first_digit}{random_letter}{random_number:04d}"

def enter_barcodes(driver, part_number):
    """Ввод штрих-кода с добавлением скриншота при ошибке"""
    barcode_success = False
    final_barcode = None
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            barcode = generate_barcode()
            logging.info(f"Entering barcode: {barcode} (attempt {attempt+1}/{max_attempts})")
            
            barcode_input = WebDriverWait(driver, TIMEOUTS["barcode"]).until(
                EC.presence_of_element_located((By.ID, "barcodes"))
            )
            barcode_input.clear()
            barcode_input.send_keys(barcode)
            
            submit_button = driver.find_element(By.ID, "submit_btn")
            submit_button.click()
            time.sleep(2)
            
            # Проверяем ошибки
            error_elements = driver.find_elements(By.CLASS_NAME, "scan_barcode_error")
            if error_elements:
                error_message = error_elements[0].text
                if "already exists in the system" in error_message:
                    logging.warning(f"Barcode exists, trying new one: {error_message}")
                    if attempt == max_attempts - 1:
                        take_screenshot(driver, "barcode_duplicate", part_number)
                    continue
                else:
                    logging.error(f"Barcode error: {error_message}")
                    take_screenshot(driver, "barcode_error", part_number)
                    return False, None
            
            # Успешный ввод
            logging.info(f"Barcode {barcode} entered successfully.")
            return True, barcode
            
        except Exception as e:
            logging.error(f"Error entering barcode: {str(e)}")
            take_screenshot(driver, "barcode_input_failed", part_number)
            return False, None
            
    # Если не смогли ввести за max_attempts попыток
    logging.error("Failed to enter valid barcode after multiple attempts")
    take_screenshot(driver, "barcode_max_attempts", part_number)
    return False, None

def check_checkbox_state(driver, part_number):
    """Проверка состояния чекбокса с добавлением скриншота"""
    try:
        logging.info("Checking state of 'Not for E-commerce' checkbox")
        
        # Делаем скриншот страницы с чекбоксом
        take_screenshot(driver, "checkbox_state", part_number)
        
        checkboxes = driver.find_elements(By.ID, "no_ecommerce_item")
        if not checkboxes:
            logging.info("Checkbox not found on page")
            return {
                'exists': False,
                'is_checked': None,
                'label_text': None
            }
            
        checkbox = checkboxes[0]
        is_checked = checkbox.is_selected()
        
        try:
            label_text = driver.find_element(
                By.XPATH,
                "//label[.//input[@id='no_ecommerce_item']]/strong"
            ).text
        except:
            label_text = "Not for E-commerce"
            
        logging.info(f"Checkbox '{label_text}' is {'checked' if is_checked else 'unchecked'} by default")
        
        return {
            'exists': True,
            'is_checked': is_checked,
            'label_text': label_text
        }
    except Exception as e:
        logging.error(f"Error checking checkbox state: {str(e)}")
        take_screenshot(driver, "checkbox_error", part_number)
        return None

def test_part_number(driver, part_number: str) -> Dict:
    """Тестирует конкретный part number и возвращает результаты"""
    results = {
        "test_executed": False,
        "checkbox_info": None,
        "error": None,
        "screenshots": []
    }
    
    try:
        logging.info(f"Navigating to target page for part number: {part_number}")
        driver.get(TARGET_URL)
        
        # Ввод номера документа
        if not enter_data(driver, DOCUMENT_NUMBER):
            results["error"] = "Failed to enter document number"
            return results
        
        # Ввод номера детали
        if not enter_part_number(driver, part_number):
            results["error"] = "Failed to enter part number"
            return results
        
        # Ввод штрих-кода
        barcode_success, final_barcode = enter_barcodes(driver, part_number)
        if not barcode_success:
            results["error"] = "Failed to enter barcode"
            return results
        
        # Проверка состояния чекбокса
        checkbox_info = check_checkbox_state(driver, part_number)
        if checkbox_info is None:
            results["error"] = "Failed to check checkbox state"
            return results
            
        results["checkbox_info"] = checkbox_info
        results["test_executed"] = True
        results["final_barcode"] = final_barcode
        
    except Exception as e:
        logging.error(f"Error testing part number {part_number}: {str(e)}")
        take_screenshot(driver, "test_error", part_number)
        results["error"] = str(e)
        
    return results

def generate_test_summary(test_results: Dict) -> str:
    """Генерирует сводный отчёт по результатам тестирования"""
    brand_info = {
        "IFD5700LL": "Shimano",
        "AG95054": "Other Brand"
    }
    summary = "\n=== TEST SUMMARY ===\n"
    
    for part_number, results in test_results.items():
        brand = brand_info.get(part_number, "Other Brand")
        summary += f"\nPart Number: {part_number} (Brand: {brand})\n"
        summary += "-" * 40 + "\n"
        
        test_status = results.get("test_executed", False)
        icon = "[+]" if test_status else "[-]"
        summary += f"{icon} Test Execution: {'Successful' if test_status else 'Failed'}\n"
        
        if "final_barcode" in results and results["final_barcode"]:
            summary += f"    Barcode Used: {results['final_barcode']}\n"
        
        checkbox_info = results.get("checkbox_info", {})
        if checkbox_info:
            exists = checkbox_info.get("exists", False)
            is_checked = checkbox_info.get("is_checked")
            label_text = checkbox_info.get("label_text", "Not for E-commerce")
            
            if not exists:
                icon = "[!]"
                status = "FAIL - Checkbox should be present"
            else:
                if brand == "Shimano":
                    if is_checked:
                        icon = "[+]"
                        status = "PASS - Checkbox is present and checked"
                    else:
                        icon = "[!]"
                        status = "FAIL - Checkbox is present but should be checked"
                else:
                    if not is_checked:
                        icon = "[+]"
                        status = "PASS - Checkbox is present and unchecked"
                    else:
                        icon = "[!]"
                        status = "FAIL - Checkbox is present but should be unchecked"
                        
            summary += f"{icon} Checkbox '{label_text}': {status}\n"
        
        if "error" in results and results["error"]:
            summary += f"[!] Error: {results['error']}\n"
    
    summary += "\n=================\n"
    return summary

def main():
    part_numbers = ["IFD5700LL", "AG95054"]
    test_results = {}

    # Изменено: Добавлен test_id для отслеживания
    driver = setup_chrome_driver(headless=True, test_id=TEST_ID)
    
    try:
        # Первоначальный логин
        if not login(driver, USERNAME, PASSWORD, LOGIN_URL):
            raise Exception("Login failed")
        
        # Тестируем каждый part number
        for part_number in part_numbers:
            logging.info(f"\nTesting part number: {part_number}")
            test_results[part_number] = test_part_number(driver, part_number)
        
        # Генерация и вывод сводного отчёта
        summary = generate_test_summary(test_results)
        print(summary)
        
        # Проверяем, есть ли ошибки в результатах тестов
        has_error = any(
            results.get("error") or not results.get("test_executed", False)
            for results in test_results.values()
        )
        
        if has_error:
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"Test failed: {str(e)}")
        # Делаем скриншот критической ошибки
        take_screenshot(driver, "critical_error")
        sys.exit(1)
    finally:
        # Изменено: Явно указываем quit=True для надежного завершения
        release_driver(driver, quit=True)
        # Добавлено: Логирование завершения теста
        logger.info(f"Test run {TEST_ID} completed")

if __name__ == "__main__":
    main()