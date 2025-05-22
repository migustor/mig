# common/pages/page_903/locators.py
from selenium.webdriver.common.by import By

class Page903Locators:
    """
    Locators for Page 903 (Document Preview/Edit)
    """
    # Shipping cost fields
    SHIPPING_COST_ROW = (By.CSS_SELECTOR, "tbody tr")
    SHIPPING_COST_INPUTS = (By.CSS_SELECTOR, "input[name*='shipping_cost']")
    
    # Page elements
    BODY = (By.TAG_NAME, "body")