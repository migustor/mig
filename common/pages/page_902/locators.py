"""
Селекторы package (ID: 902)
"""
from selenium.webdriver.common.by import By

class NewBoxLocators:
    # Поля ввода размеров для нового бокса
    LENGTH_INPUT = (By.ID, "shipping_package_length")
    WIDTH_INPUT = (By.ID, "shipping_package_width")
    HEIGHT_INPUT = (By.ID, "shipping_package_height")
    
    # Поле ввода веса для нового бокса
    WEIGHT_INPUT = (By.ID, "shipping_package_weight_focus")
    WEIGHT_INPUT_NEW = (By.NAME, "shipping_package_weight_new")
    
    # Кнопка сохранения (без учета ID)
    SAVE_BUTTON = (By.CSS_SELECTOR, "button.save_shipping_package")

    # Заголовок страницы
    PAGE_TITLE = (By.ID, "title_page_name")
    
    # Кнопка добавления упаковки (data-so-id будет добавлен в коде)
    ADD_PACKAGE_BUTTON = (By.CSS_SELECTOR, "button.add_shipping_package")
    
    # Блок с сообщениями об ошибках
    ERROR_BLOCK = (By.ID, "error_block_list")
    
    # Поле стоимости доставки (id будет добавлен в коде)
    FREIGHT_COST_INPUT = (By.CSS_SELECTOR, "input[name^='shipping_package_freight_cost_']")
    
    # Индикатор загрузки (id будет добавлен в коде)
    LOADER_ICON = (By.CSS_SELECTOR, "div[id^='freight_cost_loader_']")
    
    # Динамические поля для существующих боксов (используется с форматированием)
    EXISTING_WEIGHT_INPUT = "input[name='shipping_package_weight_{0}']"
    EXISTING_LENGTH_INPUT = "input[name='shipping_package_length_{0}']"
    EXISTING_WIDTH_INPUT = "input[name='shipping_package_width_{0}']"
    EXISTING_HEIGHT_INPUT = "input[name='shipping_package_height_{0}']"
    EXISTING_FREIGHT_COST = "input[name='shipping_package_freight_cost_{0}']"