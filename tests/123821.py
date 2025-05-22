from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import sys
import logging
from login_utils import login

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def generate_comparison_summary(results):
    """
    Generates a summary of the comparison results
    """
    summary = "\n=== COMPARISON SUMMARY ===\n"

    # Data Status Summary
    summary += "\nTable Content Status:\n"
    for table_name, content in results["tables_content"].items():
        if content["is_present"]:
            icon = "[+]" if content["content"] else "[-]"
            summary += f"{icon} {table_name}: {content['content']}\n"
        else:
            summary += f"[X] {table_name}: NOT ACCESSIBLE\n"

    # Comparison Results
    summary += "\nComparison Results:\n"
    if results["all_match"]:
        summary += "[+] All tables contain identical content\n"
    else:
        summary += "[-] Discrepancies found between tables:\n"
        for mismatch in results["mismatches"]:
            summary += f"    - {mismatch}\n"

    summary += "\n=================\n"
    return summary

def clean_content(content):
    """
    Removes Country Of Origin line from content and returns cleaned text
    """
    if not content:
        return None
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    cleaned_lines = [line for line in lines if not line.startswith('Country Of Origin:')]
    return '\n'.join(cleaned_lines)

def compare_table_contents(driver):
    """
    Compares Item Info content from three different tables, using third table as reference
    """
    try:
        results = {
            "tables_content": {},
            "all_match": False,
            "mismatches": []
        }

        # Wait and get content from third table (reference)
        third_table = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#sales_order_list_items tbody tr:first-child td .info_compact"))
        )
        third_content = clean_content(third_table.text.strip() if third_table else None)
        results["tables_content"]["Reference Table"] = {
            "is_present": bool(third_content),
            "content": third_content
        }

        if not third_content:
            results["mismatches"].append("Reference table content not found")
            results["all_match"] = False
            return results

        # Wait and get content from first table
        first_table = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#table tbody tr:first-child td .info_compact"))
        )
        first_content = clean_content(first_table.text.strip() if first_table else None)
        results["tables_content"]["First Table"] = {
            "is_present": bool(first_content),
            "content": first_content
        }

        # Try to get content from second table
        try:
            second_table = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#sc_items_sortable tr:first-child td .info_compact"))
            )
        except TimeoutException:
            logging.info("Second table not found initially, trying to open the panel...")
            try:
                # Attempt to find and click panel header
                panel_header = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#list_of_shopping_cart_items > h4"))
                )

                logging.info("Found panel header, attempting to click...")
                try:
                    panel_header.click()
                except:
                    driver.execute_script("arguments[0].click();", panel_header)
                logging.info("Successfully clicked on panel header")

                # Wait for panel to open
                time.sleep(2)

                # Try to get the table content again
                second_table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#sc_items_sortable tr:first-child td .info_compact"))
                )
            except Exception as e:
                logging.error(f"Failed to access second table even after clicking panel: {str(e)}")
                second_table = None

        second_content = clean_content(second_table.text.strip() if second_table else None)
        results["tables_content"]["Second Table"] = {
            "is_present": bool(second_content),
            "content": second_content
        }

        # Compare with reference content
        results["all_match"] = True
        if first_content != third_content:
            results["all_match"] = False
            results["mismatches"].append("First Table content differs from Reference Table")

        if second_content != third_content:
            results["all_match"] = False
            results["mismatches"].append("Second Table content differs from Reference Table")

        return results

    except Exception as e:
        logging.error(f"Error during comparison: {str(e)}")
        return None

