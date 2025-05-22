"""
Локаторы для кнопок удаления и подтверждения ид 905
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
    "weight": "//input[@name='shipping_package_weight_new']"  # Corrected selector for weight
}

# Кнопка сохранения коробки
SAVE_PACKAGE_BUTTON = "//button[@id='save_btn']"

# Новый локатор для выпадающего списка "whse_sector_new"
WHSE_SECTOR_SELECT = "//select[@name='whse_sector_new']"
