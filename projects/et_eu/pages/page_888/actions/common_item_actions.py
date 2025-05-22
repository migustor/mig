import logging
from selenium.common.exceptions import NoSuchElementException

from projects.et_eu.pages.page_888.locators import ITEM_PRICE_INPUT

logger = logging.getLogger(__name__)

def get_item_price_in_row(row_element):
    """
    Извлекает float-значение цены из скрытого инпута: <input name="item_price" value="4.00">
    row_element – это <tr> или <form> или другой контейнер, внутри которого лежит input[name="item_price"].
    """
    try:
        price_input_el = row_element.find_element(*ITEM_PRICE_INPUT)
        price_value_str = price_input_el.get_attribute("value")  # например "4.00"
        return float(price_value_str)
    except (NoSuchElementException, ValueError) as e:
        logger.warning(f"Cannot find or parse item_price in row: {e}")
        return 0.0
