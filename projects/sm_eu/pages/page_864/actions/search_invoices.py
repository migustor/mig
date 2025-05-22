"""
Action to search for invoices that have Net: € in the CN Amount column
and return IDs for both PO Company and PO PA documents.
"""

import logging
import time
import re
from urllib.parse import parse_qs, urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.utils.error_handling import jenkins_aware
from projects.sm_eu.pages.page_864.page_info import get_page_864_main_url

@jenkins_aware()
def search_invoices(driver, project_name):
    """
    Search page 864 for rows that satisfy:
      * column #1 contains “Acc PO Type: Company” or “Acc PO Type: PA”
      * column #8 (CN Amount) contains “Net: €”

    Returns a dict with `company_document_id` and `pa_document_id`
    plus boolean `success` which is True only if **both** IDs are found.
    """
    logger = logging.getLogger(' - SEARCH INVOICES - ')
    logger.info(f"Starting search for PO invoices with Net amount in {project_name}")

    # Navigate to the page
    page_url = get_page_864_main_url(project_name)
    if not page_url:
        return {"success": False, "error": f"Failed to generate URL for {project_name}"}

    driver.get(page_url)
    logger.info(f"Navigated to {page_url}")

    try:
        # ----- 1. Activate only “Paid” status filter -----
        try:
            # Find the label text first – this is more robust than value='212'
            paid_checkbox = None
            all_checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input[name="statuses"]')
            for cb in all_checkboxes:
                label = driver.execute_script(
                    "return arguments[0].nextElementSibling ? arguments[0].nextElementSibling.textContent.trim() : ''",
                    cb
                )
                if label.lower() == "paid":
                    paid_checkbox = cb
                    break

            if paid_checkbox:
                for cb in all_checkboxes:
                    cb.click() if cb.is_selected() else None  # uncheck all
                paid_checkbox.click()
                logger.info("Successfully set 'Paid' status filter")
            else:
                logger.warning("Could not find the 'Paid' checkbox; using JS fallback")
                driver.execute_script("""
                    const cbs = document.querySelectorAll('input[name="statuses"]');
                    cbs.forEach(cb => cb.checked = cb.value === '212');
                """)
        except Exception as e:
            logger.warning(f"Status filter tweak failed: {e}")

        # ----- 2. Submit the filter form -----
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"))
        )
        submit_button.click()
        logger.info("Clicked submit button to start search")

        # ----- 3. Wait for the result table -----
        table = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "table_zebra"))
        )
        logger.info("Results table has loaded")
        time.sleep(2)  # let rendering finish

        rows = table.find_elements(By.TAG_NAME, "tr")
        logger.info(f"Found {len(rows)} total rows in table")

        company_document_id = None
        pa_document_id      = None

        # Helper to extract id parameter from a link
        def extract_id_from_url(url: str):
            if not url:
                return None
            try:
                parsed = urlparse(url)
                qs = parse_qs(parsed.query)
                if qs.get("id"):
                    return qs["id"][0]
                match = re.search(r"[?&]id=(\d+)", url)
                return match.group(1) if match else None
            except Exception as err:
                logger.debug(f"URL parse error for {url}: {err}")
                return None

        # ----- 4. Iterate over table rows -----
        for idx, row in enumerate(rows, start=1):
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 8:  # skip header or malformed rows
                continue

            row_type = cells[0].text.strip().lower()
            is_company = "acc po type: company" in row_type
            is_pa      = "acc po type: pa"      in row_type
            if not (is_company or is_pa):
                continue

            cn_amount_text = cells[7].text
            if "net: €" not in cn_amount_text.lower():
                continue

            # Invoice # link is column #5 (index 4)
            links = cells[4].find_elements(By.TAG_NAME, "a")
            if not links:
                continue
            doc_id = extract_id_from_url(links[0].get_attribute("href"))
            if not doc_id:
                continue

            logger.info(f"Row {idx}: type={'Company' if is_company else 'PA'}, id={doc_id}")

            if is_company and not company_document_id:
                company_document_id = doc_id
            if is_pa and not pa_document_id:
                pa_document_id = doc_id

            if company_document_id and pa_document_id:
                break

        success = company_document_id is not None and pa_document_id is not None
        logger.info("=== SEARCH RESULTS ===")
        logger.info(f"Company document: {company_document_id}")
        logger.info(f"PA document: {pa_document_id}")

        return {
            "success": success,
            "company_document_id": company_document_id,
            "pa_document_id": pa_document_id,
            "message": "Both IDs found" if success else "One or both IDs were not found"
        }

    except Exception as e:
        logger.error(f"Error during search: {e}")
        return {"success": False, "error": str(e)}
