"""
Действие выполнения пустого поиска на странице инвентаря (ID: 584)
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.page_584.locators import SEARCH_FORM, RESULTS

def perform_empty_search(driver):
    """
    Выполняет поиск без заданных критериев (пустой поиск)
    
    Args:
        driver: WebDriver
        
    Returns:
        bool: Успешность операции
    """
    try:
        # Очищаем все поля поиска
        fields = [
            SEARCH_FORM["part_number_field"],
            SEARCH_FORM["description_field"]
        ]
        
        for field_locator in fields:
            try:
                field = driver.find_element(*field_locator)
                field.clear()
            except:
                # Игнорируем, если поле не найдено
                pass
                
        # Нажимаем сначала Reset, чтобы гарантированно сбросить все фильтры
        try:
            reset_button = driver.find_element(*SEARCH_FORM["reset_button"])
            reset_button.click()
            # Небольшая пауза для обработки сброса
            WebDriverWait(driver, 2).until(
                lambda d: True
            )
        except:
            # Игнорируем, если кнопка Reset не найдена
            pass
            
        # Клик по кнопке поиска
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(SEARCH_FORM["search_button"])
        )
        search_button.click()
        
        # Ожидание загрузки результатов
        WebDriverWait(driver, 15).until(
            lambda d: len(d.find_elements(*RESULTS["rows"])) > 0 or 
                     len(d.find_elements(*RESULTS["no_results_message"])) > 0
        )
        
        return True
    except Exception as e:
        print(f"Ошибка при выполнении пустого поиска: {str(e)}")
        return False
