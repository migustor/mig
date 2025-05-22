"""
Локаторы для кнопок удаления и подтверждения на странице 905 (Argon)
"""

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
