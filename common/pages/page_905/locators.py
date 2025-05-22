"""
Локаторы для 905 страницы
"""
from selenium.webdriver.common.by import By

# Существующие селекторы
# Кнопка удаления строки
DELETE_ROW_BUTTON = "//td/button[contains(@class, 'btn btn-primary fas fa-trash')]"

# Кнопка подтверждения удаления в pop-up
CONFIRM_DELETE_BUTTON = "//button[contains(@class, 'btn btn-primary') and contains(text(), 'Remove')]"

# Кнопка инициализации создания коробки
ADD_SHIPPING_PACKAGE_BUTTON = "//button[@id='add_shipping_package_button']"

# Поля ввода параметров новой коробки
NEW_BOX_INPUTS = {
    "length": "//input[@id='shipping_package_length']",
    "width": "//input[@id='shipping_package_width']",
    "height": "//input[@id='shipping_package_height']",
    "weight": "//input[@name='shipping_package_weight_new']"
}

# Кнопка сохранения коробки
SAVE_PACKAGE_BUTTON = "//button[@id='save_btn']"

# Новые селекторы для verify_weight_change
BLUR_ELEMENT = (By.TAG_NAME, "body")  # Более надежный элемент для снятия фокуса
WEIGHT_INPUT = (By.CSS_SELECTOR, "input[class*='shipping_package_weight_']")

# Селекторы для add_shipping_package
ADD_PACKAGE_BUTTON = (By.XPATH, ADD_SHIPPING_PACKAGE_BUTTON)  # Переиспользование существующего
LENGTH_INPUT = (By.XPATH, NEW_BOX_INPUTS["length"])  # Переиспользование существующего
WIDTH_INPUT = (By.XPATH, NEW_BOX_INPUTS["width"])    # Переиспользование существующего
HEIGHT_INPUT = (By.XPATH, NEW_BOX_INPUTS["height"])  # Переиспользование существующего
WEIGHT_INPUT_NEW = (By.XPATH, NEW_BOX_INPUTS["weight"])  # Переиспользование существующего
ERROR_BLOCK = (By.CSS_SELECTOR, "div.alert-danger")  # Новый селектор