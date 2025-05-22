from selenium.webdriver.common.by import By

# Текстовое поле для Part Number
PART_NUMBER_TEXTAREA = (By.NAME, "item_part_number")

# Кнопка Search
SEARCH_BUTTON = (By.ID, "html_inventory_search_button")

# Таблица результатов поиска
SEARCH_RESULTS_TABLE = (
    By.XPATH,
    '//table[contains(@class,"table-bordered") and contains(@class,"table-striped") and contains(@class,"xvalignmiddle")]'
)
MIN_QTY_DIV_LOCATOR = (
    By.XPATH,
    './/div[starts-with(@id,"label_min_sell_qty_") and contains(text(),"Min Qty")]'
)
# Для добавления товара (форма, поля и т. д.)
ADD_ITEM_FORM = (By.CSS_SELECTOR, "form.add_item")

# Поле "Qty" (name="quantity") — обычно ищем внутри формы add_item
QTY_INPUT = (By.NAME, "quantity")

# Кнопка "Add" (внутри формы add_item)
ADD_ITEM_BUTTON = (
    By.XPATH,
    './/button[@type="submit" and contains(text(),"Add")]'
)

# Возможные варианты ошибки (div или span)
ERROR_ALERT = (
    By.XPATH,
    '//div[contains(@class,"alert alert-danger") and contains(text(),"minimum qty which can be added to SO")]'
)

ERROR_ALERT_SPAN = (
    By.XPATH,
    '//span[@id="quantity-error" and contains(text(),"minimum qty which can be added to SO")]'
)

SPINNER = (By.CSS_SELECTOR, "i.fa-spinner.fa-spin")

# Скрытый input c ценой, например <input name="item_price" value="4.00">
ITEM_PRICE_INPUT = (
    By.XPATH,
    './/input[@name="item_price"]'
)
def row_by_part_number_in_search(part_number: str):
    """
    Строка <tr data-item-found-part-number="..."> внутри таблицы
    результатов поиска («Add More Items»).
    Таблица не имеет ID, поэтому ищем по сочетанию CSS‑классов.
    """
    return (
        By.XPATH,
        f"//table[contains(@class,'table-bordered') "
        f"and contains(@class,'xvalignmiddle')]"
        f"//tr[@data-item-found-part-number='{part_number}']"
    )