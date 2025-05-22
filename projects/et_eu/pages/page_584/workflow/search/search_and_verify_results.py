"""
Рабочий процесс поиска с проверкой результатов (ID: 584)
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.page_584.locators import RESULTS
from pages.page_584.actions.search_by_part_number import search_by_part_number
from pages.page_584.actions.search_by_description import search_by_description
from pages.page_584.actions.perform_empty_search import perform_empty_search

def search_and_verify_results(driver, search_type, search_query, expected_count=None):
    """
    Выполняет поиск указанного типа и проверяет результаты
    
    Args:
        driver: WebDriver
        search_type: тип поиска ("part_number", "description", "empty")
        search_query: запрос для поиска (не используется для empty)
        expected_count: ожидаемое количество результатов (опционально)
        
    Returns:
        dict: результаты поиска и проверки
    """
    result = {
        "success": False,
        "search_type": search_type,
        "query": search_query,
        "results_count": None,
        "expected_count": expected_count,
        "count_match": False,
        "error": None
    }
    
    try:
        # Выполнение поиска в зависимости от типа
        if search_type == "part_number":
            search_success = search_by_part_number(driver, search_query)
        elif search_type == "description":
            search_success = search_by_description(driver, search_query)
        elif search_type == "empty":
            search_success = perform_empty_search(driver)
        else:
            result["error"] = f"Неподдерживаемый тип поиска: {search_type}"
            return result
            
        if not search_success:
            result["error"] = "Не удалось выполнить поиск"
            return result
            
        # Проверка наличия результатов
        no_results_messages = driver.find_elements(*RESULTS["no_results_message"])
        if no_results_messages and "No results found" in no_results_messages[0].text:
            result["results_count"] = 0
        else:
            # Получение количества результатов из пагинатора
            try:
                pager_element = driver.find_element(*RESULTS["pager"])
                result["results_count"] = int(pager_element.text.strip())
            except:
                # Если пагинатор не найден, считаем строки таблицы
                rows = driver.find_elements(*RESULTS["rows"])
                result["results_count"] = len(rows)
        
        # Проверка ожидаемого количества, если указано
        if expected_count is not None:
            result["count_match"] = (result["results_count"] == expected_count)
            
        result["success"] = True
        return result
        
    except Exception as e:
        result["error"] = str(e)
        return result
