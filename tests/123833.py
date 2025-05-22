import logging
import time
import importlib
import sys

from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_lead_presale")

# List of projects
PROJECTS = [
    {"project_code": "sm_eu", "company_id": 802375},
    {"project_code": "sm_us", "company_id": 610072},
    {"project_code": "ra_eu", "company_id": 369754},
    {"project_code": "ag_eu", "company_id": 112102},
    {"project_code": "lt_eu", "company_id": 36772},
    {"project_code": "dr_eu", "company_id": 4564},
    {"project_code": "ho_eu", "company_id": 52276},
    {"project_code": "aro_eu", "company_id": 175278},
    {"project_code": "argon",  "company_id": 1013},
]

# Helper: try to import from primary path (for et_eu) and fallback to secondary path.
def import_with_fallback(primary_module, secondary_module, func_name):
    try:
        mod = importlib.import_module(primary_module)
        return getattr(mod, func_name)
    except ImportError:
        mod = importlib.import_module(secondary_module)
        return getattr(mod, func_name)

# For create_lead_621 and close_lead_621:
def import_create_lead_621(project_code):
    # For et_eu, try primary from projects, else fallback to common.
    if project_code == "et_eu":
        primary = "projects.et_eu.pages.page_621.actions.create_lead_621"
        secondary = "common.pages.page_621.actions.create_lead_621"
        return import_with_fallback(primary, secondary, "create_lead_621")
    else:
        # For all other projects use common
        from common.pages.page_621.actions.create_lead_621 import create_lead_621
        return create_lead_621

def import_close_lead_621(project_code):
    if project_code == "et_eu":
        primary = "projects.et_eu.pages.page_621.actions.close_lead_621"
        secondary = "common.pages.page_621.actions.close_lead_621"
        return import_with_fallback(primary, secondary, "close_lead_621")
    else:
        from common.pages.page_621.actions.close_lead_621 import close_lead_621
        return close_lead_621

# For page_972 actions – for et_eu we use projects.et_eu, for others common.
def import_create_presale(project_code):
    if project_code == "et_eu":
        primary = "projects.et_eu.pages.page_972.actions.create_presale"
        secondary = "common.pages.page_972.actions.create_presale"
        return import_with_fallback(primary, secondary, "create_presale")
    else:
        from common.pages.page_972.actions.create_presale import create_presale
        return create_presale

def import_search_yes(project_code):
    if project_code == "et_eu":
        primary = "projects.et_eu.pages.page_972.actions.search_yes"
        secondary = "common.pages.page_972.actions.search_yes"
        return import_with_fallback(primary, secondary, "search_yes")
    else:
        from common.pages.page_972.actions.search_yes import search_yes
        return search_yes

def import_search_no(project_code):
    if project_code == "et_eu":
        primary = "projects.et_eu.pages.page_972.actions.search_no"
        secondary = "common.pages.page_972.actions.search_no"
        return import_with_fallback(primary, secondary, "search_no")
    else:
        from common.pages.page_972.actions.search_no import search_no
        return search_no

def import_search_both(project_code):
    if project_code == "et_eu":
        primary = "projects.et_eu.pages.page_972.actions.search_both"
        secondary = "common.pages.page_972.actions.search_both"
        return import_with_fallback(primary, secondary, "search_both")
    else:
        from common.pages.page_972.actions.search_both import search_both
        return search_both

def import_close_presale(project_code):
    if project_code == "et_eu":
        primary = "projects.et_eu.pages.page_972.actions.close_presale"
        secondary = "common.pages.page_972.actions.close_presale"
        return import_with_fallback(primary, secondary, "close_presale")
    else:
        from common.pages.page_972.actions.close_presale import close_presale
        return close_presale

# Timeouts dict (can be adjusted)
TIMEOUTS = {"login": 20, "action": 15, "company": 25, "navigation": 25, "page_load": 30}

