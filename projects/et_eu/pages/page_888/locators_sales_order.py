from selenium.webdriver.common.by import By

# Таблица, где оказываются добавленные товары
SALES_ORDER_LIST = (By.ID, "sales_order_list_items")

# Функция, чтобы создать локатор строки по атрибуту
def row_by_part_number(part_number: str):
    """
    Строка уже добавленного товара внутри #sales_order_list_items
    """
    return (
        By.XPATH,
        f"//table[@id='sales_order_list_items']"
        f"//tr[@data-sales-order-item-part-number='{part_number}']"
    )

# Дропдаун (шестерёнка) внутри строки
DROPDOWN_HOWER = (
    By.XPATH,
    ".//div[@class='dropdown-hower']"
)

# Ссылка "Delete item..." внутри того же dropdown
DELETE_ITEM_LINK = (
    By.XPATH,
    ".//a[contains(@onclick,'delete_so_item') and contains(text(),'Delete item from this sales order')]"
)

# SweetAlert2 confirm button
SWAL_CONFIRM_BUTTON = (By.CSS_SELECTOR, "button.swal2-confirm")
