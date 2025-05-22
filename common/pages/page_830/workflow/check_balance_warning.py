"""
Workflow for checking the warning about a non-zero company balance.
"""
import logging
import time

from common.pages.page_830.actions.verify_sales_buying_values import verify_sales_buying_values
from common.pages.page_830.actions.click_company_status import click_company_status
from common.pages.page_830.actions.verify_balance_warning import verify_balance_warning

def check_balance_warning(driver, timeouts=None):
    """
    Performs a check for a warning about a non-zero company balance.

    Steps:
    1. Checks the company balance (zero or not)
    2. If the balance is non-zero, clicks the edit status button
    3. Checks for the presence of a warning about a non-zero balance

    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations

    Returns:
        dict: Check result {'success': True/False, 'error': None/str, 'step': str, ...}
    """
    logger = logging.getLogger('test')
    print("Starting check for non-zero balance warning")

    timeouts = timeouts or {}

    try:
        # Step 1: Check the company balance
        print("Step 1: Checking company balance")
        balance_result = verify_sales_buying_values(driver, timeouts)

        if not balance_result["success"]:
            return {
                "success": False,
                "error": f"Failed to check balance: {balance_result['error']}",
                "step": "verify_balance"
            }

        # Check if the company has a non-zero balance
        has_non_zero_balance = balance_result.get("has_non_zero_balance", False)
        sales_float = balance_result.get("sales_float", 0)
        buying_float = balance_result.get("buying_float", 0)

        print(f"Balance values: Sales={sales_float}, Buying={buying_float}")
        print(f"Non-zero balance: {has_non_zero_balance}")

        if not has_non_zero_balance:
            return {
                "success": False,
                "error": "Both values (Sales and Buying) are zero. A company with a non-zero balance is required.",
                "step": "check_non_zero_balance",
                "balance_result": balance_result
            }

        print(f"The company has a non-zero balance: Sales={sales_float}, Buying={buying_float}")

        # Step 2: Click the edit status button
        print("Step 2: Clicking the edit status button")
        click_result = click_company_status(driver, timeouts)

        if not click_result["success"]:
            return {
                "success": False,
                "error": f"Failed to click the edit button: {click_result['error']}",
                "step": "click_edit_button"
            }

        # Step 3: Check for the presence of a balance warning
        print("Step 3: Checking for the presence of a balance warning")
        warning_result = verify_balance_warning(driver, timeouts)

        if warning_result["success"]:
            print("Balance warning check passed successfully")
            return {
                "success": True,
                "error": None,
                "balance_result": balance_result,
                "warning_text": warning_result.get("warning_text", "")
            }
        else:
            print(f"Balance warning check failed: {warning_result['error']}")
            return {
                "success": False,
                "error": warning_result["error"],
                "step": "verify_warning",
                "balance_result": balance_result,
                "warning_text": warning_result.get("warning_text", "")
            }

    except Exception as e:
        error_msg = f"Unexpected error during balance warning check: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return {
            "success": False,
            "error": error_msg,
            "step": "unexpected_error"
        }