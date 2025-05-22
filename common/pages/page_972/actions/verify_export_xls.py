# /trunk/projects/sm_us/pages/page_972/actions/verify_export_xls.py

import logging
import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import glob

from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def verify_export_xls_for_buying(driver, expected_item_id="35033", timeouts=None):
    """
    Downloads the 'Export XLS for Buying' file and verifies that it contains
    the expected item ID in the first column.
    
    Args:
        driver: Selenium WebDriver
        expected_item_id: The item ID to check for in the Excel file (default: "35033")
        timeouts: Optional dict of timeouts
    
    Returns:
        dict: Result with "success" flag and verification details
    """
    logger = logging.getLogger("test")
    logger.info(f"Verifying Export XLS for Buying contains item ID: {expected_item_id}")
    
    action_timeout = timeouts.get("action", 10) if timeouts else 10
    download_timeout = timeouts.get("download", 30) if timeouts else 30
    
    # Фиксированный каталог для скачивания
    download_dir = r"J:\PUB28\E2E_Testing\trunk\tests\documents\124284"
    
    # Создаем директорию, если она не существует
    os.makedirs(download_dir, exist_ok=True)
    
    logger.info(f"Using download directory: {download_dir}")
    
    try:
        # Запоминаем существующие файлы перед скачиванием
        existing_files = set(glob.glob(os.path.join(download_dir, "*.xls*")))
        logger.info(f"Found {len(existing_files)} existing XLS files in download directory")
        
        # Находим и нажимаем кнопку экспорта
        logger.info("Clicking 'Export XLS for Buying' button")
        export_button = WebDriverWait(driver, action_timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-success.export-xls-for-buying"))
        )
        export_button.click()
        
        # Ожидание завершения загрузки
        logger.info(f"Waiting up to {download_timeout} seconds for XLS download")
        max_wait_time = time.time() + download_timeout
        downloaded_file = None
        
        while time.time() < max_wait_time:
            # Проверяем наличие новых файлов, исключая временные .crdownload
            current_files = set(glob.glob(os.path.join(download_dir, "*.xls*")))
            new_files = current_files - existing_files
            
            # Фильтруем только завершенные файлы
            complete_files = [f for f in new_files if not f.endswith('.crdownload')]
            
            if complete_files:
                # Берем самый свежий файл
                downloaded_file = max(complete_files, key=os.path.getmtime)
                logger.info(f"Found completed download: {downloaded_file}")
                
                # Даем время файловой системе завершить запись
                time.sleep(3)
                break
                
            time.sleep(1)
        
        if not downloaded_file:
            # Еще одна попытка найти файл, на случай если только что завершилось скачивание
            current_files = set(glob.glob(os.path.join(download_dir, "*.xls*")))
            complete_files = [f for f in current_files - existing_files if not f.endswith('.crdownload')]
            
            if complete_files:
                downloaded_file = max(complete_files, key=os.path.getmtime)
                logger.info(f"Found downloaded file after final check: {downloaded_file}")
                time.sleep(3)
            else:
                error_msg = "Download timeout: No completed XLS file found in download directory"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
        
        # Анализ файла Excel
        logger.info(f"Checking content of {downloaded_file}")
        try:
            df = pd.read_excel(downloaded_file)
            
            # Выводим имена столбцов и первую строку для отладки
            logger.info(f"Excel columns: {list(df.columns)}")
            logger.info(f"First row: \n{df.head(1)}")
            
            # Проверка наличия столбца Item ID
            if "Item ID" not in df.columns:
                error_msg = f"Column 'Item ID' not found in the Excel file. Available columns: {list(df.columns)}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg, "file_downloaded": True}
            
            # Поиск ожидаемого ID в столбце
            df["Item ID"] = df["Item ID"].astype(str)
            item_id_found = any(expected_item_id in str(id_val) for id_val in df["Item ID"])
            
            if item_id_found:
                # Получаем строку с нужным ID
                item_row = df[df["Item ID"].str.contains(expected_item_id)].iloc[0]
                item_id_value = item_row["Item ID"]
                
                logger.info(f"Found item ID: {item_id_value}")
                
                result = {
                    "success": True,
                    "file_downloaded": True,
                    "item_id_found": True,
                    "actual_item_id": item_id_value
                }
            else:
                error_msg = f"Item ID '{expected_item_id}' not found in any row of the Excel file"
                logger.error(error_msg)
                return {"success": False, "error": error_msg, "file_downloaded": True}
            
        except Exception as e:
            error_msg = f"Error reading Excel file: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "file_downloaded": True}
        
        finally:
            # Удаление скачанного файла
            try:
                if downloaded_file and os.path.exists(downloaded_file):
                    logger.info(f"Deleting downloaded file: {downloaded_file}")
                    os.unlink(downloaded_file)
            except Exception as e:
                logger.warning(f"Error deleting file: {str(e)}")
        
        return result
            
    except TimeoutException:
        error_msg = "Timeout waiting for Export XLS button to be clickable"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except NoSuchElementException:
        error_msg = "Export XLS button not found"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error verifying Export XLS: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}