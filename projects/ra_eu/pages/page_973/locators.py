"""
Локаторы для страницы поиска Alzura (ID: 973)
"""
from selenium.webdriver.common.by import By

# Элементы поиска
SEARCH_ELEMENTS = {
    "search_type_dropdown": (By.CSS_SELECTOR, '#additional_search_criteria_type'),
    "search_input": (By.CSS_SELECTOR, '#additional_search_criteria'),
    "submit_button": (By.CSS_SELECTOR, '#submit_form'),
    "reset_button": (By.CSS_SELECTOR, '#reset_form')
}

# Элементы результатов
RESULT_ELEMENTS = {
    "results_table": (By.CSS_SELECTOR, 'table.table'),
    "alzura_links": (By.CSS_SELECTOR, 'a[href*="supplier.alzura.com"]'),
    "result_message": (By.CSS_SELECTOR, '.alert')
}

# Специфичные для Alzura
ALZURA_TYPES = {
    "alzura_option_value": "alzura_order_id",
    "alzura_option_text": "Alzura order id"
}
