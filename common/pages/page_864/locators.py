"""
Locators for page 864 (VAT Checking)
"""
from selenium.webdriver.common.by import By

class Page864Locators:
    # Input fields for Invoice
    VAT_INPUT = (By.CSS_SELECTOR, "input[id*='invoice_vat_amount'], input[name='invoice_vat_amount'], input[class='document_detail_input']")
    INV_NET_INPUT = (By.CSS_SELECTOR, "input[id*='invoice_net_amount'], input[name='invoice_net_amount'], input[class='document_detail_input']")
    
    # Total cell (normal and with red background)
    TOTAL_CELL = (By.CSS_SELECTOR, "td.number_cell:not([style*='background-color'])")
    TOTAL_CELL_RED = (By.CSS_SELECTOR, "td.number_cell[style*='background-color: #ffc1cc']")
    
    # Confirmation dialog buttons
    CONFIRM_YES_BUTTON = (By.XPATH, "//button[contains(text(), 'YES')]")
    CONFIRM_NO_BUTTON = (By.XPATH, "//button[contains(text(), 'NO')]")
    
    # Modal text
    MODAL_TEXT = (By.CSS_SELECTOR, ".modal-body")
    
    # General information
    PAGE_TITLE = (By.ID, "title_page_name")