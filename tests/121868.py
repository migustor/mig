import os
import random
import time
import logging
import uuid
import base64
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    InvalidArgumentException,
    TimeoutException,
    WebDriverException,
)

# Load environment variables from .env file
load_dotenv()

# Configure logging
DETAILED_LOGS = False
if DETAILED_LOGS:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Systems configuration
systems = [
    {
        'name': 'Sovamax',
        'login_url': 'https://stage4.office.sovasystem.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage4.office.sovasystem.com/sage/index.cfm?page_id=903&phase=edit&project_short_name=sm_eu&id=15041'
    },
    {
        'name': 'RA',
        'login_url': 'https://stage4.office.ratrading.eu/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage4.office.ratrading.eu/sage/index.cfm?page_id=903&phase=edit&project_short_name=ra_eu&id=5402'
    },
    {
        'name': 'Atlas',
        'login_url': 'https://stage4.office.atlastradingworld.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage4.office.atlastradingworld.com/sage/index.cfm?page_id=903&phase=edit&project_short_name=at_EU&id=129'
    },
    {
        'name': 'Eminia',
        'login_url': 'https://stage4.office.eminiasystem.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage4.office.eminiasystem.com/sage/index.cfm?page_id=903&phase=edit&project_short_name=et_eu&id=8056'
    },
    {
        'name': 'Lanius',
        'login_url': 'https://stage4.office.laniustoys.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage4.office.laniustoys.com/sage/index.cfm?page_id=903&phase=edit&project_short_name=lt_eu&id=3479'
    },
    {
        'name': 'DbReactor',
        'login_url': 'https://stage4.office.dbreactor.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage4.office.dbreactor.com/sage/index.cfm?page_id=903&phase=edit&project_short_name=dr_EU&id=164'
    },
    {
        'name': 'Horus',
        'login_url': 'https://stage4.office.horustrading.eu/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage4.office.horustrading.eu/sage/index.cfm?page_id=903&phase=edit&project_short_name=ho_EU&id=176'
    },
    {
        'name': 'SovamaxUSA',
        'login_url': 'https://stage4.office.sovamaxusa.com/sage/index.cfm?page_id=442',
        'notifications_url': 'https://stage4.office.sovamaxusa.com/sage/index.cfm?page_id=903&phase=edit&project_short_name=sm_us&id=350'
    }
]

# Valid and invalid file extensions
valid_extensions = [
    'ods', 'xlsm', 'jpg', 'jpe', 'jpeg', 'png', 'gif', 'pdf', 'bmp', 'mp3', 'tif', 'ott', 'html', 'xls',
    'wpd', 'rpt', 'stw', 'wps', 'efx', 'dif', 'rar', 'xps', 'tiff', 'fax', 'ots', 'xlr', 'prn', 'doc',
    'vcf', 'txt', 'htm', 'xml', 'sxc', 'csv', 'odt', 'mht', 'ef', 'dat', 'eml', 'zip', 'xlsx', 'rtf',
    'xlt', 'sql', 'docx', 'abw', 'sxw'
]

invalid_extensions = [
    'exe', 'bat', 'cmd', 'sh', 'py', 'js', 'dll', 'sys', 'bin', 'com', 'vbs',
    'cpl', 'msc', 'scr', 'jar', 'php', 'asp', 'jsp', 'cgi', 'pl', 'msi'
]

# Minimal image data
image_data = {
    'gif': 'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
    'jpeg': '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=',
    'png': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=',
    'bmp': 'Qk06AAAAAAAAADYAAAAoAAAAAQAAAAEAAAABABgAAAAAAAQAAADEDgAAxA4AAAAAAAAAAAAA////AA==',
    'jpe': '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='
}

