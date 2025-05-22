from selenium.webdriver.common.by import By

class Page830Locators:
    # Прочие локаторы, если нужны
    SALES_VALUE = (By.XPATH, "//span[contains(text(), 'Sales:')]")
    BUYING_VALUE = (By.XPATH, "//span[contains(text(), 'Buying:')]")
    
    # Локатор для видимого контейнера с email адресами:
    EMAIL_CONTAINER = (By.CSS_SELECTOR, "td.scr_cd_email[id$='_im_column']")
    
    # Локаторы для данных внутри контейнера имейла
    EMAIL_DATA_ELEMENTS = (By.CSS_SELECTOR, "font[id*='__data']")
    EMAIL_TYPE_INPUT = (By.CSS_SELECTOR, "input[name='im_type_id']")
    EMAIL_LINK = (By.CSS_SELECTOR, "a.scr_im.im_mail")
    #SO ID
    SALES_ORDER_TABLE = (By.ID, "legacy_sale_table")
    SALES_ORDER_NUMBER_CELL = (By.CSS_SELECTOR, "#legacy_sale_table tr.changing_data td.alignRight:first-child")
    # Локаторы для статуса компании
    COMPANY_STATUS_CONTAINER = (By.ID, "company_status__editable_row")
    STATUS_EDIT_BUTTON = (By.XPATH, "//div[@id='company_status__editable_row']//a[@class='btnMini3 change']")
    STATUS_EDIT_BUTTON_ALT = (By.XPATH, "//div[contains(@class, 'scr_data') and @id='company_status__editable_row']//div[contains(@class, 'scr_tools')]/a[contains(@class, 'change')]")
    
    # Локатор для предупреждения о ненулевом балансе
    BALANCE_WARNING = (By.CSS_SELECTOR, "p.balance_warning")