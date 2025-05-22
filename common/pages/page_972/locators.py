# /common/pages/page_972/locators.py
"""
Locators for page 972 (two scenarios: with lead_id and without lead_id)
"""

from selenium.webdriver.common.by import By

class Page972WithLeadLocators:
    """
    Locators for creating/approving/closing presale
    when the lead_id is provided in the URL (action=new).
    """

    # Button to place presale effort and notify buying managers
    PLACE_PRESALE_EFFORT_BUTTON = (
        By.XPATH,
        "//button[@type='submit' and contains(@class, 'btn-success') and contains(text(), 'Place Presale Effort')]"
    )

    # Button to approve presale effort and notify sellers
    APPROVE_PRESALE_EFFORT_BUTTON = (By.ID, "approve_effort")

    # Button to confirm the approval in the popup
    CONFIRM_APPROVE_BUTTON = (
        By.XPATH,
        "//button[@class='btn btn-primary' and contains(text(), 'Confirm')]"
    )

    # Button to close the presale effort
    CLOSE_PRESALE_EFFORT_BUTTON = (By.ID, "close_lead")

    # Confirmation button 'Yes!' in the Swal alert
    CONFIRM_CLOSE_BUTTON = (
        By.XPATH,
        "//button[contains(@class, 'swal2-confirm')]"
    )
    
    # Deadline setting elements
    ACCEPT_OFFERS_DEADLINE_RADIO = (
        By.XPATH, 
        "//*[@id='presaleEffortForm']/div/div[2]/div/div[3]/div[1]/div/div[2]/label"
    )
    
    DEADLINE_DATE_FIELD = (By.ID, "accept_offers_deadline")
    
    UPDATE_BUTTON = (
        By.XPATH, 
        "//*[@id='presaleEffortForm']/div/div[3]/div[2]/button[2]"
    )


class Page972WithoutLeadLocators:
    """
    Locators for the scenario when lead_id is NOT provided,
    e.g. searching or other actions on page 972 without 'lead_id_list' in URL.
    """

    # Submit button that triggers the filter-based search
    SEARCH_BUTTON = (
        By.XPATH,
        "//button[@type='submit' and contains(@class, 'btn-primary') and contains(@class, 'xml5') and text()='Submit']"
    )

    # Radio buttons for "Has Items Accepted for Stock":
    HAS_ITEMS_ACCEPTED_YES = (By.ID, "has_items_accepted_for_stock_1")
    HAS_ITEMS_ACCEPTED_NO = (By.ID, "has_items_accepted_for_stock_0")
    HAS_ITEMS_ACCEPTED_BOTH = (By.ID, "has_items_accepted_for_stock_both")