# framework/projects/ra_eu/pages/page_836/locators.py
from selenium.webdriver.common.by import By

class Page836Locators:
    # Submit
    SUBMIT_BUTTON = (By.XPATH, '//button[@type="submit" and contains(@class, "btn-warning") and text()="Submit"]')
    #Company Name
    COMPANY_LINK = (By.CSS_SELECTOR, "tbody tr:first-child td:nth-child(2) a")
    #Company Status
    COMPANY_STATUS_BUTTON = (By.CSS_SELECTOR, "tbody tr:first-child td:nth-child(7) i.company-edit-status-toggle")
    # Селекторы для попапа SweetAlert2
    POPUP_CONTAINER = (By.CSS_SELECTOR, '.swal2-popup')
    POPUP_WARNING_ICON = (By.CSS_SELECTOR, '.swal2-icon.swal2-warning')
    POPUP_TITLE = (By.CSS_SELECTOR, '.swal2-title')
    POPUP_OK_BUTTON = (By.CSS_SELECTOR, '.swal2-confirm')  # Кнопка OK в SweetAlert2
    