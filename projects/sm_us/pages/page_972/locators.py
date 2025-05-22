# /trunk/projects/sm_us/pages/page_972/locators.py

from selenium.webdriver.common.by import By

class AddOfferLocators:
    """
    Locators for adding offers to a presale
    """
    ADD_OFFER_BUTTON = (By.XPATH, "//*[@id='item-container']/table/tbody/tr/td[7]/button")
    COMPANY_AUTOCOMPLETE_FIELD = (By.XPATH, "//*[@id='offer_company_autocompleter']")
    AUTOCOMPLETE_DROPDOWN = (By.CSS_SELECTOR, "ul.typeahead.dropdown-menu")
    QUANTITY_FIELD = (By.XPATH, "//*[@id='quantity']")
    PRICE_FIELD = (By.XPATH, "//*[@id='add_offer_form']/div/div[2]/div/div[4]/div/input")
    SUBMIT_BUTTON = (By.XPATH, "//*[@id='add_pe_offer']")
    
    @staticmethod
    def get_autocomplete_item_selector(company_id):
        """Get selector for a specific company ID in the autocomplete dropdown"""
        return (By.XPATH, f"//ul[contains(@class, 'typeahead')]/li[@data-value='{company_id}']")

class ExpiredOffersLocators:
    """
    Locators for expired offers functionality verification
    """
    # Expired offers elements
    EXPIRED_OFFER_ROW = (By.CSS_SELECTOR, "tr.offer_expired")
    CREATOR_NAME = (By.CSS_SELECTOR, "span.offer_expired")
    PRICE_COLOR_RED = (By.CSS_SELECTOR, "span.color-red")
    
    # Action buttons
    ACCEPT_BUTTON = (By.CSS_SELECTOR, "button.btn-success[title='Accept Offer']")
    EDIT_BUTTON = (By.CSS_SELECTOR, "button[title='Update Offer']")
    DECLINE_BUTTON = (By.CSS_SELECTOR, "button.btn-danger[title='Decline Offer']")
    
    # Export XLS button
    EXPORT_XLS_BUTTON = (By.XPATH, "//button[contains(text(), 'Export XLS with Sales Offers')]")