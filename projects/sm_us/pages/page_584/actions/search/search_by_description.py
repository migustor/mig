"""
Действие поиска по описанию на странице инвентаря (ID: 584)
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.page_584.locators import SEARCH_FORM, RESULTS

def search_by_description(driver, description):
    """
    Выполняет поиск по описанию товара
    
    Args:
        driver: WebDriver
        description: Текст описания для поиска
        
    Returns:
        bool: Успешность операции
    """
    try:
        # Очищаем поле номера детали, если оно заполнено
        part_field = driver.find_element(*SEARCH_FORM["part_number_field"])
        part_field.clear()
        
        # Ввод описания
        description_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(SEARCH_FORM["description_field"])
        )
        description_input.clear()
        description_input.send_keys(description)
        
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
        print(f"Ошибка при поиске по описанию: {str(e)}")
        return False
