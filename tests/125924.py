import logging
import sys

from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system
from common.utils.error_handling import jenkins_aware

from projects.sm_eu.pages.page_864.actions.search_invoices import search_invoices
from projects.sm_eu.pages.page_864.actions.po_type_company import po_type_company
from projects.sm_eu.pages.page_864.actions.po_type_pa import po_type_pa

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(" - MAIN TEST - ")


@jenkins_aware()
def test_po_vat_behavior(driver, project_name):
    logger.info(f"=== PO VAT behaviour test for {project_name} ===")

    # 1. Login
    res_login = login_as_user(driver, project_name, "vb")
    if not res_login["success"]:
        return {"success": False, "error": res_login["error"], "step": "login"}

    # 2. Search for document IDs
    res_search = search_invoices(driver, project_name)
    if not res_search["success"]:
        logout_from_system(driver, project_name)
        return {"success": False, "error": res_search["error"], "step": "search_invoices"}

    company_id = res_search.get("company_document_id")
    pa_id = res_search.get("pa_document_id")
    if not company_id or not pa_id:
        logout_from_system(driver, project_name)
        return {
            "success": False,
            "error": "Both Company and PA documents are required",
            "step": "search_invoices",
        }
    logger.info(f"Company ID={company_id}, PA ID={pa_id}")

    # 3. COMPANY first (popup expected)
    res_company = po_type_company(driver, project_name, company_id)
    if not res_company["success"]:
        logout_from_system(driver, project_name)
        return {
            "success": False,
            "error": res_company["error"],
            "step": "modify_company_vat",
        }
    if not res_company.get("popup_appeared", False):
        logout_from_system(driver, project_name)
        return {
            "success": False,
            "error": "Popup did not appear for Company document",
            "step": "verify_company_popup",
        }

    # 4. PA second (popup NOT expected)
    res_pa = po_type_pa(driver, project_name, pa_id)
    if not res_pa["success"]:
        logout_from_system(driver, project_name)
        return {
            "success": False,
            "error": res_pa["error"],
            "step": "modify_pa_vat",
        }
    if res_pa.get("popup_appeared", False):
        logout_from_system(driver, project_name)
        return {
            "success": False,
            "error": "Unexpected popup for PA document",
            "step": "verify_pa_popup",
        }

    # 5. Logout
    logout_from_system(driver, project_name)

    return {
        "success": True,
        "message": "Test completed",
        "company_document_id": company_id,
        "pa_document_id": pa_id,
        "company_popup": "with popup",
        "pa_popup": "without popup",
    }


def main():
    driver = None
    try:
        driver = setup_chrome_driver(headless=False)
        result = test_po_vat_behavior(driver, "sm_eu")

        logger.info("=== SUMMARY ===")
        if result["success"]:
            logger.info("PO Company → VAT change with popup")
            logger.info("PO PA      → VAT change without popup")
            return 0
        else:
            logger.error(f"{result['error']} (step: {result.get('step')})")
            return 1
    finally:
        if driver:
            release_driver(driver)


if __name__ == "__main__":
    sys.exit(main())
