# common/pages/page_621/actions/upload_file.py
"""
Модуль для загрузки файлов на странице 621, специфичных для каждого проекта.
"""
import os
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Импортируем локаторы для страницы 621
from common.pages.page_621.locators import Page621Locators

def upload_project_document(driver, project_name, upload_timeout=10):
    """
    Загружает файл, специфичный для проекта на странице 621.
    
    Args:
        driver: Selenium WebDriver
        project_name: Название проекта (например, "ra_eu", "sm_us", и т.д.)
        upload_timeout: Таймаут ожидания элементов загрузки
        
    Returns:
        dict: Результат загрузки {'success': bool, 'error': str или None, 'filename': str или None, 'step': str или None}
    """
    logger = logging.getLogger('test')
    logger.info(f"Starting document upload for project: {project_name} on page 621")
    
    # Step 1: Get file path - preferably from driver.custom_file_path if set
    logger.info("Step 1: Locating document file")
    if hasattr(driver, 'custom_file_path') and driver.custom_file_path:
        file_path = driver.custom_file_path
        filename = os.path.basename(file_path)
        logger.info(f"Using file path from driver: {file_path}")
    else:
        # Fallback to default location if custom path not set
        documents_dir = r"C:\Users\maxim.lupan\Desktop\E2E_Testing\trunk\tests\documents"
        filename = f"{project_name}.xlsx"
        file_path = os.path.join(documents_dir, filename)
        
        if not os.path.exists(file_path):
            error_msg = f"File {filename} not found at: {file_path}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "filename": None, "step": "locate_file"}
            
        logger.info(f"Using default file path: {file_path}")
    
    try:
        # Step 2: Upload the file
        logger.info("Step 2: Uploading document file")
        file_input = WebDriverWait(driver, upload_timeout).until(
            EC.presence_of_element_located(Page621Locators.FILE_INPUT)
        )
        
        # Отправляем путь к файлу напрямую в скрытый input
        logger.info(f"Uploading file: {file_path}")
        file_input.send_keys(file_path)
        
        # Проверяем, что имя файла отображается в поле
        try:
            display_element = WebDriverWait(driver, upload_timeout).until(
                EC.presence_of_element_located(Page621Locators.FILENAME_DISPLAY)
            )
            
            display_value = display_element.get_attribute('value')
            if not display_value:
                logger.warning("Filename display field is empty after upload")
            else:
                logger.info(f"Filename display shows: {display_value}")
        except Exception as e:
            logger.warning(f"Could not verify filename display: {str(e)}")
        
        # Ждем немного, чтобы дать время для завершения загрузки файла
        time.sleep(1)
        
        logger.info(f"Successfully uploaded file for project {project_name}")
        return {"success": True, "error": None, "filename": filename, "step": "upload_completed"}
            
    except TimeoutException as te:
        error_msg = f"Timeout occurred: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "filename": filename, "step": "timeout_error"}
        
    except NoSuchElementException as nse:
        error_msg = f"Element not found: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "filename": filename, "step": "element_not_found"}
        
    except Exception as e:
        error_msg = f"Unexpected error during file upload: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "filename": filename, "step": "general_error"}

def process_uploaded_document(driver, upload_timeout=10):
    """
    Обрабатывает уже загруженный файл на странице 621. Запускает процесс обработки.
    Должен вызываться ПОСЛЕ нажатия на кнопку создания.
    
    Args:
        driver: Selenium WebDriver
        upload_timeout: Таймаут ожидания элементов
        
    Returns:
        dict: Результат обработки {'success': bool, 'error': str или None, 'step': str или None}
    """
    logger = logging.getLogger('test')
    logger.info("Starting document processing after create button click on page 621")
    
    try:
        # Step 1: Click the process file button
        logger.info("Step 1: Clicking the process file button")
        process_button = WebDriverWait(driver, upload_timeout).until(
            EC.element_to_be_clickable(Page621Locators.PROCESS_FILE_BUTTON)
        )
        process_button.click()
        time.sleep(2)  # Give time for processing to start and complete
        
        logger.info("Successfully initiated file processing")
        return {"success": True, "error": None, "step": "processing_initiated"}
            
    except TimeoutException as te:
        error_msg = f"Timeout occurred during processing: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "step": "timeout_error"}
        
    except NoSuchElementException as nse:
        error_msg = f"Element not found during processing: {str(nse)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "step": "element_not_found"}
        
    except Exception as e:
        error_msg = f"Unexpected error during file processing: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg, "step": "general_error"}