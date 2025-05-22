# common/pages/page_22/locators.py
"""
Селекторы для страницы (ID: 22)
"""
from selenium.webdriver.common.by import By

class Page22Locators:
    # Поля ввода для количества на поддон (могут быть динамически добавлены)
    QUANTITY_PER_PALLET_INPUT_1 = (By.ID, "quantity_per_pallet_1")
    QUANTITY_PER_PALLET_INPUT_2 = (By.ID, "quantity_per_pallet_2")
    QUANTITY_PER_PALLET_INPUT_3 = (By.ID, "quantity_per_pallet_3")
    QUANTITY_PER_PALLET_INPUT_4 = (By.ID, "quantity_per_pallet_4")
    
    # Кнопка добавления нового поля для количества
    ADD_NEW_QUANTITY_BUTTON = (By.XPATH, "//a[contains(text(), 'add new Qty per Pallet')]")
    
    # Кнопка сохранения формы
    SAVE_BUTTON = (By.ID, "save_btn")
    
    # Общий локатор для всех полей количества (для поиска всех сразу)
    ALL_QUANTITY_INPUTS = (By.CSS_SELECTOR, ".quantity_per_pallet_input")
    
    # Функция для получения локатора поля ввода по номеру
    @staticmethod
    def get_quantity_input(index):
        return (By.ID, f"quantity_per_pallet_{index}")