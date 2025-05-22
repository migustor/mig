import logging
import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from projects.et_eu.pages.page_888.locators_item_search import row_by_part_number_in_search


from projects.et_eu.pages.page_888.locators_item_search import (
    ERROR_ALERT,
    ERROR_ALERT_SPAN,
    ADD_ITEM_BUTTON,
    ITEM_PRICE_INPUT,
    MIN_QTY_DIV_LOCATOR,
)
from projects.et_eu.pages.page_888.locators_sales_order import (
    SALES_ORDER_LIST,
    row_by_part_number
)

logger = logging.getLogger(__name__)

def verify_min_qty_and_add_item(driver, part_number, timeout=15):
    """
    Для товара, у которого есть "Min Qty: X".
    1) Находим строку <tr data-item-found-part-number=part_number>
    2) Ищем <span>Min Qty: X</span>, парсим X
    3) Получаем price через input[name="item_price"]
    4) Пробуем ввести qty < minQty => ловим ошибку
    5) Вводим ровно minQty => товар успешно добавляется
    """
    wait = WebDriverWait(driver, timeout)

    # 1) Ищем строку
    row_loc = row_by_part_number_in_search(part_number)
    try:
        row_el  = wait.until(EC.visibility_of_element_located(row_loc))
    except TimeoutException:
        return {"success": False, "error": f"Row not found for part_number={part_number}"}

    logger.info(f"Row found for part_number={part_number}")

    # 2) Ищем span Min Qty
    try:
        min_qty_div = row_el.find_element(*MIN_QTY_DIV_LOCATOR)
        min_qty_text = min_qty_div.text              # «Min Qty: 7»
        logger.info(f"Found min_qty_text: {min_qty_text}")

        # извлекаем только число
        min_qty = int(re.search(r'(\d+)', min_qty_text).group(1))

    except Exception:
        # если div не найден — выдаём ошибку
        return {
            "success": False,
            "error": f"Min Qty div not found for {part_number}"
        }

    # 3) Получаем price
    try:
        price_input = row_el.find_element(*ITEM_PRICE_INPUT)
        price_str = price_input.get_attribute("value")  # "1.00", "4.00", ...
        price_value = float(price_str)
    except (NoSuchElementException, ValueError):
        price_value = 0.0
    logger.info(f"Detected price={price_value} for part_number={part_number}")

    # 4) Пробуем ввести меньше
    less_qty = max(1, min_qty - 2)
    add_form = row_el.find_element(By.CSS_SELECTOR, "form.add_item")
    qty_input = add_form.find_element(By.NAME, "quantity")
    qty_input.clear()
    qty_input.send_keys(str(less_qty))
    logger.info(f"Entered less_qty={less_qty} < min_qty={min_qty} for {part_number}")

    add_btn = add_form.find_element(*ADD_ITEM_BUTTON)
    add_btn.click()
    time.sleep(2)

    # Ловим ошибку
    error_found = False
    for loc in (ERROR_ALERT, ERROR_ALERT_SPAN):
        try:
            err_el = row_el.find_element(*loc)
            if str(min_qty) in err_el.text:
                logger.info(f"Got expected error => {err_el.text}")
                error_found = True
                break
        except NoSuchElementException:
            pass

    if not error_found:
        return {"success": False, "error": "No min_qty error appeared after adding too few items."}

    # 5) Вводим ровно minQty
    qty_input.clear()
    qty_input.send_keys(str(min_qty))
    logger.info(f"Entered min_qty={min_qty} for {part_number}")

    add_btn.click()
    time.sleep(2)

    # Проверяем отсутствие ошибки
    for loc in (ERROR_ALERT, ERROR_ALERT_SPAN):
        try:
            err_el = row_el.find_element(*loc)
            return {"success": False, "error": f"Error still present after adding correct qty => {err_el.text}"}
        except NoSuchElementException:
            pass

    # Убеждаемся, что таблица всё ещё есть
    try:
        wait.until(EC.presence_of_element_located(SALES_ORDER_LIST))
    except TimeoutException:
        return {"success": False, "error": "Sales order list missing after adding correct qty?"}

    logger.info(f"Successfully added item {part_number} with min_qty={min_qty}.")
    return {"success": True, "error": None}
