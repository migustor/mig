from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dataclasses import dataclass
from typing import List, Dict
import json
import logging
from datetime import datetime
import time

@dataclass
class TableStructure:
    name: str
    expected_columns: List[str]
    section_header: str

class TransactionPageChecker:
    def __init__(self):
        # Configure logging
        self.setup_logging()

        # Define expected structures
        self.expected_tables = {
            'sales': TableStructure(
                name="Sales Orders",
                expected_columns=["SO #", "Invoice", "Creation Date", "Ready to Ship",
                                "Value", "Sales Representative"],
                section_header="Sales Transactions:"
            ),
            'buying': TableStructure(
                name="Purchase Orders",
                expected_columns=["PO #", "Creation Date", "Value", "MB, %",
                                "Buying Rep", "Status", "Price Per", "Payment method"],
                section_header="Buying Transactions:"
            ),
            'leads': TableStructure(
                name="Leads",
                expected_columns=["Lead #", "Creation Date", "Max Buy Value",
                                "Buying Representative", "Status"],
                section_header="Leads:"
            )
        }

    def setup_logging(self):
        """Configure logging settings"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()  # Only console output
            ]
        )

    def setup_driver(self):
        """Set up and configure the Chrome driver"""
        logging.info("Setting up the Chrome driver")
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        # Add headless mode if needed
        # options.add_argument('--headless')
        return webdriver.Chrome(options=options)

    def login(self, driver, username: str, password: str) -> bool:
        """
        Handle the login process
        Returns True if login successful, False otherwise
        """
        logging.info(f"Attempting to login as {username}")
        try:
            # Navigate to login page
            driver.get("https://stage28.office.horustrading.eu/sage/index.cfm?page_id=830&company_id=80914")

            # Wait for and find login elements
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "login_name"))
            )
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )

            # Enter credentials
            username_input.clear()
            username_input.send_keys(username)
            password_input.clear()
            password_input.send_keys(password)

            # Submit login form
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="Submit"]'))
            )
            submit_button.click()

            # Wait for successful login (adjust selector as needed)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "scr_module_content"))
            )

            logging.info("Login successful")
            return True

        except TimeoutException as e:
            logging.error(f"Timeout during login: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Error during login: {str(e)}")
            return False

    def check_page_structure(self, driver) -> Dict:
        """
        Checks the structure of the Transaction Activity page
        Returns a dictionary with detailed results
        """
        logging.info("Starting page structure check")
        results = {
            "page_title_present": False,
            "sections": {},
            "detailed_results": {},
            "access_rights": {}
        }

        try:
            page_content = driver.find_element(By.CLASS_NAME, "scr_module_content")
            results["page_title_present"] = page_content.is_displayed()
        except Exception as e:
            logging.warning(f"Error checking page content: {str(e)}")

        for section_key, structure in self.expected_tables.items():
            logging.info(f"Checking section: {section_key}")
            section_results = {
                "header_present": False,
                "table_present": False,
                "columns_present": [],
                "missing_columns": [],
                "additional_columns": [],
                "columns_data": {},  # New field for column data analysis
                "features": {},
                "access_status": "Unknown"
            }

            try:
                header = driver.find_element(By.XPATH, f"//h2[contains(text(),'{structure.section_header}')]")
                section_results["header_present"] = header.is_displayed()
            except Exception as e:
                logging.warning(f"Error checking {section_key} header: {str(e)}")

            table_selector = ""
            if section_key == "sales":
                table_selector = "legacy_sale_table"
            elif section_key == "buying":
                table_selector = "legacy_po_table"
            elif section_key == "leads":
                table_selector = "lead_leads_table"

            try:
                table = driver.find_element(By.ID, table_selector)
                section_results["table_present"] = table.is_displayed()
                section_results["access_status"] = "Full Access"

            # Get headers and their positions
                headers = table.find_elements(By.XPATH, ".//tr[@class='th2']/td")
                header_texts = [h.text.strip() for h in headers]

            # Get all data rows
                rows = table.find_elements(By.XPATH, ".//tr[not(@class='th2') and not(th)]")

            # Initialize column data analysis
                for header in header_texts:
                    section_results["columns_data"][header] = {
                        "total_cells": 0,
                        "empty_cells": 0,
                        "dash_cells": 0,
                        "filled_cells": 0
                    }

            # Analyze each row
                for row in rows:
                    cells = row.find_elements(By.XPATH, "./td")
                    for idx, cell in enumerate(cells):
                        if idx < len(header_texts):  # Ensure we don't go out of bounds
                            header = header_texts[idx]
                            value = cell.text.strip()
                            section_results["columns_data"][header]["total_cells"] += 1

                            if value == "":
                                section_results["columns_data"][header]["empty_cells"] += 1
                            elif value == "-":
                                section_results["columns_data"][header]["dash_cells"] += 1
                            else:
                                section_results["columns_data"][header]["filled_cells"] += 1

                # Check special features and controls
                if section_key == "sales":
                    try:
                        # Check for "Show not shipped orders" checkbox
                        checkbox = driver.find_element(By.ID, "show_not_shipped_orders")
                        checkbox_label = driver.find_element(By.CLASS_NAME, "show_not_shipped_label")
                        section_results["features"]["show_not_shipped_checkbox"] = {
                            "present": checkbox.is_displayed(),
                            "enabled": not checkbox.get_attribute("disabled"),
                            "label": checkbox_label.text
                        }
                        logging.info("Sales checkbox feature checked")
                    except Exception as e:
                        section_results["features"]["show_not_shipped_checkbox"] = {
                            "present": False,
                            "error": str(e)
                        }
                        logging.warning(f"Error checking sales checkbox: {str(e)}")

                elif section_key == "buying":
                    try:
                        # Простая проверка наличия радио-кнопок
                        all_radio = table.find_element(By.NAME, "legacy_po_outsource_radio")
                        section_results["features"]["radio_controls"] = {
                            "present": True
                        }
                        logging.info("Buying radio buttons found")
                    except Exception as e:
                        section_results["features"]["radio_controls"] = {
                            "present": False
                        }
                        logging.warning("Buying radio buttons not found")

                # Standard column presence check
                found_columns = header_texts
                for expected_col in structure.expected_columns:
                    if expected_col in found_columns:
                        section_results["columns_present"].append(expected_col)
                    else:
                        section_results["missing_columns"].append(expected_col)

                for found_col in found_columns:
                    if found_col not in structure.expected_columns:
                        section_results["additional_columns"].append(found_col)

            except Exception as e:
                error_message = str(e)
                if "no such element" in error_message:
                    section_results["access_status"] = "No Access"
                    section_results["error"] = "User does not have access to this section"
                    logging.info(f"User does not have access to {section_key} section")
                else:
                    section_results["access_status"] = "Error"
                    section_results["error"] = error_message
                    logging.error(f"Error checking {section_key} section: {error_message}")

            results["sections"][section_key] = section_results
            results["access_rights"][section_key] = section_results["access_status"]

        return results


    def generate_test_summary(self, results: Dict) -> str:
            """
            Generates a concise summary of the test results including control elements
            """
            summary = "\n=== TEST SUMMARY ===\n"

        # Access Rights Summary
            summary += "\nAccess Status:\n"
            for section, status in results["access_rights"].items():
                icon = "[+]" if status == "Full Access" else "[-]"
                summary += f"{icon} {section.upper()}: {status}\n"

        # Data and Controls Summary
            summary += "\nData & Controls Status:\n"
            for section_name, section_data in results["sections"].items():
                if section_data["table_present"]:
                    summary += f"\n{section_name.upper()} Table:\n"

                # Check for special features first
                    if 'features' in section_data:
                        summary += "Controls:\n"
                        if section_name == "sales":
                            checkbox = section_data["features"].get("show_not_shipped_checkbox", False)
                            summary += f"[{'+' if checkbox else '-'}] Show Not Shipped Orders checkbox\n"
                        elif section_name == "buying":
                            radio_controls = section_data["features"].get("radio_controls", {})
                            summary += f"[{'+' if radio_controls.get('present') else '-'}] All/Outsourced radio buttons\n"

                # Data presence information
                    summary += "Columns:\n"
                    for column, data in section_data["columns_data"].items():
                        total = data["total_cells"]
                        if total > 0:
                            filled_percent = (data["filled_cells"] / total * 100)
                            dash_percent = (data["dash_cells"] / total * 100)

                        # Determine column status
                            if filled_percent > 70:
                                status = "FILLED"
                                icon = "[+]"
                            elif filled_percent > 30:
                                status = "PARTIAL"
                                icon = "[!]"
                            elif dash_percent > 70:
                                status = "DASHES"
                                icon = "[-]"
                            else:
                                status = "EMPTY"
                                icon = "[X]"

                            summary += f"{icon} {column}: {status} ({filled_percent:.0f}%)\n"
                else:
                    summary += f"\n{section_name.upper()} Table: NOT ACCESSIBLE\n"

            summary += "\n=================\n"
            return summary

# Функцию run_check меняем на:
def run_check(username: str, password: str) -> None:
    """
    Main function to run the page structure check
    """
    checker = TransactionPageChecker()
    driver = None
    try:
        driver = checker.setup_driver()

        if not checker.login(driver, username, password):
            print("Login failed. Aborting check.")
            return

        time.sleep(5)

        results = checker.check_page_structure(driver)

        # Generate and print summary only
        summary = checker.generate_test_summary(results)
        print(summary)

    except Exception as e:
        print(f"Error during check: {str(e)}")
    finally:
        if driver:
            driver.quit()

# Example usage:
if __name__ == "__main__":
    run_check(
        username="user58540@mteam.test",
        password="12"
    )
