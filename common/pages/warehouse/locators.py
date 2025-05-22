from selenium.webdriver.common.by import By

class WarehouseLocators:
    # Общие элементы страницы (до попапа)
    MAIN_PAGE_ELEMENTS = {
        "so_id_input": (By.ID, "so_id"),
        "view_button": (By.XPATH, "//input[@type='submit' and @value='View']"),
        "orders_table": (By.CSS_SELECTOR, "div#result table.goods"),
        "loading_indicator": (By.ID, "ajaxLoadingDiv")
    }

    # Ссылки
    ORDER_ELEMENTS = {
        "ship_details_link": (By.XPATH, "//a[contains(@href, 'f_enterShipDetails') and contains(@style, 'color: red')]"),
        "specific_order_link": lambda order_id: (By.XPATH, f"//a[contains(@href, 'f_enterShipDetails({order_id})')]")
    }

    # Попап (внутри iframe!)
    POPUP_ELEMENTS = {
        "iframe": lambda so_id: (By.ID, f"ship_template_{so_id}"),
        "popup_container": (By.TAG_NAME, "body"),  # внутри iframe body есть всё
        "box_weight_input": lambda box_id: (By.ID, f"box_weight_{box_id}"),
        "cost_input": lambda box_id: (By.ID, f"cost_{box_id}"),
        "close_button": (By.ID, "close_ship_template")  # может быть не нужен
    }

    # Локаторы для добавления нового бокса
    NEW_BOX_ELEMENTS = {
        "add_new_box_link": (By.ID, "new_box_link"),
        "width_input": (By.NAME, "shipping_package_width"),
        "length_input": (By.NAME, "shipping_package_length"),
        "height_input": (By.NAME, "shipping_package_height"),
        "weight_input": (By.NAME, "shipping_package_weight_new"),
        "carrier_select": (By.NAME, "shipping_package_carrier_id"),
        "warning_message": (By.XPATH, "//font[@color='red' and contains(text(), 'Please contact Logistics to get shipping cost!')]")
    }