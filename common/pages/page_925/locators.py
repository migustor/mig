# /common/pages/page_925/locators.py
from selenium.webdriver.common.by import By

# Form elements with multiple selector options for redundancy
FORM_ELEMENTS = {
    "has_yes_offers_radio": (By.ID, "has_yes_offers"),
    "has_yes_offers_label": (By.CSS_SELECTOR, "label[for='has_yes_offers']"),
    "has_no_offers_radio": (By.ID, "has_no_offers"),
    "has_no_offers_label": (By.CSS_SELECTOR, "label[for='has_no_offers']"),
    "submit_button": (By.ID, "search_si"),
    "main_form": (By.ID, "mainForm")
}

# Results table elements
RESULTS_TABLE = {
    "table_panel": (By.CSS_SELECTOR, "div.panel.panel-default"),
    "table_heading": (By.CSS_SELECTOR, "div.panel-heading h4"),
    "table_rows": (By.CSS_SELECTOR, "table.table tbody tr"),
    "si_links": (By.CSS_SELECTOR, "table.table tbody tr td a[href*='&phase=edit&id=']")
}

# Specific cells in the table
TABLE_CELLS = {
    "si_number": (By.CSS_SELECTOR, "td:nth-child(1) a"),
    "company_name": (By.CSS_SELECTOR, "td:nth-child(1) div.text-break a"),
    "created_date": (By.CSS_SELECTOR, "td:nth-child(2)"),
    "created_by": (By.CSS_SELECTOR, "td:nth-child(3)"),
    "status": (By.CSS_SELECTOR, "td:nth-child(4)"),
    "last_note": (By.CSS_SELECTOR, "td:nth-child(5)"),
    "last_activity": (By.CSS_SELECTOR, "td:nth-child(6)"),
    "quantity": (By.CSS_SELECTOR, "td:nth-child(7)"),
    "brand": (By.CSS_SELECTOR, "td:nth-child(8)"),
    "tools": (By.CSS_SELECTOR, "td:nth-child(9) div.dropdown-hower")
}

# SI editor elements
SI_EDITOR_ELEMENTS = {
    "offers_table": (By.CSS_SELECTOR, "div[class^='offer-data_']"),
    "offers_table_rows": (By.CSS_SELECTOR, "div[class^='offer-data_'] table tbody tr"),
    "offer_quantity": (By.CSS_SELECTOR, "span.qty-reserved-in-offer__editable"),
    "offer_price": (By.CSS_SELECTOR, "td:nth-child(2) span"),
    "offer_info": (By.CSS_SELECTOR, "td:nth-child(4)"),
    "accept_offer_button": (By.CSS_SELECTOR, "button[title='Accept Offer']"),
    "decline_offer_button": (By.CSS_SELECTOR, "button[title='Decline Offer']"),
    "update_offer_button": (By.CSS_SELECTOR, "button[title='Update Offer']")
}