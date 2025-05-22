import logging
import time

# Actions
from projects.gr_eu.pages.page_907.actions.set_order_status_filters_po import set_order_status_filters_po
from projects.gr_eu.pages.page_907.actions.build_report import build_report
from projects.gr_eu.pages.page_907.actions.get_first_three_orders import get_first_three_orders
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def filter_and_get_orders_workflow_po(driver, timeouts=None):
    """
    1) Set order status filter to Waiting for Pick-Up + Waiting for Arrival
    2) Build report
    3) Retrieve first three order IDs
    """
    logger = logging.getLogger(' - TEST - ')
    logger.info("Starting filter_and_get_orders_workflow_po")

    result = {
        "success": False,
        "order_ids": [],
        "error": None
    }

    # Step 1: set PO statuses
    filter_res = set_order_status_filters_po(driver, timeouts)
    if not filter_res["success"]:
        result["error"] = f"set_order_status_filters_po failed: {filter_res['error']}"
        return result
    time.sleep(3)  # let the filter apply

    # Step 2: Build report
    build_res = build_report(driver, timeouts)
    if not build_res["success"]:
        result["error"] = f"build_report failed: {build_res['error']}"
        return result
    time.sleep(5)  # let results load

    # Step 3: Get the first three orders
    # Note: This function now handles refreshing and re-applying filters if needed
    get_orders_res = get_first_three_orders(driver, timeouts)
    if not get_orders_res["success"]:
        result["error"] = f"get_first_three_orders failed: {get_orders_res['error']}"
        return result

    order_ids = get_orders_res.get("order_ids", [])
    logger.info(f"Found order IDs: {order_ids}")

    result["order_ids"] = order_ids
    result["success"] = True
    return result