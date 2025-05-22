import logging
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from projects.et_eu.pages.page_888.locators_item_search import row_by_part_number_in_search


from projects.et_eu.pages.page_888.locators_item_search import (
    ERROR_ALERT, ERROR_ALERT_SPAN, ADD_ITEM_BUTTON, ITEM_PRICE_INPUT
)
from projects.et_eu.pages.page_888.locators_sales_order import (
    SALES_ORDER_LIST,
    row_by_part_number
)

logger = logging.getLogger(__name__)

def verify_no_min_qty_item(driver, part_number, test_qty=1, timeout=15):
    """
    Товар без Min Qty:
      1) Находим строку <tr data-item-found-part-number=part_number>
      2) Убеждаемся, что нет 'Min Qty:' внутри
      3) Пробуем добавить qty=test_qty => НЕ должно быть ошибки
      4) Товар добавляется
    """
    wait = WebDriverWait(driver, timeout)

    # 1) Находим строку
    row_loc = row_by_part_number_in_search(part_number)
    try:
        row_el  = wait.until(EC.visibility_of_element_located(row_loc))
    except TimeoutException:
        return {"success": False, "error": f"Row not found for part_number={part_number}"}

    logger.info(f"Found row for part_number={part_number} (no-min-qty).")

    # 2) Проверяем, что нет Min Qty
    try:
        row_el.find_element(By.XPATH, './/span[contains(text(),"Min Qty:")]')
        return {"success": False, "error": f"Unexpected 'Min Qty' found in row for {part_number}"}
    except NoSuchElementException:
        logger.info("No 'Min Qty:' => correct for no-min-qty item")

    # 2.1) Считываем price (если нужно)
    try:
        price_input = row_el.find_element(*ITEM_PRICE_INPUT)
        price_value = float(price_input.get_attribute("value"))
        logger.info(f"Detected price={price_value} for {part_number}")
    except (NoSuchElementException, ValueError):
        logger.info("Unable to parse item_price => 0.0 by default")
        price_value = 0.0

    # 3) Пробуем добавить test_qty
    add_form = row_el.find_element(By.CSS_SELECTOR, "form.add_item")
    qty_input = add_form.find_element(By.NAME, "quantity")
    qty_input.clear()
    qty_input.send_keys(str(test_qty))
    logger.info(f"Entered quantity={test_qty} for {part_number}, expecting no error")

    add_button = add_form.find_element(*ADD_ITEM_BUTTON)
    add_button.click()
    time.sleep(2)

    # 3.1) Проверяем, что нет ошибки
    for loc in (ERROR_ALERT, ERROR_ALERT_SPAN):
        try:
            err_el = row_el.find_element(*loc)
            return {"success": False, "error": f"Unexpected error after adding qty={test_qty}: {err_el.text}"}
        except NoSuchElementException:
            pass

    # 4) Проверяем, что таблица есть
    try:
        wait.until(EC.presence_of_element_located(SALES_ORDER_LIST))
    except TimeoutException:
        return {"success": False, "error": "Sales order list missing?"}

    logger.info(f"Item {part_number} added successfully without min_qty restriction.")
    return {"success": True, "error": None}
