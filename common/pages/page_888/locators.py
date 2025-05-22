"""
Селекторы для страницы 888 (Sales Order)
"""
from selenium.webdriver.common.by import By

class Page888Locators:
    # Выпадающий список статусов
    STATUS_DROPDOWN = (By.ID, "status_id")

    # Кнопка сохранения "Update Sales Order"
    SAVE_BUTTON = (By.ID, "surplus_order_btn")
    
    # Селекторы для копирования парт номера и добавления
    PART_NUMBER_CELL = (By.XPATH, "//td[contains(@class, 'part_number')]")
    PART_NUMBER_BOLD = (By.XPATH, ".//span[contains(@class, 'd-block')][1]//b")
    
    # Селекторы для панели "Add More Items"
    ADD_MORE_ITEMS_BUTTON = (By.XPATH, "//h4[contains(text(), 'Add More Items')]")
    SEARCH_TEXTAREA = (By.XPATH, "//*[@id='inventory_search']/div/div[1]/div/textarea")
    SEARCH_BUTTON = (By.XPATH, "//*[@id='html_inventory_search_button']")
    
    # Селекторы для ссылок открытия модальных окон с баркодами
    GET_BARCODES_LINK = (By.XPATH, "//a[starts-with(@onclick, 'get_barcodes')]")
    UPDATE_RESERVED_BARCODES_LINK = (By.XPATH, "//a[starts-with(@onclick, 'updateReservedBarcodes')]")
    
    # Селекторы для модальных окон и предупреждений
    WARNING_TRIANGLE_ICON = (By.CSS_SELECTOR, "td i.fa-exclamation-triangle")
    MODAL_CLOSE_BUTTON = (By.CSS_SELECTOR, ".modal-dialog .close")
    MODAL_DIALOG = (By.CSS_SELECTOR, ".modal-dialog")
    BARCODE_TABLE = (By.CSS_SELECTOR, ".table.table-bordered.table-striped")