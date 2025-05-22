import logging
import random
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Project configuration
PROJECT_CONFIG = {
    "SM EU": {
        "po_url": "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=839&po_id=228592",
        "order_url": "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=888&sales_order_id=605195&phase=edit",
        "grafit_url": "https://stage15.office.grafit.md",
        "project_id": "sm_eu"
    },
    "RA": {
        "po_url": "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=839&po_id=44601",
        "order_url": "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=888&sales_order_id=100589&phase=edit",
        "grafit_url": "https://stage15.office.grafit.md",
        "project_id": "ra_eu"
    },
    "AGAVA": {
        "po_url": "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=839&po_id=4502",
        "order_url": "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=888&sales_order_id=50229&phase=edit",
        "grafit_url": "https://stage15.office.grafit.md",
        "project_id": "ag_eu"
    },
    "EMINIA": {
        "po_url": "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=839&po_id=132729",
        "order_url": "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=888&sales_order_id=276001&phase=edit",
        "grafit_url": "https://stage15.office.grafit.md",
        "project_id": "et_eu"
    },
    "LANIUS": {
        "po_url": "https://stage15.office.laniustoys.com/sage/index.cfm?page_id=839&po_id=41644",
        "order_url": "https://stage15.office.laniustoys.com/sage/index.cfm?page_id=888&sales_order_id=87976&phase=edit",
        "grafit_url": "https://stage15.office.grafit.md",
        "project_id": "lt_eu"
    },
    "DB": {
        "po_url": "https://stage15.office.dbreactor.com/sage/index.cfm?page_id=839&po_id=622",
        "order_url": "https://stage15.office.dbreactor.com/sage/index.cfm?page_id=888&sales_order_id=1075&phase=edit",
        "grafit_url": "https://stage15.office.grafit.md",
        "project_id": "dr_eu"
    },
    "HORUS": {
        "po_url": "https://stage15.office.horustrading.eu/sage/index.cfm?page_id=839&po_id=748",
        "order_url": "https://stage15.office.horustrading.eu/sage/index.cfm?page_id=888&sales_order_id=818&phase=edit",
        "grafit_url": "https://stage15.office.grafit.md",
        "project_id": "ho_eu"
    },
    "ATLAS": {
        "po_url": "https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=839&po_id=302",
        "order_url": "https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=888&sales_order_id=470&phase=edit",
        "grafit_url": "https://stage15.office.grafit.md",
        "project_id": "at_eu"
    },
    "ARO": {
        "po_url": "https://stage15.office.arotrading.eu/sage/index.cfm?page_id=839&po_id=17",
        "order_url": "https://stage15.office.arotrading.eu/sage/index.cfm?page_id=888&sales_order_id=37&phase=edit",
        "grafit_url": "https://stage15.office.grafit.md",
        "project_id": "aro_eu"
    },
    "ARGON": {
        "po_url": "https://stage15.office.argontrading.de/sage/index.cfm?page_id=839&po_id=17",
        "order_url": "https://stage15.office.argontrading.de/sage/index.cfm?page_id=888&sales_order_id=49&phase=edit",
        "grafit_url": "https://stage15.office.grafit.md",
        "project_id": "argon"
    }
}

def generate_random_zip_code(prefix="BT"):
    """Generate a random UK-style postal code with the given prefix."""
    return f"{prefix}{random.randint(1, 9)} {random.randint(100, 999)}"

def get_order_id_from_url(url):
    """Extract order ID from URL."""
    parsed_url = parse_qs(urlparse(url).query)
    return (
        parsed_url.get('po_id', [None])[0],
        parsed_url.get('sales_order_id', [None])[0]
    )

def generate_grafit_url(project_config, url):
    """Generate Grafit URL based on project configuration and source URL."""
    po_id, so_id = get_order_id_from_url(url)
    order_type = 'po' if po_id else 'so'
    order_id = po_id if po_id else so_id
    return (f"{project_config['grafit_url']}/sage/index.cfm"
            f"?page_id=907&{order_type}_id={order_id}"
            f"&project_id={project_config['project_id']}&order_type={order_type}")

def perform_login(driver, username, password):
    """Perform login on the current page."""
    try:
        login_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'login_name')))
        login_name.send_keys(username)
        driver.find_element(By.ID, 'password').send_keys(password)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        time.sleep(2)
        return True
    except Exception as e:
        logging.error(f'Login failed: {str(e)}')
        return False