def run_test_for_project(driver, project_code, company_id):
    errors = []
    logger.info(f"--- Starting test for project {project_code} with company ID {company_id} ---")
    
    # Step 1: Create lead (page 621)
    try:
        create_lead = import_create_lead_621(project_code)
        result_lead = create_lead(driver, project_code, company_id, timeouts=TIMEOUTS)
        if not result_lead.get("success", False):
            err = f"[create_lead_621] {result_lead.get('error', 'Unknown error')}"
            errors.append(err)
            logger.error(err)
            return {"success": False, "errors": errors}
        lead_id = result_lead.get("lead_id")
        logger.info(f"Lead created with ID: {lead_id}")
    except Exception as e:
        err = f"[create_lead_621 - EXCEPTION] {str(e)}"
        errors.append(err)
        logger.exception("Exception in create_lead_621")
        return {"success": False, "errors": errors}
    
    # Step 2: Create presale (page 972)
    try:
        create_presale = import_create_presale(project_code)
        result_presale = create_presale(driver, project_code, lead_id, timeouts=TIMEOUTS)
        if not result_presale.get("success", False):
            err = f"[create_presale] {result_presale.get('error', 'Unknown error')}"
            errors.append(err)
            logger.error(err)
            return {"success": False, "errors": errors}
        presale_id = result_presale.get("presale_id")
        logger.info(f"Presale created with ID: {presale_id}")
    except Exception as e:
        err = f"[create_presale - EXCEPTION] {str(e)}"
        errors.append(err)
        logger.exception("Exception in create_presale")
        return {"success": False, "errors": errors}
    
    # Step 3: Search Yes (page 972)
    try:
        search_yes = import_search_yes(project_code)
        result_search_yes = search_yes(driver, project_code, presale_id, timeouts=TIMEOUTS)
        if not result_search_yes.get("success", False) or not result_search_yes.get("found", False):
            err = f"[search_yes] {result_search_yes.get('error', 'Presale not found')}"
            errors.append(err)
            logger.error(err)
            return {"success": False, "errors": errors}
        logger.info("Search YES successful.")
    except Exception as e:
        err = f"[search_yes - EXCEPTION] {str(e)}"
        errors.append(err)
        logger.exception("Exception in search_yes")
        return {"success": False, "errors": errors}
    
    # Step 4: Search No (page 972)
    try:
        search_no = import_search_no(project_code)
        result_search_no = search_no(driver, project_code, presale_id, timeouts=TIMEOUTS)
        if not result_search_no.get("success", False) or result_search_no.get("found", True):
            err = f"[search_no] {result_search_no.get('error', 'Presale unexpectedly found')}"
            errors.append(err)
            logger.error(err)
            return {"success": False, "errors": errors}
        logger.info("Search NO successful.")
    except Exception as e:
        err = f"[search_no - EXCEPTION] {str(e)}"
        errors.append(err)
        logger.exception("Exception in search_no")
        return {"success": False, "errors": errors}
    
    # Step 5: Search Both (page 972)
    try:
        search_both = import_search_both(project_code)
        result_search_both = search_both(driver, project_code, presale_id, timeouts=TIMEOUTS)
        if not result_search_both.get("success", False) or not result_search_both.get("found", False):
            err = f"[search_both] {result_search_both.get('error', 'Presale not found in BOTH search')}"
            errors.append(err)
            logger.error(err)
            return {"success": False, "errors": errors}
        logger.info("Search BOTH successful.")
    except Exception as e:
        err = f"[search_both - EXCEPTION] {str(e)}"
        errors.append(err)
        logger.exception("Exception in search_both")
        return {"success": False, "errors": errors}
    
    # Step 6: Close presale (page 972)
    try:
        close_presale = import_close_presale(project_code)
        result_close_presale = close_presale(driver, project_code, presale_id, timeouts=TIMEOUTS)
        if not result_close_presale.get("success", False):
            err = f"[close_presale] {result_close_presale.get('error', 'Unknown error')}"
            errors.append(err)
            logger.error(err)
            return {"success": False, "errors": errors}
        logger.info("Presale closed successfully.")
    except Exception as e:
        err = f"[close_presale - EXCEPTION] {str(e)}"
        errors.append(err)
        logger.exception("Exception in close_presale")
        return {"success": False, "errors": errors}
    
    # Step 7: Close lead (page 621)
    try:
        close_lead = import_close_lead_621(project_code)
        lead_id_int = int(lead_id)
        # Pass company_id from function parameter
        result_close_lead = close_lead(driver, project_code, lead_id_int, company_id=company_id, timeouts=TIMEOUTS)
        if not result_close_lead.get("success", False):
            err = f"[close_lead_621] {result_close_lead.get('error', 'Unknown error')}"
            errors.append(err)
            logger.error(err)
            return {"success": False, "errors": errors}
        logger.info("Lead closed successfully.")
    except Exception as e:
        err = f"[close_lead_621 - EXCEPTION] {str(e)}"
        errors.append(err)
        logger.exception("Exception in close_lead_621")
        return {"success": False, "errors": errors}
    
    # All steps succeeded
    logger.info(f"All steps completed successfully for project {project_code}.")
    return {"success": True, "errors": []}

def main():
    driver = setup_chrome_driver(headless=False)
    overall_errors = []
    
    try:
        for proj in PROJECTS:
            pcode = proj["project_code"]
            cid = proj["company_id"]
            logger.info(f"--- Processing project {pcode} ---")
            
            # Step 0: Login as vb
            login_result = login_as_user(driver, pcode, "vb", timeouts=TIMEOUTS)
            if not login_result.get("success", False):
                err = f"[LOGIN] {pcode}: {login_result.get('error', 'Unknown login error')}"
                overall_errors.append(err)
                logger.error(err)
                # Logout and move to next project
                logout_from_system(driver, pcode)
                time.sleep(2)
                continue
            
            # Run the 7-step test
            result = run_test_for_project(driver, pcode, cid)
            if not result.get("success", False):
                for e in result.get("errors", []):
                    overall_errors.append(f"{pcode}: {e}")
            # Logout for the project
            logout_from_system(driver, pcode)
            time.sleep(2)
    finally:
        release_driver(driver, quit=True)
    
    # Final summary
    if overall_errors:
        logger.info("==== TEST COMPLETED WITH ERRORS ====")
        for err in overall_errors:
            logger.info(f" - {err}")
        sys.exit(1)  # This signals Jenkins to treat build as failed
    else:
        logger.info("==== ALL PROJECTS PASSED SUCCESSFULLY ====")

if __name__ == "__main__":
    main()