# Supported MIME types
supported_formats = {
    'jpg': 'image/jpeg', 'jpe': 'image/jpeg', 'jpeg': 'image/jpeg',
    'png': 'image/png', 'gif': 'image/gif', 'bmp': 'image/bmp',
    'tif': 'image/tiff', 'tiff': 'image/tiff', 'mp3': 'audio/mpeg',
    'pdf': 'application/pdf', 'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xls': 'application/vnd.ms-excel',
    'xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'csv': 'text/csv', 'txt': 'text/plain', 'htm': 'text/html',
    'html': 'text/html', 'xml': 'application/xml', 'zip': 'application/zip',
    'rar': 'application/x-rar-compressed', 'rtf': 'application/rtf',
    'xlt': 'application/vnd.ms-excel', 'sql': 'application/sql',
    'abw': 'application/x-abiword', 'sxw': 'application/vnd.sun.xml.writer',
    'rpt': 'application/octet-stream', 'wps': 'application/vnd.ms-works',
    'wpd': 'application/wordperfect', 'odt': 'application/vnd.oasis.opendocument.text',
    'ott': 'application/vnd.oasis.opendocument.text-template',
    'sxc': 'application/vnd.sun.xml.calc',
    'stw': 'application/vnd.sun.xml.writer.template',
    'efx': 'application/octet-stream', 'dif': 'application/octet-stream',
    'xps': 'application/vnd.ms-xpsdocument', 'fax': 'image/fax-g3',
    'ots': 'application/vnd.oasis.opendocument.spreadsheet-template',
    'xlr': 'application/vnd.ms-works', 'prn': 'application/octet-stream',
    'vcf': 'text/vcard', 'mht': 'message/rfc822', 'eml': 'message/rfc822',
    'ef': 'application/octet-stream', 'dat': 'application/octet-stream',
    'ods': 'application/vnd.oasis.opendocument.spreadsheet'
}

# Helper functions
def random_text(length=10):
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=length))

def random_number(length=5):
    return ''.join(random.choices('0123456789', k=length))

def create_temp_file(directory, prefix, extension, content="Dummy content"):
    os.makedirs(directory, exist_ok=True)
    unique_id = uuid.uuid4().hex
    filename = f"{prefix}_{unique_id}.{extension}"
    filepath = os.path.join(directory, filename)
    with open(filepath, "w") as file:
        file.write(content)
    return filepath

def create_temp_image_file(directory, prefix, extension="png"):
    os.makedirs(directory, exist_ok=True)
    unique_id = uuid.uuid4().hex
    filename = f"{prefix}_{unique_id}.{extension}"
    filepath = os.path.join(directory, filename)
    from PIL import Image
    import numpy as np
    image_array = np.random.rand(100, 100, 3) * 255
    img = Image.fromarray(image_array.astype('uint8')).convert('RGB')
    img.save(filepath)
    return filepath

def delete_file_with_retry(file_path, max_attempts=5, delay=1):
    attempts = 0
    while attempts < max_attempts:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Deleted file {file_path} after upload.")
                return True
            else:
                logging.warning(f"File {file_path} does not exist.")
                return False
        except Exception as e:
            logging.error(f"Attempt {attempts + 1}: Error deleting file {file_path}: {e}")
            attempts += 1
            time.sleep(delay)
    logging.error(f"Failed to delete file {file_path} after {max_attempts} attempts.")
    return False

def insert_file_via_js(driver, extension):
    """Функция для основных файлов"""
    mime_type = supported_formats.get(extension.lower(), 'application/octet-stream')

    if extension.lower() in image_data:
        file_content_base64 = image_data[extension.lower()]
        js_code = f"""
            var fileInput = document.getElementById('document_file');
            if (!fileInput) {{
                console.error('[File Insert] File input not found');
            }} else {{
                var base64Data = '{file_content_base64}';
                var byteCharacters = atob(base64Data);
                var byteNumbers = new Array(byteCharacters.length);
                for (var i = 0; i < byteCharacters.length; i++) {{
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }}
                var byteArray = new Uint8Array(byteNumbers);
                var blob = new Blob([byteArray], {{ type: '{mime_type}' }});
                var file = new File([blob], 'test_document.{extension}', {{type: '{mime_type}'}});
                var dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;
                fileInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                fileInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        """
    else:
        sample_content = base64.b64encode(b'Sample content for test file upload').decode('utf-8')
        js_code = f"""
            var fileInput = document.getElementById('document_file');
            if (!fileInput) {{
                console.error('[File Insert] File input not found');
            }} else {{
                var byteCharacters = atob('{sample_content}');
                var byteNumbers = new Array(byteCharacters.length);
                for (var i = 0; i < byteCharacters.length; i++) {{
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }}
                var byteArray = new Uint8Array(byteNumbers);
                var blob = new Blob([byteArray], {{ type: '{mime_type}' }});
                var file = new File([blob], 'test_document.{extension}', {{type: '{mime_type}'}});
                var dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;
                fileInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                fileInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        """
    driver.execute_script(js_code)

