from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options 
import logging
import time
from typing import Dict, List, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Конфигурация систем
SYSTEMS_CONFIG = {
    "RA Trading": {
        "base_url": "https://stage15.office.ratrading.eu",
        "username": "maxim.lupan@mteam.md",
        "password": "12",
        "valid_id": "1040"
    },
    "AGAVA": {
        "base_url": "https://stage15.office.agavasystem.com",
        "username": "maxim.lupan@mteam.md",
        "password": "12",
        "valid_id": "1040"
    },
    "SM USA": {
        "base_url": "https://stage15.office.sovamaxusa.com",
        "username": "maxim.lupan@mteam.md",
        "password": "12",
        "valid_id": "1040"
    },
    "SM EU": {
        "base_url": "https://stage15.office.sovasystem.com",
        "username": "maxim.lupan@mteam.md",
        "password": "12",
        "valid_id": "1040"
    },
    "Eminia": {
        "base_url": "https://stage15.office.eminiasystem.com",
        "username": "maxim.lupan@mteam.md",
        "password": "12",
        "valid_id": "1040"
    },
    "Lanius": {
        "base_url": "https://stage15.office.laniustoys.com",
        "username": "maxim.lupan@mteam.md",
        "password": "12",
        "valid_id": "1040"
    },
    "DB": {
        "base_url": "https://stage15.office.dbreactor.com",
        "username": "maxim.lupan@mteam.md",
        "password": "12",
        "valid_id": "10"
    },
    "Horus": {
        "base_url": "https://stage28.office.horustrading.eu",
        "username": "maxim.lupan@mteam.md",
        "password": "12",
        "valid_id": "10"
    },
    "Atlas": {
        "base_url": "https://stage15.office.atlastradingworld.com",
        "username": "maxim.lupan@mteam.md",
        "password": "12",
        "valid_id": "10"
    }
}

def login(driver: webdriver.Chrome, system_config: Dict) -> bool:
    """Выполняет вход в систему"""
    logging.info(f"Logging in to {system_config['base_url']} as {system_config['username']}")
    driver.get(f"{system_config['base_url']}/sage/index.cfm?page_id=442")
    try:
        username_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "login_name")))
        password_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "password")))
        username_input.send_keys(system_config['username'])
        password_input.send_keys(system_config['password'])
        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()

        WebDriverWait(driver, 15).until(
            EC.invisibility_of_element_located((By.ID, "login_name"))
        )
        logging.info("Login successful")
        return True
    except TimeoutException:
        logging.error("Timeout occurred while logging in")
        return False
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")
        return False

def check_page_status(driver: webdriver.Chrome, wait: WebDriverWait, expect_success: bool = False) -> bool:
    """
    Проверяет статус страницы
    Args:
        driver: WebDriver
        wait: WebDriverWait
        expect_success: True если ожидаем успешную загрузку, False для ошибки
    """
    try:
        if expect_success:
            # Для валидного ID сначала проверяем успешную загрузку
            try:
                panel_heading = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.panel-heading h4"))
                )
                logging.info(f"Success: Found {panel_heading.text}")
                return True
            except TimeoutException:
                # Проверяем ошибку, если успех не найден
                error_div = driver.find_element(By.CSS_SELECTOR, "div.alert.alert-danger")
                if error_div.is_displayed():
                    logging.info("Error message found when success expected")
                    return False
        else:
            # Для невалидного ID сначала проверяем ошибку
            try:
                error_div = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.alert.alert-danger"))
                )
                if error_div.is_displayed():
                    logging.info("Error message found as expected")
                    return False
            except TimeoutException:
                # Проверяем успех, если ошибка не найдена
                try:
                    panel_heading = driver.find_element(By.CSS_SELECTOR, "div.panel-heading h4")
                    logging.info(f"Success found when error expected: {panel_heading.text}")
                    return True
                except:
                    return None

    except Exception as e:
        logging.error(f"Error checking page status: {str(e)}")
        return None

def test_problem_sale_request(driver: webdriver.Chrome, system_config: Dict, test_id: str) -> bool:
   """Тестирует конкретный ID"""
   url = f"{system_config['base_url']}/sage/index.cfm?page_id=936&action=update&id={test_id}"
   wait = WebDriverWait(driver, 10)

   try:
       logging.info(f"Testing URL with ID: {test_id}")
       driver.get(url)

       # Определяем, ожидаем ли успешную загрузку
       should_succeed = test_id == system_config['valid_id']

       page_status = check_page_status(driver, wait, expect_success=should_succeed)

       if page_status is None:
           logging.error(f"Test INCONCLUSIVE for ID={test_id}")
           return False

       if page_status == should_succeed:
           logging.info(f"Test PASSED for ID={test_id}")
           return True
       else:
           logging.error(
               f"Test FAILED for ID={test_id}. "
               f"Expected {'successful load' if should_succeed else 'error message'}, "
               f"but got {'error message' if should_succeed else 'successful load'}"
           )
           return False

   except Exception as e:
       logging.error(f"Error testing ID {test_id}: {str(e)}")
       return False

def test_system(driver: webdriver.Chrome, system_name: str, system_config: Dict) -> List[Tuple[str, bool]]:
    """Тестирует одну систему"""
    logging.info(f"\nTesting system: {system_name}")
    print(f"\nTesting system: {system_name}")
    print("-" * 50)

    results = []

    # Логинимся в систему
    if not login(driver, system_config):
        logging.error(f"Login failed for {system_name}, skipping tests")
        return results

    # ID для тестирования
    test_ids = [
        system_config['valid_id'],  # Валидный ID
        "abc",                      # Некорректный формат
        "999999",                   # Несуществующий ID
        "0",                        # Нулевой ID
        "-1"                        # Отрицательный ID
    ]

    # Тестируем каждый ID
    for test_id in test_ids:
        result = test_problem_sale_request(driver, system_config, test_id)
        results.append((test_id, result))
        time.sleep(2)

    return results

def main():
    driver = None
    try:
        # Add headless mode configuration
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')  # Required for Windows
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)  # Pass the options here
        driver.maximize_window()

        all_results = {}

      
        for system_name, system_config in SYSTEMS_CONFIG.items():
            results = test_system(driver, system_name, system_config)
            all_results[system_name] = results

            if results:
                print(f"\nResults for {system_name}:")
                print("-" * 30)
                for test_id, result in results:
                    status = "PASSED" if result else "FAILED"
                    print(f"ID {test_id}: {status}")

                total_passed = sum(1 for _, result in results if result)
                print(f"\nTotal: {len(results)} tests")
                print(f"Passed: {total_passed}")
                print(f"Failed: {len(results) - total_passed}")

        print("\nOverall Statistics:")
        print("=" * 50)
        for system_name, results in all_results.items():
            if results:
                passed = sum(1 for _, result in results if result)
                total = len(results)
                print(f"{system_name}: {passed}/{total} passed")

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