def verify_postal_code_color(driver, prefix, url_type="order_url"):
    """Verify the postal code color in the shipping/pickup info section."""
    try:
        time.sleep(2)

        if url_type == "order_url":
            info_section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.shipping_info'))
            )
            postal_span = info_section.find_element(By.CSS_SELECTOR, 'p.xpb0.xpt0 span')
        else:
            pickup_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#pickup_address_data'))
            )
            paragraphs = pickup_div.find_elements(By.CSS_SELECTOR, 'p.xpb0.xpt0')
            if len(paragraphs) >= 2:
                second_p = paragraphs[1]
                postal_spans = second_p.find_elements(By.CSS_SELECTOR, 'span')
                if postal_spans:
                    postal_span = postal_spans[0]
                else:
                    raise Exception("Postal code span not found")
            else:
                raise Exception("Required paragraphs not found")

        postal_code = postal_span.text.strip()
        has_red_class = "red-custom-rules" in (postal_span.get_attribute("class") or "")
        expected_red = prefix != "BT"
        is_valid = has_red_class == expected_red

        logging.info(f'Found postal code: {postal_code}')
        return is_valid, postal_code

    except Exception as e:
        logging.error(f'Error in postal code verification: {str(e)}')
        return False, None

def verify_postal_code_color_grafit_so(driver, project_id, sales_order_id, original_postal_code):
    """Verify customs rules message on Grafit page for Sales Orders"""
    try:
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(3)

        container_selector = f'#logistics_request_for_so_id_{project_id}_{sales_order_id}'
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
        )

        non_eu_rule = container.find_elements(
            By.CSS_SELECTOR,
            '.red-custom-rules[data-message="Non-EU zone - Customs rules apply"]'
        )
        has_non_eu_rule = len(non_eu_rule) > 0

        is_bt = original_postal_code.startswith('BT')
        is_valid = has_non_eu_rule != is_bt
        return is_valid

    except Exception as e:
        logging.error(f'Error in SO Grafit verification: {str(e)}')
        return False

def verify_postal_code_color_grafit_po(driver, project_id, po_id, original_postal_code):
    """Verify customs rules message on Grafit page for Purchase Orders"""
    try:
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(3)

        container_selector = f'#logistics_request_for_po_id_{project_id}_{po_id}'
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
        )

        non_eu_rule = container.find_elements(
            By.CSS_SELECTOR,
            '.red-custom-rules[data-message="Non-EU zone - Customs rules apply"]'
        )
        has_non_eu_rule = len(non_eu_rule) > 0

        is_bt = original_postal_code.startswith('BT')
        is_valid = has_non_eu_rule != is_bt
        return is_valid

    except Exception as e:
        logging.error(f'Error in PO Grafit verification: {str(e)}')
        return False

def test_postal_code(driver, prefix, url_type="order_url"):
    """Test postal code color for given prefix"""
    try:
        if url_type == "order_url":
            address_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-secondary.mng_shipping_address.address_editor'))
            )
        else:
            address_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn.pull-right.address_editor[data-select-class="select_pickup_addr"]'))
            )
        address_btn.click()
        time.sleep(1)

        first_edit = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.edit-name[data-address-id]'))
        )[0]
        first_edit.click()
        time.sleep(1)

        country_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'country_id'))
        )
        if driver.execute_script("return arguments[0].value;", country_dropdown) != '224':
            driver.execute_script("""
                arguments[0].value = '224';
                arguments[0].dispatchEvent(new Event('change'));
            """, country_dropdown)

        new_postal_code = generate_random_zip_code(prefix)
        postal_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'postal_code')))
        postal_input.clear()
        postal_input.send_keys(new_postal_code)
        time.sleep(1)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-primary.address_manager_btn[data-address-event="save"]'))
        ).click()
        time.sleep(2)

        if url_type == "order_url":
            address_select = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button.btn-success.select_shipping'))
            )[0]
        else:
            address_select = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button.btn.btn-success.select_pickup_addr'))
            )[0]
        address_select.click()
        time.sleep(2)

        return verify_postal_code_color(driver, prefix, url_type)

    except Exception as e:
        logging.error(f'Error in test execution: {str(e)}')
        return False, None

