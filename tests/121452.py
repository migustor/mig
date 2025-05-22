import os
import random
import string
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv

print("Starting script...")
print(f"Python version: {sys.version}")
print("Loading environment variables...")

# Load .env file
load_dotenv()

# Constants
USERNAME = os.getenv('VAL-USERNAME')
PASSWORD = os.getenv('VAL-PASSWORD')

# Проверка переменных окружения
if not USERNAME or not PASSWORD:
    print("ERROR: Username or password not found in environment variables")
    sys.exit(1)
print("Environment variables loaded successfully")

PROJECTS = {
    "HORUS": "https://stage15.office.horustrading.eu/sage/index.cfm?page_id=864&phase=edit&id=251",
    "SM USA": "https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=864&phase=edit&id=3136",
    "SM EU": "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=864&phase=edit&id=56631",
    "AGAVA": "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=864&phase=edit&id=3264",
    "ATLAS": "https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=864&phase=edit&id=135",
    "ARGON": "https://stage15.office.argontrading.de/sage/index.cfm?page_id=864&phase=edit&id=1",
    "DB": "https://stage15.office.dbreactor.com/sage/index.cfm?page_id=864&phase=edit&id=250",
    "ARO": "https://stage15.office.arotrading.eu/sage/index.cfm?page_id=864&phase=edit&id=3",
    "LANIUS": "https://stage15.office.laniustoys.com/sage/index.cfm?page_id=864&phase=edit&id=5281",
    "EMINIA": "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=864&phase=edit&id=15079",
    "RA": "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=864&phase=edit&id=8053"
}

print(f"Projects to test: {list(PROJECTS.keys())}")

TEST_SUMMARY = []

def log_step(step_message):
    print(f"[INFO] {step_message}")

def generate_random_filename(extension, length=5):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return f"{random_string}.{extension}"

def check_restriction_element(driver, wait, project_name, stage):
    """Check for restriction element and its visibility"""
    RESTRICTION_TEXT = "A credit note document can be uploaded only if an active invoice is attached"
    try:
        time.sleep(2)

        # Находим элемент
        restriction_elements = driver.find_elements(
            By.XPATH,
            f"//div[contains(text(), '{RESTRICTION_TEXT}')]"
        )

        # Проверяем видимость элемента
        restriction_visible = False
        if restriction_elements:
            restriction_visible = any(
                element.is_displayed() and
                element.value_of_css_property('display') != 'none' and
                element.value_of_css_property('visibility') != 'hidden' and
                element.value_of_css_property('opacity') != '0'
                for element in restriction_elements
            )

        log_step(f"Checking restriction for stage {stage}")
        log_step(f"Restriction element {'visible' if restriction_visible else 'hidden or not present'}")

        if stage == 'Initial':
            # После загрузки страницы - должен быть видимым
            if not restriction_visible:
                log_step(f"ERROR: Restriction not visible at initial stage")
                return False
            log_step(f"SUCCESS: Initial restriction visible")
            return True

        elif stage == 'After Upload':
            # После загрузки документа - должен быть скрыт
            if restriction_visible:
                log_step(f"ERROR: Restriction still visible after document upload")
                return False
            log_step(f"SUCCESS: Restriction hidden after upload")
            return True

        elif stage == 'After Cancel':
            # После отмены документа - должен быть видимым
            if not restriction_visible:
                log_step(f"ERROR: Restriction not visible after cancel")
                return False
            log_step(f"SUCCESS: Restriction visible after cancel")
            return True

    except Exception as e:
        log_step(f"Error checking restriction element: {e}")
        log_step(str(e))
        return False


def wait_for_file_appearance(driver, wait):
    """Wait for file container to appear"""
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'c1-32')))
        log_step("File container appeared")
        return True
    except Exception as e:
        log_step(f"Error waiting for file container: {e}")
        return False

def wait_for_upload_success(driver, wait):
    """Wait for success message after upload"""
    try:
        # Сначала ждем появления сообщения
        success_message = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#result_inv'))
        )

        # Проверяем, что сообщение зеленое и содержит нужный текст
        if 'color_green' in success_message.get_attribute('class') and 'Invoice is uploaded!' in success_message.text:
            log_step("Upload success message appeared")
            time.sleep(2)  # Добавляем задержку после успешного сообщения
            return True
        else:
            log_step(f"Unexpected message state: {success_message.get_attribute('class')} - {success_message.text}")
            return False

    except Exception as e:
        log_step(f"Error waiting for upload success message: {e}")
        return False

