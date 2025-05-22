"""
Селекторы package (ID: 902)
"""
from selenium.webdriver.common.by import By

class NewBoxLocators:
    # Поля ввода размеров
    LENGTH_INPUT = (By.ID, "shipping_package_length")
    WIDTH_INPUT = (By.ID, "shipping_package_width")
    HEIGHT_INPUT = (By.ID, "shipping_package_height")
    
    # Поле ввода веса
    WEIGHT_INPUT = (By.ID, "shipping_package_weight_focus")

    # Кнопка сохранения (без учета ID)
    SAVE_BUTTON = (By.CSS_SELECTOR, "button.save_shipping_package")

    # Заголовок страницы
    PAGE_TITLE = (By.ID, "title_page_name")
