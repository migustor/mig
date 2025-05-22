# /common/pages/page_953/locators.py
from selenium.webdriver.common.by import By

# Form elements for Vendor Evolution Report page
VENDOR_EVOLUTION_FORM = {
    "company_name_input": (By.ID, "company_name"),
    "company_autocomplete_dropdown": (By.CLASS_NAME, "typeahead"),
    "company_autocomplete_item": (By.XPATH, "//ul[contains(@class, 'typeahead')]/li[contains(@class, 'active')]"),
    "date_from_field": (By.ID, "datepicker_from"),
    "date_to_field": (By.ID, "datepicker_to"),
    "submit_button": (By.XPATH, "//input[@value='Submit']"),
}

# Result section elements
REPORT_RESULTS = {
    "purchase_history_section": (By.ID, "purchase_history"),
    "purchase_history_table": (By.XPATH, "//div[@id='purchase_history']//table"),
    "export_button": (By.XPATH, "//button[contains(@onclick, 'vendorEvolutionExportPurchaseHistory')]"),
    "po_links": (By.XPATH, "//a[contains(@href, 'po_id')]"),
    "spm_links": (By.XPATH, "//a[contains(@href, 'item_id')]"),
    "items_rows": (By.XPATH, "//div[@id='purchase_history']//table/tbody[2]/tr[not(contains(@class, 'th2')) and not(contains(td[1], 'Export'))]"),
    "table_headers": (By.XPATH, "//div[@id='purchase_history']//table/tbody/tr[@class='th2']/th"),
    "expected_header_count": 8,
    "expected_headers": ["PO ID", "Date", "Part Number", "Item Description", "BC", "Qty", "Cost", ""] 
}

# Error messages and notifications
ERROR_MESSAGES = {
    "no_data_found": (By.XPATH, "//div[contains(text(), 'No data found')]"),
    "validation_error": (By.CLASS_NAME, "alert-danger"),
}