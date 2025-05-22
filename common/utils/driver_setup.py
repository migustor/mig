from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from typing import Optional
import logging
import os
import time
import uuid
import psutil
import tempfile
import traceback

# Логгер для всего модуля
logger = logging.getLogger('driver_setup')
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def setup_chrome_driver(headless: bool = True, download_dir: Optional[str] = None, 
                        with_retry: bool = True, max_retries: int = 3, 
                        test_id: str = None) -> webdriver.Chrome:
    """
    Создает новый экземпляр Chrome WebDriver (без сложностей пула)
    
    Args:
        headless: Запускать ли в headless режиме
        download_dir: Директория для загрузок
        with_retry: Использовать ли повторные попытки
        max_retries: Количество попыток
        test_id: Идентификатор теста (для логирования)
    
    Returns:
        Новый экземпляр Chrome WebDriver
    """
    test_id = test_id or f"test_{str(uuid.uuid4())[:8]}"
    logger.info(f"Creating Chrome WebDriver for test {test_id}")
    
    if not with_retry:
        return _create_driver(headless, download_dir, test_id)
    
    # С повторными попытками
    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Driver creation attempt {attempt}/{max_retries}")
            driver = _create_driver(headless, download_dir, test_id)
            return driver
        except Exception as e:
            logger.error(f"Failed to create driver (attempt {attempt}): {str(e)}")
            last_exception = e
            if attempt < max_retries:
                wait_time = 5 * attempt
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
    
    # Если все попытки исчерпаны
    if last_exception:
        raise last_exception
    else:
        raise Exception("Failed to create driver after multiple attempts")

def _create_driver(headless: bool, download_dir: Optional[str], test_id: str) -> webdriver.Chrome:
    """
    Внутренняя функция создания драйвера
    """
    # Создаем временную директорию для профиля Chrome
    temp_dir = tempfile.mkdtemp(prefix=f"webdriver_{test_id}_")
    
    # Настраиваем опции Chrome
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={temp_dir}")
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    
    if download_dir:
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "safebrowsing.enabled": False
        }
        options.add_experimental_option("prefs", prefs)
    
    try:
        # Создаем драйвер
        service = webdriver.ChromeService(
            log_output=os.path.join(temp_dir, f"chromedriver_{uuid.uuid4().hex}.log")
        )
        driver = webdriver.Chrome(options=options, service=service)
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(30)
        
        # Сохраняем информацию о драйвере
        driver._test_id = test_id
        driver._temp_dir = temp_dir
        driver._creation_time = time.time()
        
        # Запоминаем PID процесса браузера для последующей очистки
        if hasattr(driver, 'service') and hasattr(driver.service, 'process') and driver.service.process:
            driver._process_id = driver.service.process.pid
        
        logger.info(f"Driver created successfully for test {test_id}")
        return driver
        
    except Exception as e:
        logger.error(f"Error creating driver: {str(e)}")
        # Пытаемся очистить временную директорию в случае ошибки
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
        raise

def release_driver(driver: webdriver.Chrome, quit: bool = True):
    """
    Освобождает драйвер и завершает все связанные процессы
    
    Args:
        driver: WebDriver для освобождения
        quit: Всегда True в этой реализации (для совместимости)
    """
    test_id = getattr(driver, '_test_id', 'unknown')
    logger.info(f"Quitting driver for test {test_id}")
    
    try:
        # Пытаемся корректно завершить драйвер
        driver.quit()
    except Exception as e:
        logger.warning(f"Error during normal driver quit: {str(e)}")
    
    # Принудительно убиваем процесс браузера, если он все еще существует
    if hasattr(driver, '_process_id'):
        try:
            process = psutil.Process(driver._process_id)
            
            # Получаем все дочерние процессы
            children = []
            try:
                children = process.children(recursive=True)
            except:
                pass
            
            # Убиваем все дочерние процессы
            for child in children:
                try:
                    if child.is_running():
                        child.kill()
                except:
                    pass
            
            # Убиваем основной процесс
            if process.is_running():
                process.kill()
                logger.info(f"Forcefully killed browser process {driver._process_id}")
        except:
            pass
    
    # Удаляем временную директорию
    if hasattr(driver, '_temp_dir'):
        try:
            import shutil
            shutil.rmtree(driver._temp_dir, ignore_errors=True)
            logger.info(f"Removed temporary directory: {driver._temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary directory: {str(e)}")
    
    logger.info(f"Driver successfully quit for test {test_id}")

def with_driver(func):
    """
    Декоратор для автоматического управления жизненным циклом драйвера
    """
    def wrapper(*args, **kwargs):
        # Используем str() для преобразования UUID в строку
        test_id = f"{func.__name__}_{str(uuid.uuid4())[:8]}"
        driver = setup_chrome_driver(test_id=test_id)
        try:
            return func(driver, *args, **kwargs)
        finally:
            release_driver(driver)
    return wrapper