def automate_sales_order(driver, target_url):
    """
    Automates the sales order process on the trading platform
    """
    try:
        # Navigate to the specific sales order page
        driver.get(target_url)
        logging.info(f"Navigating to {target_url}")

        # First, find and extract the part number
        part_number_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#sales_order_list_items tbody tr:first-child td.part_number span.d-block.nobreak:first-child"))
        )
        part_number = part_number_element.text.strip()
        # Remove comma if present at the end
        part_number = part_number.rstrip(',')
        logging.info(f"Found part number: {part_number}")

        # Wait for and click the "Add More Items" panel
        add_items_panel = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "item_search_form"))
        )
        add_items_panel.click()

        # Wait for and click the "Shopping Cart Items" tab
        shopping_cart_tab = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#shopping_cart']"))
        )
        shopping_cart_tab.click()

        # Wait for tab content to load
        time.sleep(2)

        # Wait for and find the textarea using full CSS selector
        textarea = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#shopping_cart > div.col-md-6 > div.form-group > div.col-md-8 > textarea.multi_item_part_number.form-control"))
        )

        # Clear any existing text and input the description
        textarea.clear()
        textarea.send_keys(part_number)

        # Find and click the search button
        search_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "html_shopping_cart_button"))
        )
        search_button.click()

        # Wait for results
        time.sleep(5)

        # Check panel state before clicking
        try:
            panel = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#list_of_shopping_cart_items"))
            )
            # Check icon state (open/closed)
            icon = panel.find_element(By.CSS_SELECTOR, "i.glyphicon-chevron-up")
            is_open = "open" in icon.get_attribute("class")

            # Check content visibility
            content_visible = driver.find_element(By.ID, "list_of_shopping_cart_result").is_displayed()

            logging.info(f"Panel state - Icon open: {is_open}, Content visible: {content_visible}")

            # Click only if panel is closed
            if not (is_open and content_visible):
                logging.info("Panel is closed, clicking to open...")
                panel_header = panel.find_element(By.TAG_NAME, "h4")
                driver.execute_script("arguments[0].click();", panel_header)
                logging.info("Clicked on shopping cart panel")
                time.sleep(3)
            else:
                logging.info("Panel is already open, skipping click")

        except Exception as e:
            logging.error(f"Error checking panel state: {str(e)}")

        # Compare contents
        comparison_results = compare_table_contents(driver)

        if comparison_results:
            summary = generate_comparison_summary(comparison_results)
            logging.info(summary)

            if not comparison_results["all_match"]:
                logging.error("Content mismatch detected")
                sys.exit(1)
        else:
            logging.error("Failed to compare table contents")
            sys.exit(1)

    except TimeoutException as e:
        logging.error(f"Timeout occurred: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)

def generate_final_summary(test_results):
    """
    Generates a final summary of all test results
    """
    summary = "\n\n=== FINAL TEST SUMMARY ===\n"

    # Count statistics
    total_tests = len(test_results)
    successful_tests = sum(1 for result in test_results.values() if result["status"] == "SUCCESS")
    failed_tests = sum(1 for result in test_results.values() if result["status"] == "FAILED")
    login_failed = sum(1 for result in test_results.values() if result["status"] == "LOGIN_FAILED")

    summary += f"\nTotal Projects Tested: {total_tests}"
    summary += f"\nSuccessful Tests: {successful_tests}"
    summary += f"\nFailed Tests: {failed_tests}"
    summary += f"\nLogin Failures: {login_failed}\n"

    summary += "\nDetailed Results:"
    for project, result in test_results.items():
        status_icon = {
            "SUCCESS": "✓",
            "FAILED": "✗",
            "LOGIN_FAILED": "!"
        }.get(result["status"], "?")

        summary += f"\n{status_icon} {project.upper()}: {result['status']}"
        if result.get("error"):
            summary += f" - {result['error']}"

    summary += "\n\n========================="
    return summary

def main():
    # Dictionary of projects to test with their respective URLs
    test_cases = {
        "horus": "https://stage15.office.horustrading.eu/sage/index.cfm?page_id=888&phase=edit&sales_order_id=772",
        "sm_eu": "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=888&phase=edit&sales_order_id=605232",
        "ra_trading": "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=888&phase=edit&sales_order_id=100256",
        "sm_usa": "https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=888&phase=edit&sales_order_id=34242",
        "atlas_trading": "https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=888&sales_order_id=483&phase=edit",
        "aro": "https://stage15.office.arotrading.eu/sage/index.cfm?page_id=888&phase=edit&sales_order_id=38",
        "agava_trading": "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=888&phase=edit&sales_order_id=48992"
    }

    # Store test results
    test_results = {}

    # Test each project
    for project_name, target_url in test_cases.items():
        logging.info(f"\n{'='*50}")
        logging.info(f"Testing {project_name.upper()}")
        logging.info(f"{'='*50}")

        test_results[project_name] = {
            "status": "FAILED",  # Default status
            "error": None
        }

        driver = webdriver.Chrome()
        try:
            if login(driver, project_name, "ml"):
                logging.info(f"Successfully logged in to {project_name}")
                try:
                    automate_sales_order(driver, target_url)
                    test_results[project_name]["status"] = "SUCCESS"
                    logging.info(f"Successfully completed test for {project_name}")
                except Exception as e:
                    error_msg = str(e)
                    test_results[project_name].update({
                        "status": "FAILED",
                        "error": f"Automation error: {error_msg}"
                    })
                    logging.error(f"Error during {project_name} test: {error_msg}")
            else:
                test_results[project_name].update({
                    "status": "LOGIN_FAILED",
                    "error": "Failed to login"
                })
                logging.error(f"Login failed for {project_name}")
        except Exception as e:
            error_msg = str(e)
            test_results[project_name].update({
                "status": "FAILED",
                "error": f"Unexpected error: {error_msg}"
            })
            logging.error(f"Unexpected error for {project_name}: {error_msg}")
        finally:
            driver.quit()

    # Generate and print final summary
    final_summary = generate_final_summary(test_results)
    logging.info(final_summary)

    # If any tests failed (including login failures), exit with error code
    if any(result["status"] != "SUCCESS" for result in test_results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()