def fill_invoice_details(driver, wait, project_name):
    """Fill invoice details"""
    try:
        # Select document type
        select_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="in_supplier_inv_prefix"]')))
        select = Select(select_element)
        select.select_by_value('Invoice')
        log_step(f"Selected document type for {project_name}")

        time.sleep(1)  # Небольшая пауза после выбора типа

        # Fill invoice number and amount
        random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        invoice_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#in_supplier_inv')))
        invoice_field.clear()  # Очищаем поле перед вводом
        invoice_field.send_keys(random_name)

        amount_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#in_amount_inv')))
        amount_field.clear()  # Очищаем поле перед вводом
        amount_field.send_keys("100")

        log_step(f"Filled document details for {project_name}")
        return True

    except Exception as e:
        log_step(f"Error filling invoice details: {e}")
        return False

def upload_and_save_document(driver, wait, project_name):
    pdf_filename = generate_random_filename('pdf')
    with open(pdf_filename, 'w') as file:
        file.write("")
    log_step(f"Temporary file {pdf_filename} created.")

    try:
        # Загрузка файла
        upload_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pickfiles_inv')))
        upload_button.send_keys(os.path.abspath(pdf_filename))
        log_step(f"File upload initiated for {project_name}")

        # Ждем появления файла
        if not wait_for_file_appearance(driver, wait):
            return False

        # Сохранение документа
        save_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#btn_upload_inv')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
        save_button.click()
        log_step(f"Save initiated for {project_name}")

        # Ждем сообщения об успешной загрузке
        if not wait_for_upload_success(driver, wait):
            return False

        log_step(f"Document saved successfully for {project_name}")
        return True

    except Exception as e:
        log_step(f"Error during document upload and save: {e}")
        return False
    finally:
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
            log_step(f"Temporary file {pdf_filename} removed.")

def cancel_document(driver, wait, project_name):
    """Cancel document with working implementation"""
    try:
        # Находим все контейнеры и проверяем наличие второго
        all_containers = driver.find_elements(By.CLASS_NAME, 'c1-32')
        if len(all_containers) < 2:
            log_step("Failed to find the second container.")
            return False

        # Берем второй контейнер
        second_container = all_containers[1]

        # Ждем появления кнопок инструментов
        btn_tools = WebDriverWait(second_container, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'btnToolsRight'))
        )

        # Наводим мышь на кнопки
        ActionChains(driver).move_to_element(btn_tools).perform()

        # Находим и кликаем кнопку отмены
        cancel_button = btn_tools.find_element(By.XPATH, './/a[contains(@title, "Cancel This Document")]')
        cancel_button.click()
        log_step(f"Cancel button clicked for project {project_name}")

        # Принимаем алерт
        alert = driver.switch_to.alert
        alert.accept()
        log_step("Alert accepted")

        time.sleep(2)  # Даем время на обработку отмены
        return True

    except Exception as e:
        log_step(f"Error during document cancellation: {e}")
        return False