def insert_file_via_js_additional(driver, input_element):
    """Простая и работающая версия вставки файла"""
    js_code = """
        var fileInput = arguments[0];
        var file = new File(['test content'], 'invoice.xlsx', {type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
        var dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
        fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        fileInput.dispatchEvent(new Event('input', { bubbles: true }));
    """
    driver.execute_script(js_code, input_element)

def upload_file(driver, wait, file_path, expect_error=False, notifications_url=None):
    """Функция для загрузки основных файлов"""
    max_retries = 3
    retry_delay = 3
    retry_count = 0
    extension = os.path.splitext(file_path)[1].lstrip('.')
    last_error = None

    while retry_count < max_retries:
        try:
            # Перезагрузка страницы при повторной попытке
            if retry_count > 0:
                logging.info(f"Retry attempt {retry_count + 1}/{max_retries} for file {file_path}")
                driver.get(notifications_url)
                time.sleep(3)

            # Поиск элемента загрузки
            upload_element = wait.until(
                EC.element_to_be_clickable((By.ID, "document_file"))
            )

            driver.execute_script("""
                arguments[0].style.display = 'block';
                arguments[0].style.visibility = 'visible';
                arguments[0].opacity = '1';
                arguments[0].disabled = false;
                arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});
            """, upload_element)

            time.sleep(1)

            # Вставка файла через JavaScript
            logging.info(f"Attempt {retry_count + 1}: Injecting file via JS with extension: {extension}")
            insert_file_via_js(driver, extension)

            # Проверка выбора файла
            files_selected = driver.execute_script(
                "return document.getElementById('document_file').files.length"
            )

            if files_selected == 0:
                raise Exception("File was not selected after injection")

            # Нажатие кнопки сохранения
            save_button = wait.until(
                EC.element_to_be_clickable((By.ID, "btn_upload_lgst_docs"))
            )
            driver.execute_script("arguments[0].click();", save_button)

            # Обработка ожидаемых результатов
            if expect_error:
                error_element = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@for='document_file' and @class='error2']")
                    )
                )
                error_text = error_element.text
                if error_text:
                    logging.info(f"Expected error received: {error_text}")
                    return True

            else:
                # Ожидание сообщения об успехе с внутренними повторами
                message_checks = 5
                message_delay = 2

                for i in range(message_checks):
                    try:
                        success_element = wait.until(
                            EC.presence_of_element_located((By.ID, "logistics_docs"))
                        )
                        success_text = success_element.text.strip()
                        logging.info(f"Attempt {retry_count + 1}, Check {i + 1}: Message text: '{success_text}'")

                        if "Logistics Document is uploaded!" in success_text:
                            logging.info(f"File upload successful on attempt {retry_count + 1}")
                            return True

                        if i < message_checks - 1:
                            time.sleep(message_delay)

                    except Exception as check_error:
                        if i < message_checks - 1:
                            time.sleep(message_delay)
                            continue
                        raise

                raise Exception("Success message not found after all checks")

        except Exception as e:
            last_error = str(e)
            logging.error(f"Upload attempt {retry_count + 1} failed: {last_error}")

            # Сохранение отладочной информации
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            debug_dir = "failures"
            os.makedirs(debug_dir, exist_ok=True)

            try:
                driver.save_screenshot(f"{debug_dir}/failure_{timestamp}_{os.path.basename(file_path)}.png")
                with open(f"{debug_dir}/page_source_{timestamp}_{os.path.basename(file_path)}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
            except Exception as capture_error:
                logging.error(f"Failed to capture debug info: {str(capture_error)}")

            retry_count += 1
            if retry_count < max_retries:
                time.sleep(retry_delay)
                continue

            return False

    logging.error(f"File upload failed after {max_retries} attempts. Last error: {last_error}")
    return False

def input_additional_file(driver, wait, file_path):
    """Функция для загрузки инвойса"""
    try:
        logging.info("Starting invoice upload process...")

        # Заполнение формы
        select = wait.until(EC.presence_of_element_located((By.ID, "in_supplier_inv_prefix")))
        Select(select).select_by_visible_text("Invoice")
        time.sleep(1)

        supplier_inv = wait.until(EC.presence_of_element_located((By.ID, "in_supplier_inv")))
        supplier_inv.clear()
        supplier_inv.send_keys("TEST123")

        amount = wait.until(EC.presence_of_element_located((By.ID, "in_amount_inv")))
        amount.clear()
        amount.send_keys("100")

        # Загрузка файла
        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        logging.info(f"Found {len(file_inputs)} file inputs")

        if len(file_inputs) > 3:
            invoice_input = file_inputs[3]
            logging.info(f"Working with invoice input: {invoice_input.get_attribute('id')}")

            # Делаем элемент видимым
            driver.execute_script("""
                arguments[0].style.display = 'block';
                arguments[0].style.visibility = 'visible';
                arguments[0].style.position = 'static';
                arguments[0].style.opacity = '1';
                arguments[0].disabled = false;
            """, invoice_input)
            time.sleep(1)

            # Вставляем файл
            logging.info("Inserting file...")
            insert_file_via_js_additional(driver, invoice_input)
            time.sleep(1)

            # Нажатие Save
            try:
                save_button = wait.until(EC.element_to_be_clickable((By.ID, "btn_upload_inv")))
                save_button.click()
                time.sleep(2)

                # Проверка результата
                result = wait.until(EC.presence_of_element_located((By.ID, "result_inv")))
                result_text = result.text
                logging.info(f"Upload result: {result_text}")

                if "Invoice is uploaded!" in result_text:
                    logging.info("Invoice upload successful")
                    return True
                else:
                    logging.error(f"Unexpected result message: {result_text}")
                    return False

            except Exception as e:
                logging.error(f"Failed to complete upload: {str(e)}")
                return False

        else:
            raise Exception("File input element not found")

    except Exception as e:
        logging.error(f"Invoice upload failed: {str(e)}")
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        debug_dir = "failures"
        os.makedirs(debug_dir, exist_ok=True)

        try:
            driver.save_screenshot(f"{debug_dir}/invoice_error_{timestamp}.png")
            with open(f"{debug_dir}/page_source_{timestamp}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except Exception as capture_error:
            logging.error(f"Failed to save debug info: {str(capture_error)}")

        return False

def insert_credit_note(driver, wait):
    """Функция для вставки кредитной ноты"""
    try:
        logging.info("Starting credit note upload process...")

        # Генерация случайных данных
        random_supplier_number = str(random.randint(1, 99999))
        random_amount = str(random.randint(1, 9999))

        # Заполняем Supplier Credit Note #
        supplier_credit = wait.until(EC.presence_of_element_located((By.ID, "in_supplier_cnote")))
        supplier_credit.clear()
        supplier_credit.send_keys(random_supplier_number)
        logging.info(f"Set Supplier Credit Note # to: {random_supplier_number}")

        # Заполняем Credit Note Amount
        amount = wait.until(EC.presence_of_element_located((By.ID, "in_amount_cnote")))
        amount.clear()
        amount.send_keys(random_amount)
        logging.info(f"Set Credit Note Amount to: {random_amount}")

        # Находим file input для кредитной ноты
        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        credit_note_input = file_inputs[4]  # Предполагаем, что это 5-й input

        # Делаем элемент видимым
        driver.execute_script("""
            arguments[0].style.display = 'block';
            arguments[0].style.visibility = 'visible';
            arguments[0].style.position = 'static';
            arguments[0].style.opacity = '1';
            arguments[0].disabled = false;
        """, credit_note_input)
        time.sleep(1)

        # Создаем и вставляем файл
        js_code = """
            var fileInput = arguments[0];
            var file = new File(['test content'], 'credit_note.pdf', {type: 'application/pdf'});
            var dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
            fileInput.dispatchEvent(new Event('input', { bubbles: true }));
        """
        driver.execute_script(js_code, credit_note_input)
        time.sleep(1)

        # Нажимаем Save для кредитной ноты
        save_button = wait.until(EC.element_to_be_clickable((By.ID, "btn_upload_cnote")))
        save_button.click()
        time.sleep(2)

        # Проверяем результат
        result = wait.until(EC.presence_of_element_located((By.ID, "result_cnote")))
        result_text = result.text
        logging.info(f"Credit note upload result: {result_text}")

        if "Credit Note is uploaded!" in result_text:
            logging.info("Credit note upload successful")
            return True
        else:
            logging.error(f"Unexpected credit note result message: {result_text}")
            return False

    except Exception as e:
        logging.error(f"Credit note upload failed: {str(e)}")
        return False

def test_system(system, driver, wait, upload_dir):
    max_system_retries = 2
    system_attempt = 0
    failed_files = []

    try:
        logging.info(f"\nTesting system: {system['name']}")

        # Login process
        driver.get(system['login_url'])
        login_input = wait.until(EC.presence_of_element_located((By.NAME, "login_name")))
        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))

        login_input.send_keys(os.getenv("DEFAULT_USERNAME"))
        password_input.send_keys(os.getenv("DEFAULT_PASSWORD"))
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

        if "login" in driver.current_url.lower():
            raise Exception("Login failed - still on login page")

        # Navigate to notifications page
        driver.get(system['notifications_url'])
        time.sleep(5)

        # Тестирование инвойса
        while system_attempt <= max_system_retries:
            try:
                logging.info(f"\nTesting invoice upload - Attempt {system_attempt + 1}")
                xlsx_file = create_temp_file(upload_dir, f"additional_file_{system['name']}", "xlsx")

                if input_additional_file(driver, wait, xlsx_file):
                    logging.info("Invoice upload successful!")

                    # После успешной загрузки инвойса пробуем загрузить кредитную ноту
                    logging.info("\nTesting credit note upload")
                    if insert_credit_note(driver, wait):
                        logging.info("Credit note upload successful!")
                    else:
                        failed_files.append("Credit note upload failed")

                    break
                else:
                    raise Exception("Invoice upload failed")

            except Exception as e:
                logging.error(f"Invoice upload attempt {system_attempt + 1} failed: {str(e)}")
                system_attempt += 1

                if system_attempt <= max_system_retries:
                    logging.info(f"Retrying invoice upload - Attempt {system_attempt + 1}")
                    try:
                        supplier_inv = wait.until(EC.presence_of_element_located((By.ID, "in_supplier_inv")))
                        supplier_inv.clear()
                        amount = wait.until(EC.presence_of_element_located((By.ID, "in_amount_inv")))
                        amount.clear()
                        time.sleep(2)
                    except:
                        pass
                    continue
                else:
                    logging.error("All invoice upload attempts failed")
                    return {"system": system['name'], "passed": False, "failed_files": ["Invoice upload failed"]}

        # Тестирование остальных файлов
        logging.info("\nTesting valid file extensions:")
        for ext in valid_extensions:
            try:
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'jpe', 'tif', 'tiff']:
                    file_path = create_temp_image_file(upload_dir, f"valid_file_{system['name']}", ext)
                else:
                    file_path = create_temp_file(upload_dir, f"valid_file_{system['name']}", ext)

                logging.info(f"Testing file with extension: {ext}")
                if not upload_file(driver, wait, file_path, notifications_url=system['notifications_url']):
                    failed_files.append(f"Valid file: {ext}")
                time.sleep(3)
            except Exception as e:
                failed_files.append(f"Valid file {ext}: {str(e)}")
                logging.error(f"Error testing {ext}: {str(e)}")

        # Test invalid files
        logging.info("\nTesting invalid file extensions:")
        for ext in invalid_extensions:
            try:
                file_path = create_temp_file(upload_dir, f"invalid_file_{system['name']}", ext)
                logging.info(f"Testing invalid file with extension: {ext}")
                if not upload_file(driver, wait, file_path, expect_error=True, notifications_url=system['notifications_url']):
                    failed_files.append(f"Invalid file test failed: {ext}")
                time.sleep(3)
            except Exception as e:
                failed_files.append(f"Invalid file {ext}: {str(e)}")
                logging.error(f"Error testing invalid {ext}: {str(e)}")

        if not failed_files:
            logging.info("\nAll tests passed successfully!")
            return {"system": system['name'], "passed": True, "failed_files": []}
        else:
            return {"system": system['name'], "passed": False, "failed_files": failed_files}

    except Exception as e:
        logging.error(f"\nTest failed on {system['name']}: {str(e)}")
        return {"system": system['name'], "passed": False, "failed_files": [str(e)]}

