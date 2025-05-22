"""
Селекторы CAS (ID: 830)
"""
from selenium.webdriver.common.by import By

GENERATE_SALES_ORDER_LINK = (
    By.XPATH,
    '//a[contains(@href, "page_id=888") and contains(text(),"Generate Sales Order")]'
)


class Page830Locators:
    SALES_VALUE = (By.CSS_SELECTOR, "span.hdx12:not(.color_green)")
    BUYING_VALUE = (By.CSS_SELECTOR, "span.hdx12.color_green")