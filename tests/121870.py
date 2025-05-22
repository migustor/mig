from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import logging
from typing import Dict

PROJECTS = {
    "Ra trading": {
        "login_url": "https://stage15.office.ratrading.eu/sage/",
        "first_page": "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=621&phase=edit&lead_id=31760",
        "second_page": "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=714&item_id=35644"
    },
    "Atlas Trading": {
        "login_url": "https://stage15.office.atlastradingworld.com/sage/",
        "first_page": "https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=621&phase=edit&lead_id=3470",
        "second_page": "https://stage15.office.atlastradingworld.com/sage/index.cfm?page_id=714&item_id=67526"
    },
    "Agava Trading": {
        "login_url": "https://stage15.office.agavasystem.com/sage/",
        "first_page": "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=621&phase=edit&lead_id=3470",
        "second_page": "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=714&item_id=65585"
    },
    "SM USA": {
        "login_url": "https://stage15.office.sovamaxusa.com/sage/",
        "first_page": "https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=621&phase=edit&lead_id=3473",
        "second_page": "https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=714&item_id=596"
    },
    "SM EU": {
        "login_url": "https://stage15.office.sovasystem.com/sage/",
        "first_page": "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=621&phase=edit&lead_id=208523",
        "second_page": "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=714&item_id=1426"
    }

}

def get_base_url(url: str) -> str:
    """
    Returns the correct base URL for project verification based on the project domain
    """
    base_urls = {
        "ratrading.eu": "https://stage15.office.ratrading.eu/sage/",
        "atlastradingworld.com": "https://stage15.office.atlastradingworld.com/sage/",
        "agavasystem.com": "https://stage15.office.agavasystem.com/sage/",
        "sovamaxusa.com": "https://stage15.office.sovamaxusa.com/sage/",
        "sovasystem.com": "https://stage15.office.sovasystem.com/sage/"
    }

    for domain, base_url in base_urls.items():
        if domain in url:
            return base_url

    return "https://stage15.office.ratrading.eu/sage/"

def login_to_system(driver, username, password, url):
    """
    Universal login function for the system.
    """
    logging.info(f"Logging in as {username}")
    try:
        driver.get(url)
        username_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "login_name")))
        password_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "password")))

        username_input.send_keys(username)
        password_input.send_keys(password)

        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()

        sleep(3)
        logging.info("Login successful")
        return True
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        return False

def find_and_click_generation_link(driver):
    """
    Finds and clicks the Generation link
    """
    try:
        generation_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Generation')]"))
        )
        generation_link.click()
        logging.info("Clicked Generation link")
        sleep(5)
        return True
    except Exception:
        logging.error("Element not found: 'Generation' link is not present on the page")
        return False

def get_item_id_from_table(driver):
    """
    Gets the item ID from the first row of the table with improved error handling
    """
    try:
        # First try to find the table
        try:
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered.table-striped.xvalignmiddle.xmb0"))
            )
        except Exception:
            logging.error("Unable to find the table containing item IDs")
            return None

        # Then try to find the first cell
        try:
            table_cell = table.find_element(By.CSS_SELECTOR, "td:nth-child(1)")
        except Exception:
            logging.error("Table found but unable to locate the first cell containing item ID")
            return None

        # Finally try to find and get the link text
        try:
            item_link = table_cell.find_element(By.TAG_NAME, "a")
            item_id = item_link.text.strip()
            if not item_id:
                logging.error("Found item ID link but it contains no text")
                return None
            logging.info(f"Successfully found item ID: {item_id}")
            return item_id
        except Exception:
            logging.error("Found table cell but unable to locate or read the item ID link")
            return None

    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            logging.error("Timeout: Table did not appear within 10 seconds")
        else:
            logging.error(f"Failed to read item ID from table: {error_msg}")
        return None

def verify_link_format(driver, item_id, base_url):
    """
    Verifies the link format in the table
    """
    try:
        table_cell = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered.table-striped.xvalignmiddle.xmb0 td:nth-child(1)"))
        )
        link = table_cell.find_element(By.TAG_NAME, "a")
        actual_link = link.get_attribute("href")
        expected_link = f"{base_url}index.cfm?page_id=714&item_id={item_id}"

        return actual_link == expected_link, {
            "expected": expected_link,
            "actual": actual_link
        }
    except Exception as e:
        error_msg = str(e)
        if "no such element" in error_msg.lower():
            return False, {"error": "Table cell with link is missing on the page"}
        elif "timeout" in error_msg.lower():
            return False, {"error": "Table did not appear within 10 seconds"}
        else:
            return False, {"error": f"Error verifying link format: {error_msg}"}