def main():
    upload_dir = "test_uploads"

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/118.0.0.0 Safari/537.36')
    chrome_options.add_argument('--lang=ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7')

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 30)

    summary = []
    try:
        for system in systems:
            logging.info(f"Testing system: {system['name']}")
            result = test_system(system, driver, wait, upload_dir)
            summary.append(result)
            if not result['passed']:
                logging.error(f"Test failed for system: {system['name']}")
            else:
                logging.info(f"Test passed for system: {system['name']}")

            driver.delete_all_cookies()
            driver.get('about:blank')
            time.sleep(2)
    finally:
        driver.quit()

        logging.info("\n" + "="*50)
        logging.info("DETAILED TEST SUMMARY")
        logging.info("="*50)

        for item in summary:
            logging.info(f"\nSystem: {item['system']}")
            if item['passed']:
                logging.info("Status: [PASSED]")
                logging.info("Additional files:")
                logging.info("  - Invoice (xlsx): [OK]")
                logging.info("  - Credit Note (pdf): [OK]")
                logging.info("Valid extensions: All formats uploaded successfully")
                logging.info("Invalid formats: All blocked as expected")
            else:
                logging.info("Status: [FAILED]")
                failed = item['failed_files']

                # Анализ ошибок и группировка по типам
                invoice_failed = any("Invoice upload failed" in f for f in failed)
                credit_note_failed = any("Credit note upload failed" in f for f in failed)
                valid_fails = [f.split(': ')[1] for f in failed if f.startswith('Valid file:')]
                invalid_fails = [f.split(': ')[1] for f in failed if f.startswith('Invalid file test failed:')]

                # Вывод результатов
                logging.info("Additional files:")
                logging.info(f"  - Invoice (xlsx): {'[FAILED]' if invoice_failed else '[OK]'}")
                logging.info(f"  - Credit Note (pdf): {'[FAILED]' if credit_note_failed else '[OK]'}")

                if valid_fails:
                    logging.info("Failed valid formats:")
                    logging.info(f"  {', '.join(valid_fails)}")

                if invalid_fails:
                    logging.info("Issues with blocking invalid formats:")
                    logging.info(f"  {', '.join(invalid_fails)}")

            logging.info("-"*50)

        # Общая статистика
        total_systems = len(summary)
        passed_systems = sum(1 for item in summary if item['passed'])

        logging.info("\nOVERALL STATISTICS")
        logging.info(f"Total systems tested: {total_systems}")
        logging.info(f"Systems passed: {passed_systems}")
        logging.info(f"Systems failed: {total_systems - passed_systems}")
        logging.info(f"Success rate: {(passed_systems/total_systems)*100:.1f}%")
        logging.info("="*50)

        if os.path.exists(upload_dir) and not os.listdir(upload_dir):
            os.rmdir(upload_dir)

if __name__ == "__main__":
    main()