def test_postal_code_workflow(driver, project_id, prefix, url_type, grafit_credentials):
    """Complete test workflow for a postal code"""
    results = {"original": False, "grafit": False}
    order_window = driver.current_window_handle

    try:
        original_result, postal_code = test_postal_code(driver, prefix, url_type)
        results["original"] = original_result

        if original_result and postal_code:
            if url_type == "po_url":
                current_url = driver.current_url
                po_id, _ = get_order_id_from_url(current_url)
                grafit_url = generate_grafit_url(PROJECT_CONFIG[project_id], current_url)
                before_handles = set(driver.window_handles)
                driver.execute_script(f'window.open("{grafit_url}", "_blank");')
            else:
                surplus_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#surplus_order_btn'))
                )
                surplus_btn.click()
                time.sleep(5)

                current_url = driver.current_url
                _, so_id = get_order_id_from_url(current_url)
                before_handles = set(driver.window_handles)
                grafit_url = generate_grafit_url(PROJECT_CONFIG[project_id], current_url)
                driver.execute_script(f'window.open("{grafit_url}", "_blank");')

            time.sleep(2)

            new_handle = list(set(driver.window_handles) - before_handles)[0]
            driver.switch_to.window(new_handle)

            try:
                login_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, 'login_name'))
                )
                perform_login(driver, grafit_credentials["username"], grafit_credentials["password"])
            except:
                pass

            po_id, so_id = get_order_id_from_url(current_url)

            if url_type == "po_url" and po_id:
                results["grafit"] = verify_postal_code_color_grafit_po(
                    driver,
                    PROJECT_CONFIG[project_id]["project_id"].upper(),
                    po_id,
                    postal_code
                )
            elif url_type == "order_url" and so_id:
                results["grafit"] = verify_postal_code_color_grafit_so(
                    driver,
                    PROJECT_CONFIG[project_id]["project_id"].upper(),
                    so_id,
                    postal_code
                )

            driver.close()
            driver.switch_to.window(order_window)
            driver.refresh()
            time.sleep(2)

    except Exception as e:
        logging.error(f'Error in workflow: {str(e)}')
        try:
            if len(driver.window_handles) > 1:
                driver.close()
            driver.switch_to.window(order_window)
        except:
            pass

    return results

def main():
    driver = None
    overall_test_results = {}
    error_found = False
    grafit_credentials = {
        "username": "valeriu.bistritchi@mteam.md",
        "password": "12"
    }

    try:
        logging.info('Starting test execution')
        driver = webdriver.Chrome()
        driver.maximize_window()

        for project_id, config in PROJECT_CONFIG.items():
            test_results = {}
            logged_in_domains = set()

            for url_type in ["order_url", "po_url"]:
                try:
                    logging.info(f'\n=== Testing project: {project_id} - {url_type} ===')
                    current_url = config[url_type]
                    current_domain = urlparse(current_url).netloc
                    driver.get(current_url)

                    if current_domain not in logged_in_domains:
                        logging.info(f'Performing login for domain: {current_domain}')
                        if perform_login(driver, grafit_credentials["username"], grafit_credentials["password"]):
                            logged_in_domains.add(current_domain)
                        else:
                            continue

                    url_results = {}
                    for prefix in ['BT', 'OR']:
                        logging.info(f'\n=== Testing {prefix} postal code on {url_type} page ===')
                        results = test_postal_code_workflow(
                            driver=driver,
                            project_id=project_id,
                            prefix=prefix,
                            url_type=url_type,
                            grafit_credentials=grafit_credentials
                        )

                        url_results[prefix] = {
                            "original": "SUCCESS" if results.get("original") else "FAILED",
                            "grafit": "SUCCESS" if results.get("grafit") else "FAILED"
                        }

                    test_results[url_type] = url_results

                except Exception as e:
                    logging.error(f'Error processing {url_type}: {str(e)}')
                    test_results[url_type] = "ERROR"

            overall_test_results[project_id] = test_results

    except Exception as e:
        logging.error(f'Global test execution error: {str(e)}')

    finally:
        if driver:
            driver.quit()

        print("\n=== OVERALL TEST SUMMARY ===")
        for project_id, results in overall_test_results.items():
            print(f"\n=== TEST SUMMARY ({project_id}) ===")

            for url_type, url_results in results.items():
                print(f"\n  {url_type}:")
                if isinstance(url_results, str):
                    print(f"    {url_results}")
                    if url_results == "ERROR":
                        error_found = True
                else:
                    for prefix, page_results in url_results.items():
                        expected_color = "BLACK" if prefix == "BT" else "RED"
                        print(f"    Prefix {prefix} ({expected_color}):")
                        print(f"      Original page: {page_results['original']}")
                        print(f"      Grafit page: {page_results['grafit']}")

        if error_found:
            logging.error("Tests completed with errors")
            sys.exit(1)
        else:
            logging.info("All tests completed successfully")

if __name__ == "__main__":
    main()