def verify_second_page_links(driver, second_page_url, base_url):
    """
    Verifies links on the second page with improved error handling
    """
    try:
        # Navigate to second page
        driver.get(second_page_url)
        logging.info("Navigated to second page")
        sleep(5)

        # Find info icon
        info_icon = None
        icon_selectors = {
            "i.fa.fa-info-circle.xml5[title='View Details']": "Info icon with 'View Details' title",
            "i.fa.fa-info-circle[onclick*='ViewItemLineage']": "Info icon with ViewItemLineage onclick",
            "i.fa.fa-info-circle.xml5": "Basic info icon"
        }

        for selector, description in icon_selectors.items():
            try:
                info_icon = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logging.info(f"Found info icon using selector: {description}")
                break
            except Exception:
                continue

        if info_icon is None:
            logging.error("Could not find info icon. Tried the following elements:")
            for _, desc in icon_selectors.items():
                logging.error(f"- {desc}")
            return False, {"error": "Info icon not found on page"}

        # Click info icon
        try:
            info_icon.click()
            logging.info("Successfully clicked info icon")
            sleep(3)
        except Exception as e:
            logging.error(f"Found info icon but unable to click it: {str(e)}")
            return False, {"error": "Info icon found but not clickable"}

        # Find external link
        external_link = None
        link_selectors = {
            "a.fas.fa-external-link-alt": "External link with font-awesome icon",
            "a[target='_blank']": "Link opening in new tab",
            "a.fa-external-link-alt": "Basic external link"
        }

        for selector, description in link_selectors.items():
            try:
                external_link = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logging.info(f"Found external link using selector: {description}")
                break
            except Exception:
                continue

        if external_link is None:
            logging.error("Could not find external link. Tried the following elements:")
            for _, desc in link_selectors.items():
                logging.error(f"- {desc}")
            return False, {"error": "External link not found after info icon click"}

        # Get and verify link
        actual_link = external_link.get_attribute("href")
        if not actual_link:
            logging.error("External link found but has no href attribute")
            return False, {"error": "External link has no URL"}

        # Verify link format
        if "page_id=714" not in actual_link:
            logging.error(f"Invalid link format: missing page_id=714 in {actual_link}")
            return False, {"error": "Link has incorrect page_id"}

        if "item_id=" not in actual_link:
            logging.error(f"Invalid link format: missing item_id parameter in {actual_link}")
            return False, {"error": "Link missing item_id parameter"}

        if base_url.strip('/') not in actual_link:
            logging.error(f"Invalid link format: incorrect base URL in {actual_link}")
            return False, {"error": "Link has incorrect base URL"}

        item_id = actual_link.split("item_id=")[-1].split("&")[0]
        expected_link = f"{base_url}index.cfm?page_id=714&item_id={item_id}"

        return actual_link.startswith(expected_link), {
            "expected": expected_link,
            "actual": actual_link
        }

    except Exception as e:
        error_msg = str(e)
        if "no such element" in error_msg.lower():
            logging.error("Required element not found on second page")
        elif "timeout" in error_msg.lower():
            logging.error("Page elements did not load within expected time")
        else:
            logging.error(f"Unexpected error while verifying second page: {error_msg}")
        return False, {"error": f"Second page verification failed: {error_msg}"}

def check_project(driver, project_name: str, project_urls: Dict) -> Dict:
    """
    Performs checks for a single project
    """
    project_results = {
        "authentication": {
            "success": False
        },
        "first_page": {
            "generation_link_clicked": False,
            "item_id_found": False,
            "item_id": None,
            "link_verification": {
                "success": False,
                "expected": None,
                "actual": None
            }
        },
        "second_page": {
            "info_icon_clicked": False,
            "link_verification": {
                "success": False,
                "expected": None,
                "actual": None
            }
        }
    }

    try:
        logging.info(f"\nChecking project: {project_name}")

        # Get base URL for the project
        base_url = get_base_url(project_urls["login_url"])

        # Login to system
        project_results["authentication"]["success"] = login_to_system(
            driver,
            "maxim.lupan@mteam.md",
            "12",
            project_urls["login_url"]
        )

        if project_results["authentication"]["success"]:
            # First page verification
            logging.info(f"Navigating to {project_urls['first_page']}")
            driver.get(project_urls['first_page'])
            sleep(5)

            # Click Generation link
            project_results["first_page"]["generation_link_clicked"] = find_and_click_generation_link(driver)

            # Get item ID
            item_id = get_item_id_from_table(driver)
            if item_id:
                project_results["first_page"]["item_id_found"] = True
                project_results["first_page"]["item_id"] = item_id

                # Verify first page link format using project base URL
                success, verification_data = verify_link_format(driver, item_id, base_url)
                project_results["first_page"]["link_verification"]["success"] = success
                project_results["first_page"]["link_verification"].update(verification_data)

            # Second page verification using project base URL
            success, verification_data = verify_second_page_links(driver, project_urls['second_page'], base_url)
            project_results["second_page"]["info_icon_clicked"] = True
            project_results["second_page"]["link_verification"]["success"] = success
            project_results["second_page"]["link_verification"].update(verification_data)

    except Exception as e:
        logging.error(f"Error checking project {project_name}: {str(e)}")

    return project_results

