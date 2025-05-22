# common/pages/page_621/locators.py
from selenium.webdriver.common.by import By

class Page621Locators:
    """
    Локаторы для элементов на странице 621.
    """
    # Unchanged locators (kept exactly as provided)
    RADIO_BUTTON_SHOULD_BE_USED = (By.XPATH, "//input[@name='use_in_presale' and @value='1']")
    CREATE_BUTTON = (By.XPATH, "//button[@type='submit' and contains(@class, 'btn-primary') and contains(text(), 'Create')]")
    FILE_INPUT = (By.ID, "browse_document")
    BROWSE_BUTTON = (By.XPATH, "//label[contains(@class, 'file-form-input-group__button')]")
    FILENAME_DISPLAY = (By.XPATH, "//input[contains(@class, 'file-form-input-group__input')]")
    LEAD_ID_HEADER = (By.XPATH, "//h1[@id='title_page_name']")
    LEAD_STATUS_DROPDOWN = (By.ID, "lead_status_id")
    SAVE_CHANGES_BUTTON = (By.XPATH, "//button[@type='submit' and contains(@class, 'btn btn-primary')]")
    SUCCESS_ALERT = (By.XPATH, "//div[contains(@class, 'alert-success')]")
    # Process file elements
    PROCESS_FILE_BUTTON = (By.XPATH, "//a[contains(@class, 'process-file-link')]")
    LEAD_ITEMS_TABLE = (By.CSS_SELECTOR, "table.table-bordered.table-hover")
    QTY_PER_PALLET_SPAN = (By.XPATH, "//span[contains(text(), 'Qty per pallet:')]")
    
    # Locators for extracting item ID and part number
    ITEM_HISTORY_LINK = (By.XPATH, "//a[contains(@href, 'page_id=714') and contains(@title, 'SPM')]")
    PART_NUMBER_STRONG = (By.XPATH, "//td/strong[not(contains(@class, 'item_description'))]")
    
    # Locators for search panel
    ADD_ITEM_PANEL_HEADER = (By.ID, "lead_add_item_show")
    PANEL_BODY = (By.XPATH, "//div[@id='lead_add_item_show']/following-sibling::div[@class='panel-body']")
    PART_NUMBER_SEARCH_INPUT = (By.ID, "ism_second_part_number")
    SEARCH_BUTTON = (
        By.XPATH,
        "//form[@id='search_items_module_form']//div[@class='panel-footer']//button[@type='submit' and contains(@class, 'btn-primary')]"
    )
    
    # Locators for search results
    SEARCH_RESULTS_TABLE = (By.CSS_SELECTOR, "table.table-bordered.table-striped.item_result")
    SEARCH_RESULT_ITEM_DESCRIPTION = (By.CSS_SELECTOR, "strong.item_description")
    SEARCH_RESULT_QTY_PER_PALLET_SPAN = (By.XPATH, "//table[contains(@class, 'item_result')]//span[contains(text(), 'Qty per pallet:')]")

    # Дополнительные селекторы для управления позициями в результатах поиска
    ITEM_QUANTITY_INPUT = (By.CSS_SELECTOR, "input[id^='item_']")  # Общий селектор для полей ввода количества
    SEARCH_RESULTS_ADD_BUTTON = (By.CSS_SELECTOR, "#ism_search_results button.btn.btn-primary[type='submit']")
    
    # Селекторы для отметки товаров как presale
    ITEM_CHECKBOX = (By.XPATH, "//input[@type='checkbox' and @name='delete_items'][1]")
    ALL_ITEM_CHECKBOXES = (By.XPATH, "//input[@type='checkbox' and @name='delete_items']")
    MARK_AS_PRESALE_BUTTON = (By.XPATH, "//button[contains(text(), 'Mark Selected Items As Presale')]")
    PRESALE_CONFIRM_BUTTON = (By.XPATH, "//button[@onclick='mark_item_as_presale(1)']")