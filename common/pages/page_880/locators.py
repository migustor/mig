"""
Locators for the Orders Page (ID: 880)
"""
from selenium.webdriver.common.by import By

class OrdersPageLocators:
    # Build Report Button
    BUILD_REPORT_BUTTON = (By.ID, "build_report")
    
    # Date range elements
    DATE_RANGE_CONTAINER = (By.ID, "input-daterange-date_range")
    DATE_FROM_INPUT = (By.ID, "date_range_from")
    DATE_TO_INPUT = (By.ID, "date_range_till")
    
    # Results count element
    RESULTS_COUNT = (By.XPATH, "//h4[contains(text(), 'Results found:')]")
    
    # Table elements
    TABLE = (By.CSS_SELECTOR, "table")
    TABLE_HEADERS = (By.CSS_SELECTOR, "table thead tr th")
    TABLE_ROWS = (By.CSS_SELECTOR, "table tbody tr")
    FIRST_ROW = (By.CSS_SELECTOR, "table tbody tr:first-child")
    
    # Specific for data rows (for testing)
    TABLE_DATA_ROWS = (By.CSS_SELECTOR, "table tbody tr")
    
    # Multiselect dropdown (for et_eu special case)
    MULTISELECT_DROPDOWN = (By.CSS_SELECTOR, "button.multiselect.dropdown-toggle")
    SHOPIFY_CHECKBOX = (By.XPATH, "//label[contains(@class, 'checkbox')]/input[@value='85']")
    
    # E-commerce indicators
    EBAY_INDICATOR = (By.CSS_SELECTOR, "[title='eBay']")
    AMAZON_INDICATOR = (By.CSS_SELECTOR, "[title='Amazon']")
    MYSUPPLYSHOP_INDICATOR = (By.CSS_SELECTOR, "[title='Mysupplyshop']")
    ALZURA_INDICATOR = (By.CSS_SELECTOR, "[title='Alzura']")
    
    # Column cells for specific columns
    FREIGHT_TAX_CELL = (By.CSS_SELECTOR, "td:nth-child(11)")  # Adjust index as needed
    GP_CELL = (By.CSS_SELECTOR, "td:nth-child(13)")  # Adjust index as needed
    
    # Other elements
    SITE_INFO = (By.CSS_SELECTOR, "td.site-info")
    SALES_REP_INFO = (By.CSS_SELECTOR, "td.sales-rep-info")