def generate_test_summary(all_results: Dict) -> str:
    """
    Generates a concise summary of all project test results
    """
    summary = "\n=== TEST SUMMARY ===\n"

    # Project Results
    for project_name, results in all_results["projects"].items():
        summary += f"\n{project_name}:\n"

        # Authentication Summary
        icon = "[+]" if results["authentication"]["success"] else "[-]"
        summary += f"{icon} Login Status: {'SUCCESS' if results['authentication']['success'] else 'FAILED'}\n"

        # First Page Verification
        summary += "First Page:\n"
        first_page = results["first_page"]
        summary += f"[{'+'  if first_page['generation_link_clicked'] else '-'}] Generation Link Click\n"
        summary += f"[{'+'  if first_page['item_id_found'] else '-'}] Item ID Found: {first_page.get('item_id', 'N/A')}\n"

        if first_page["link_verification"]["success"]:
            summary += "[+] Link Format: CORRECT\n"
            if "expected" in first_page["link_verification"]:
                summary += f"    Link: {first_page['link_verification']['actual']}\n"
        else:
            summary += "[-] Link Format: INCORRECT\n"
            if "error" in first_page["link_verification"]:
                summary += f"    Error: {first_page['link_verification']['error']}\n"
            else:
                summary += f"    Expected: {first_page['link_verification'].get('expected', 'N/A')}\n"
                summary += f"    Actual: {first_page['link_verification'].get('actual', 'N/A')}\n"

        # Second Page Verification
        summary += "Second Page:\n"
        second_page = results["second_page"]
        summary += f"[{'+'  if second_page['info_icon_clicked'] else '-'}] Info Icon Click\n"

        if second_page["link_verification"]["success"]:
            summary += "[+] Link Format: CORRECT\n"
            if "expected" in second_page["link_verification"]:
                summary += f"    Link: {second_page['link_verification']['actual']}\n"
        else:
            summary += "[-] Link Format: INCORRECT\n"
            if "error" in second_page["link_verification"]:
                summary += f"    Error: {second_page['link_verification']['error']}\n"
            else:
                summary += f"    Expected: {second_page['link_verification'].get('expected', 'N/A')}\n"
                summary += f"    Actual: {second_page['link_verification'].get('actual', 'N/A')}\n"

    # Overall Statistics
    total_projects = len(all_results["projects"])
    passed_projects = sum(
        1 for proj in all_results["projects"].values()
        if all([
            proj["authentication"]["success"],
            proj["first_page"]["generation_link_clicked"],
            proj["first_page"]["link_verification"]["success"],
            proj["second_page"]["link_verification"]["success"]
        ])
    )

    summary += f"\nFinal Results:\n"
    summary += f"Projects Passed: {passed_projects}/{total_projects}\n"
    if passed_projects == total_projects:
        summary += "ALL PROJECTS PASSED\n"
    else:
        failed_projects = [
            name for name, data in all_results["projects"].items()
            if not all([
                data["authentication"]["success"],
                data["first_page"]["generation_link_clicked"],
                data["first_page"]["link_verification"]["success"],
                data["second_page"]["link_verification"]["success"]
            ])
        ]
        summary += f"Failed Projects: {', '.join(failed_projects)}\n"

    summary += "\n=================\n"
    return summary

def main():
    logging.basicConfig(level=logging.INFO)

    all_results = {
        "projects": {}
    }

    try:
        driver = webdriver.Chrome()
        driver.maximize_window()

        # Check each project
        for project_name, project_urls in PROJECTS.items():
            all_results["projects"][project_name] = check_project(driver, project_name, project_urls)
            sleep(2)  # Pause between projects

        # Generate and print summary
        summary = generate_test_summary(all_results)
        print(summary)

    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
