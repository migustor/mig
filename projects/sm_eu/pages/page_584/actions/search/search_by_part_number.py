"""
Действие поиска по номеру детали на странице инвентаря (ID: 584)
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.page_584.locators import SEARCH_FORM, RESULTS

def search_by_part_number(driver, part_number):
    """
    Выполняет поиск по номеру детали
    
    Args:
        driver: WebDriver
        part_number: Номер детали для поиска
        
    Returns:
        bool: Успешность операции
    """
    try:
        # Ввод номера детали
        part_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(SEARCH_FORM["part_number_field"])
        )
        part_input.clear()
        part_input.send_keys(part_number)
        
        # Клик по кнопке поиска
        search_button = driver.find_element(*SEARCH_FORM["search_button"])
        search_button.click()
        
        # Ожидание результатов поиска
        WebDriverWait(driver, 15).until(
            lambda d: len(d.find_elements(*RESULTS["rows"])) > 0 or 
                     len(d.find_elements(*RESULTS["no_results_message"])) > 0
        )
        
        return True
    except Exception as e:
        print(f"Ошибка при поиске по номеру детали: {str(e)}")
        return False
