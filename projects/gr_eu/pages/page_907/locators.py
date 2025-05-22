# projects/gr_eu/pages/page_907/locators.py
from selenium.webdriver.common.by import By

class Page907Locators:
    """
    Locators for Sales Order tracking page (ID: 907)
    """
    # Form input elements
    ORDER_ID_FIELD = (By.ID, "order_id")
    TRACKING_NUMBER_FIELD = (By.ID, "tracking_number")
    BUILD_REPORT_BUTTON = (By.ID, "build_report")
    
    # Results elements
    RESULT_CONTAINER = (By.XPATH, "//div[@class='col-lg-2 col-md-4 col-sm-6 col-xs-12 b-result']")
    FIRST_TRACKING_LINK = (By.XPATH, "//a[contains(@class,'text-danger clipboard')]")
    SECOND_TRACKING_LINK = (By.XPATH, "//a[contains(@class,'tracking-number text-danger clipboard editable')]")
    FINAL_ORDER_LINK = (By.XPATH, "//a[@class='xml5 result_order_id']")

    # Tracking Number
    TRACKING_NUMBER = (By.XPATH, "//a[contains(@class, 'tracking-number') and contains(@class, 'text-danger')]")

    # Company Name
    COMPANY_NAME = (By.XPATH, "//div[@class='content_block'][./label[text()='Company']]")

    # Order ID
    BAR_RESULT_ORDER_ID = (By.XPATH, "//a[contains(@class, 'result_order_id')]")