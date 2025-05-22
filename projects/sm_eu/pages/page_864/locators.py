"""
Locators for page 864 (PO Getting)
"""
from selenium.webdriver.common.by import By

class Page864Locators:
    # Confirmation dialog buttons
    SUBMIT_BUTTON = (By.XPATH, "//input[@id='submit_btn' and @type='submit']")
    PO_COMPANY = (By.XPATH, "//div[@class='purchase_order_color' and contains(text(), 'Acc PO Type: Company')]")
    PO_PA = (By.XPATH, "//div[@class='purchase_order_color' and contains(text(), 'Acc PO Type: PA')]")
    NET_AMOUNT = (By.XPATH, "//td[contains(.,'€')]//span[contains(@style,'color: #999') and contains(text(),'Net:')]")