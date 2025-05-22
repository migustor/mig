# common/pages/page_696/locators.py
from selenium.webdriver.common.by import By

class Page696Locators:
    """
    Локаторы для элементов на странице 696.
    """
    # Column selection dropdowns (using the name attribute to identify them)
    COLUMN_1_DROPDOWN = (By.NAME, "column[1]")
    COLUMN_2_DROPDOWN = (By.NAME, "column[2]")
    COLUMN_3_DROPDOWN = (By.NAME, "column[3]")
    COLUMN_4_DROPDOWN = (By.NAME, "column[4]")
    
    # Save configuration button
    SAVE_CONFIG_BUTTON = (By.XPATH, "//input[@type='submit' and contains(@value, 'Save column configuration')]")
    
    # Additional buttons for further processing steps
    SAVE_QUANTITIES_BUTTON = (By.XPATH, '//input[@type="submit" and contains(@value, "Save Quantities and Mark Incorrect Ones")]')
    SKIP_STEP_3_BUTTON = (By.XPATH, '//input[@type="button" and @value="No items found, skip this step" and contains(@onclick, "skipStep(3)")]')
    SKIP_STEP_4_BUTTON = (By.XPATH, '//input[@type="button" and @value="No items found, skip this step" and contains(@onclick, "skipStep(4)")]')
    ADD_PROCESSED_ITEMS_BUTTON = (By.XPATH, '//input[@type="button" and @value="Add processed items to the lead" and contains(@onclick, "submitForm(0)")]')
    BACK_TO_LEAD_EDITOR_BUTTON = (By.XPATH, '//input[@type="button" and @value="Back to Lead Editor"]')