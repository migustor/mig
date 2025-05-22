# common/pages/page_714/locators.py
"""
Locators for lead history page (ID: 714)
"""
from selenium.webdriver.common.by import By

# Lead history page elements
LEAD_HISTORY_ELEMENTS = {
    "date_diff_dropdown": (By.ID, "lead_date_diff"),
    "dropdown_option_all": (By.CSS_SELECTOR, "option[value='0']"),
    "history_button": (By.CSS_SELECTOR, "#defaultLeadHistory > small"),
    "history_table": (By.CSS_SELECTOR, "#lead_history_content table"),
    "history_rows": (By.CSS_SELECTOR, "#lead_history_content table tr:not(:first-child)"),
    "history_table_row": (By.CSS_SELECTOR, "#lead_history_content table tr:nth-child(2)"),
    "lead_cell": (By.TAG_NAME, "td"),
    "lead_link": (By.TAG_NAME, "a"),
    
    # New locators for item information on page 714
    "ITEM_TABLE": (By.CSS_SELECTOR, "table.table-bordered.table-striped.table-condensed"),
    "INFO_COMPACT": (By.CSS_SELECTOR, "div.info_compact"),
    "ITEM_DESCRIPTION": (By.XPATH, "//strong[@class='item_description']"),
    "QTY_PER_PALLET_SPAN": (By.XPATH, "//span[contains(text(), 'Qty per pallet:')]")
}

# Блок, внутри которого уже отрисованы все данные (замени на точный селектор).
DATA_CONTAINER      = (By.CSS_SELECTOR, "div.panel-body")

# Спиннер/оверлей, который виден, пока идёт запрос (замени, если у тебя другой).
LOADING_SPINNER     = (By.CSS_SELECTOR, "div.loader, div.spinner, div.overlay")

