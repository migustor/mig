"""
Селекторы CAS (ID: 830)
"""
from selenium.webdriver.common.by import By

class Page830Locators:
    SALES_VALUE = (By.CSS_SELECTOR, "span.hdx12:not(.color_green)")
    BUYING_VALUE = (By.CSS_SELECTOR, "span.hdx12.color_green")