def generate_test_summary(test_results):
    """
    Generates a formatted summary of the test results for each project
    """
    summary = "\n=== TEST SUMMARY ===\n"

    # Группируем результаты по проектам
    projects = {}
    for result in test_results:
        project_name = result.split(':')[0].strip()
        if project_name not in projects:
            projects[project_name] = []
        projects[project_name].append(result)

    # Для каждого проекта формируем отчет
    for project_name, project_results in projects.items():
        summary += f"\n{project_name} Status:\n"
        summary += "-" * 30 + "\n"

        # Restriction Checks
        summary += "Restriction Status:\n"

        # Initial Check
        initial_check = next((result for result in project_results if "Initial check" in result), "")
        icon_initial = "[+]" if "FAILED" not in initial_check else "[-]"
        summary += f"{icon_initial} INITIAL RESTRICTION: {'PRESENT' if 'FAILED' not in initial_check else 'MISSING'}\n"

        # After Upload Check
        upload_check = next((result for result in project_results if "After upload check" in result), "")
        icon_upload = "[+]" if "FAILED" not in upload_check else "[-]"
        summary += f"{icon_upload} AFTER UPLOAD RESTRICTION: {'HIDDEN' if 'FAILED' not in upload_check else 'STILL PRESENT'}\n"

        # After Cancel Check
        cancel_check = next((result for result in project_results if "After cancel check" in result), "")
        icon_cancel = "[+]" if "FAILED" not in cancel_check else "[-]"
        summary += f"{icon_cancel} AFTER CANCEL RESTRICTION: {'PRESENT' if 'FAILED' not in cancel_check else 'MISSING'}\n"

        # Operations Status
        summary += "\nOperations Status:\n"

        # Invoice Details
        invoice_check = next((result for result in project_results if "Fill invoice details" in result), "")
        icon_invoice = "[+]" if "FAILED" not in invoice_check else "[-]"
        summary += f"{icon_invoice} INVOICE DETAILS: {'FILLED' if 'FAILED' not in invoice_check else 'FAILED'}\n"

        # Document Upload
        upload_op_check = next((result for result in project_results if "Document upload" in result), "")
        icon_upload_op = "[+]" if "FAILED" not in upload_op_check else "[-]"
        summary += f"{icon_upload_op} DOCUMENT UPLOAD: {'SUCCESS' if 'FAILED' not in upload_op_check else 'FAILED'}\n"

        # Document Cancel
        cancel_op_check = next((result for result in project_results if "cancellation failed" in result), "")
        icon_cancel_op = "[+]" if not cancel_op_check else "[-]"
        summary += f"{icon_cancel_op} DOCUMENT CANCEL: {'SUCCESS' if not cancel_op_check else 'FAILED'}\n"

        # Final Status
        final_check = next((result for result in project_results if "All checks" in result), "")
        summary += "\nFinal Status:\n"
        icon_final = "[+]" if "PASSED" in final_check else "[-]"
        summary += f"{icon_final} OVERALL TEST: {'PASSED' if 'PASSED' in final_check else 'FAILED'}\n"

        summary += "-" * 30 + "\n"

    return summary

def main():
    print("Starting main function...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        for project_name, url in PROJECTS.items():
            try:
                # 1. Загрузка страницы и проверка начального restriction
                driver.get(url)
                time.sleep(2)
                log_step(f"Navigating to {project_name}")

                wait.until(EC.presence_of_element_located((By.ID, 'login_name'))).send_keys(USERNAME)
                wait.until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(PASSWORD)
                driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
                time.sleep(2)

                # Проверка 1: Должен быть restriction
                if not check_restriction_element(driver, wait, project_name, 'Initial'):
                    TEST_SUMMARY.append(f"{project_name}: Initial check - FAILED (Missing restriction)")
                    continue

                # 2. Загрузка документа
                # Заполняем данные инвойса
                if not fill_invoice_details(driver, wait, project_name):
                    TEST_SUMMARY.append(f"{project_name}: Fill invoice details - FAILED")
                    continue

                # Загружаем файл
                if not upload_and_save_document(driver, wait, project_name):
                    TEST_SUMMARY.append(f"{project_name}: Document upload - FAILED")
                    continue

                # Проверка 2: НЕ должно быть restriction
                if not check_restriction_element(driver, wait, project_name, 'After Upload'):
                    TEST_SUMMARY.append(f"{project_name}: After upload check - FAILED (Restriction still present)")
                    continue

                # Отмена документа
                if not cancel_document(driver, wait, project_name):
                    TEST_SUMMARY.append(f"{project_name}: Document cancellation failed")
                    continue

                # Проверка 3: Должен появиться restriction
                time.sleep(1)  # Дополнительное ожидание перед проверкой
                if not check_restriction_element(driver, wait, project_name, 'After Cancel'):
                    TEST_SUMMARY.append(f"{project_name}: After cancel check - FAILED (Missing restriction)")
                    continue

                TEST_SUMMARY.append(f"{project_name}: All checks - PASSED")

            except Exception as project_error:
                log_step(f"Error processing project {project_name}: {project_error}")
                TEST_SUMMARY.append(f"{project_name}: Unexpected Error - FAILED")

    finally:
        driver.quit()
    formatted_summary = generate_test_summary(TEST_SUMMARY)
    print(formatted_summary)

    if any("FAILED" in result for result in TEST_SUMMARY):
        sys.exit(1)

if __name__ == "__main__":
    main()