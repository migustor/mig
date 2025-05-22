import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from projects.et_eu.pages.page_830.actions.click_generate_sales_order import click_generate_sales_order
from projects.et_eu.pages.page_888.actions.click_create_sales_order import click_create_sales_order
from projects.et_eu.pages.page_888.actions.click_add_more_items_panel import click_add_more_items_panel

from projects.et_eu.pages.page_888.actions.input_part_number_and_search import input_part_number_and_search
from projects.et_eu.pages.page_888.actions.verify_min_qty_and_add_item import verify_min_qty_and_add_item
from projects.et_eu.pages.page_888.actions.verify_no_min_qty_item import verify_no_min_qty_item
from projects.et_eu.pages.page_888.actions.delete_item_from_so import delete_item_from_so

logger = logging.getLogger(__name__)

def run_generate_sales_order_flow(driver, timeouts):
    """
    Демонстрационный workflow:
      1) Переход на page_id=830 + company_id=59390
      2) "Generate Sales Order" -> новая вкладка
      3) "Create Sales Order"
      4) "Add More Items", вводим "07147075520" -> есть min_qty -> добавляем -> удаляем
      5) "Add More Items", вводим "S99999" -> нет min_qty -> добавляем -> удаляем
    """
    try:
        # 1) Идём на 830
        url_830 = "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=830&company_id=59390"
        driver.get(url_830)
        time.sleep(2)
        logger.info("Opened page 830")

        # 2) Клик Generate
        window_handles_before = driver.window_handles
        gen_res = click_generate_sales_order(driver, timeouts.get("action", 15))
        if not gen_res["success"]:
            return gen_res
        time.sleep(2)

        # Переключимся, если реально открылась новая вкладка
        window_handles_after = driver.window_handles
        if len(window_handles_after) > len(window_handles_before):
            new_tab = list(set(window_handles_after) - set(window_handles_before))[0]
            driver.switch_to.window(new_tab)
            logger.info("Switched to new tab for page_id=888")

        # 3) Create Sales Order
        create_res = click_create_sales_order(driver, timeouts.get("action", 15))
        if not create_res["success"]:
            return create_res
        time.sleep(3)

        # 4) Кликаем "Add More Items"
        add_items_res = click_add_more_items_panel(driver, timeouts.get("action", 15))
        if not add_items_res["success"]:
            return add_items_res
        time.sleep(2)

        # 4.1) Первый товар: 07147075520 (min_qty)
        search_res = input_part_number_and_search(driver, "07147075520", timeouts.get("action", 15))
        if not search_res["success"]:
            return search_res
        time.sleep(5)

        min_qty_res = verify_min_qty_and_add_item(driver, "07147075520", timeouts.get("action", 15))
        if not min_qty_res["success"]:
            return min_qty_res
        time.sleep(5)

        del_first = delete_item_from_so(driver, "07147075520", timeouts.get("action", 15))
        if not del_first["success"]:
            return del_first
        logger.info("Deleted first item (07147075520).")

        # 5) Второй товар: S99999 (no_min_qty)
        # возможно панель свернулась, открываем ещё раз
        add2 = click_add_more_items_panel(driver, timeouts.get("action", 15))
        if not add2["success"]:
            return add2
        time.sleep(2)

        search2 = input_part_number_and_search(driver, "S99999", timeouts.get("action", 15))
        if not search2["success"]:
            return search2

        no_min_qty_res = verify_no_min_qty_item(driver, "S99999", test_qty=2, timeout=timeouts.get("action",15))
        if not no_min_qty_res["success"]:
            return no_min_qty_res

        del_second = delete_item_from_so(driver, "S99999", timeouts.get("action", 15))
        if not del_second["success"]:
            return del_second
        logger.info("Deleted second item (S99999).")

        logger.info("All items tested and removed successfully.")
        return {"success": True, "error": None}

    except Exception as e:
        err = f"Exception in run_generate_sales_order_flow: {str(e)}"
        logger.error(err)
        return {"success": False, "error": err}
