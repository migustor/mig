# common/pages/page_907/locators.py
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
    
    # Template generation elements
    TEMPLATE_BUTTON = (By.XPATH, "//button[contains(@onclick, 'generateTemplate') and contains(@class, 'btn-success')]")
    MODAL_WINDOW = (By.XPATH, "//div[contains(@class, 'modal-content')]")
    EMAIL_SPAN = (By.XPATH, "//span[contains(text(), '@') and preceding-sibling::span[contains(text(), 'Email:')]]")

    # Shipping package cost elements
    SHIPPING_PACKAGE_COSTS = (By.XPATH, "//a[contains(@class, 'shipping_package_cost text-danger no-link-style editable')]")
    SHIPPING_PACKAGE_COST_BY_ID = lambda box_id: (By.XPATH, f"//a[contains(@class, 'shipping_package_cost') and @data-pk='{box_id}']")