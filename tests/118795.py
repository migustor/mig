import logging
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import string
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Define systems configuration
SYSTEMS = [
    {
        "name": "SM EU",
        "url": "https://stage15.office.sovasystem.com/euwhse/receive/enter_item_number.cfm",
        "document_number": "228545",
        "part_number": "841507"
    },
    {
        "name": "RA",
        "url": "https://stage15.office.ratrading.eu/euwhse/receive/enter_item_number.cfm",
        "document_number": "43259",
        "part_number": "BL1850B"
    },
    {
        "name": "AGAVA",
        "url": "https://stage15.office.agavasystem.com/euwhse/receive/enter_item_number.cfm",
        "document_number": "4471",
        "part_number": "0385JS891"
    },
    {
        "name": "Lanius",
        "url": "https://stage15.office.laniustoys.com/euwhse/receive/enter_item_number.cfm",
        "document_number": "41621",
        "part_number": "30689148"
    },
    {
        "name": "DB_R",
        "url": "https://stage15.office.dbreactor.com/euwhse/receive/enter_item_number.cfm",
        "document_number": "406",
        "part_number": "MOTIVMV51"
    },
    {
        "name": "Eminia",
        "url": "https://stage15.office.eminiasystem.com/euwhse/receive/enter_item_number.cfm",
        "document_number": "132341",
        "part_number": "31402415"
    },
    {
        "name": "Horus",
        "url": "https://stage15.office.horustrading.eu/euwhse/receive/enter_item_number.cfm",
        "document_number": "617",
        "part_number": "SE5505P"
    },
    {
        "name": "Atlas",
        "url": "https://stage15.office.atlastradingworld.com/euwhse/receive/enter_item_number.cfm",
        "document_number": "206",
        "part_number": "B5L46A"
    },
    {
        "name": "ARO",
        "url": "https://stage15.office.arotrading.eu/euwhse/receive/enter_item_number.cfm",
        "document_number": "11",
        "part_number": "GEOFLEX-25"
    },
    {
        "name": "Argon",
        "url": "https://stage15.office.argontrading.de/euwhse/receive/enter_item_number.cfm",
        "document_number": "13",
        "part_number": "19132"
    }
]

def setup_driver():
    logging.info("Setting up the Chrome driver.")
    options = webdriver.ChromeOptions()
    return webdriver.Chrome(options=options)

def login(driver, username, password, url):
    logging.info(f"Logging in as {username}")
    driver.get(url)
    try:
        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login_name")))
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()
        logging.info("Login successful.")
        return True
    except TimeoutException:
        logging.error(f"Timeout occurred while logging in for user {username}")
        return False
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")
        return False

def enter_data(driver, document_number):
    try:
        logging.info(f"Entering document number: {document_number}")
        document_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "document_number")))
        document_input.send_keys(document_number)
        submit_button = driver.find_element(By.ID, "start_receiving")
        submit_button.click()
        logging.info("Data entered successfully.")
        return True
    except TimeoutException:
        logging.error("Timeout occurred while entering data.")
        return False
    except NoSuchElementException:
        logging.error("Input field or submit button not found.")
        return False
    except Exception as e:
        logging.error(f"Error entering data: {str(e)}")
        return False

def enter_part_number(driver, part_number):
    try:
        logging.info(f"Entering part number: {part_number}")
        part_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "part_number")))
        part_input.send_keys(part_number)
        submit_button = driver.find_element(By.ID, "register_product")
        submit_button.click()
        logging.info("Part number entered successfully.")
        return True
    except TimeoutException:
        logging.error("Timeout occurred while entering part number.")
        return False
    except NoSuchElementException:
        logging.error("Input field or submit button not found.")
        return False
    except Exception as e:
        logging.error(f"Error entering part number: {str(e)}")
        return False

def generate_barcode():
    # Генерация случайной цифры от 0 до 9 для первого символа
    first_digit = str(random.randint(0, 9))

    # Генерация случайной заглавной буквы
    random_letter = random.choice(string.ascii_uppercase)

    # Генерация случайного четырехзначного числа
    random_number = random.randint(0, 9999)

    # Форматирование баркода: случайная цифра + случайная буква + четырехзначное число с ведущими нулями
    return f"{first_digit}{random_letter}{random_number:04d}"

def check_button_text(driver):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nextItem"))
        )
        button_text = next_button.get_attribute("value")
        expected_text = "Save Barcode"
        is_correct = button_text == expected_text
        logging.info(f"Button text check - Expected: '{expected_text}', Found: '{button_text}'")
        return button_text, is_correct
    except TimeoutException:
        logging.error("Timeout occurred while checking button text")
        return None, False
    except NoSuchElementException:
        logging.error("Button not found")
        return None, False

def enter_barcodes(driver):
    barcode_success = False
    final_barcode = None

    while True:
        try:
            barcodes = generate_barcode()
            logging.info(f"Entering barcode: {barcodes}")
            barcode_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "barcodes")))
            barcode_input.send_keys(barcodes)
            submit_button = driver.find_element(By.ID, "submit_btn")
            submit_button.click()

            # Check for barcode error message
            time.sleep(2)
            error_elements = driver.find_elements(By.CLASS_NAME, "scan_barcode_error")
            if error_elements:
                error_message = error_elements[0].text
                if "already exists in the system" in error_message:
                    logging.warning(f"Error occurred: {error_message}. Generating a new barcode.")
                    continue

            logging.info("Barcode entered successfully.")
            barcode_success = True
            final_barcode = barcodes
            break

        except TimeoutException:
            logging.error("Timeout occurred while entering barcodes.")
            break
        except NoSuchElementException:
            logging.error("Input field or submit button not found.")
            break

    return barcode_success, final_barcode

def select_random_option(driver, select_id):
    """
    Helper function to select a random option from a select element, excluding the first/default option
    """
    try:
        select_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, select_id))
        )
        options = select_element.find_elements(By.TAG_NAME, "option")
        # Filter out the default option (usually first one with value "0")
        valid_options = [opt for opt in options if opt.get_attribute("value") not in ["0", "None"]]
        if valid_options:
            random_option = random.choice(valid_options)
            random_option.click()
            logging.info(f"Selected option '{random_option.text}' from {select_id}")
            return True
        return False
    except TimeoutException:
        logging.info(f"Select element {select_id} not found (might be optional)")
        return False
    except Exception as e:
        logging.error(f"Error selecting option from {select_id}: {str(e)}")
        return False

def select_box_condition(driver):
    """
    Helper function to select the second option (first after None) from box condition select element
    """
    try:
        select_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "box_condition_select"))
        )
        # Получаем все опции
        options = select_element.find_elements(By.TAG_NAME, "option")
        # Проверяем, что есть хотя бы 2 опции (None и еще хотя бы одна)
        if len(options) >= 2:
            # Выбираем вторую опцию (индекс 1)
            second_option = options[1]
            second_option.click()
            selected_value = second_option.get_attribute("value")
            selected_text = second_option.text.strip()
            logging.info(f"Selected box condition: '{selected_text}' (value: {selected_value})")
            return True
        else:
            logging.warning("Box condition select has less than 2 options")
            return False
    except TimeoutException:
        logging.info("Box condition select element not found (might be optional)")
        return False
    except Exception as e:
        logging.error(f"Error selecting box condition: {str(e)}")
        return False

def select_random_country(driver):
    """
    Helper function to select a random country option, excluding the default option
    """
    try:
        select_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "country_of_origin_select"))
        )
        options = select_element.find_elements(By.TAG_NAME, "option")
        # Filter out the default option (usually first one with value "0")
        valid_options = [opt for opt in options if opt.get_attribute("value") not in ["0", "None"]]
        if valid_options:
            random_option = random.choice(valid_options)
            random_option.click()
            logging.info(f"Selected country '{random_option.text}'")
            return True
        return False
    except TimeoutException:
        logging.info("Country select element not found (might be optional)")
        return False
    except Exception as e:
        logging.error(f"Error selecting country: {str(e)}")
        return False

def enter_additional_inputs(driver, universal_input_value, box_qty_value):
    try:
        logging.info(f"Entering universal input: {universal_input_value}")
        universal_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "universal")))
        universal_input.send_keys(universal_input_value)

        logging.info(f"Entering box quantity: {box_qty_value}")
        box_qty_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "box_qty")))
        box_qty_input.send_keys(box_qty_value)

        # Try to select second box condition option if present
        box_condition_selected = select_box_condition(driver)
        logging.info(f"Box condition selection {'successful' if box_condition_selected else 'not available'}")

        # Try to select random country if present
        country_selected = select_random_country(driver)
        logging.info(f"Country selection {'successful' if country_selected else 'not available'}")

        submit_button = driver.find_element(By.ID, "nextItem")
        submit_button.click()
        logging.info("Additional inputs entered and submitted successfully.")

        return {
            "success": True,
            "box_condition_selected": box_condition_selected,
            "country_selected": country_selected
        }

    except TimeoutException:
        logging.error("Timeout occurred while entering additional inputs.")
        return {"success": False}
    except NoSuchElementException:
        logging.error("Input field or submit button not found.")
        return {"success": False}
    except Exception as e:
        logging.error(f"Error entering additional inputs: {str(e)}")
        return {"success": False}

def click_done_receiving(driver):
    try:
        logging.info("Clicking 'Done Receiving' button")
        done_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "done"))
        )
        done_button.click()
        logging.info("Successfully clicked 'Done Receiving' button")
        return True
    except TimeoutException:
        logging.error("Timeout occurred while looking for 'Done Receiving' button")
        return False
    except Exception as e:
        logging.error(f"Error clicking 'Done Receiving' button: {str(e)}")
        return False

def click_edit_link(driver):
    try:
        logging.info("Clicking 'Edit' link")
        edit_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'javascript: edit_barcode')]"))
        )
        edit_link.click()
        logging.info("Successfully clicked 'Edit' link")
        return True
    except TimeoutException:
        logging.error("Timeout occurred while looking for 'Edit' link")
        return False
    except Exception as e:
        logging.error(f"Error clicking 'Edit' link: {str(e)}")
        return False

def check_save_barcode_button(driver):
    try:
        # Wait for button to be present
        save_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "action"))
        )

        # Check button text
        button_text = save_button.get_attribute("value")
        expected_text = "Save Barcode"
        text_correct = button_text == expected_text

        # Check if button is enabled and clickable
        is_enabled = save_button.is_enabled()

        # Try to check if the button is clickable using explicit wait
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.NAME, "action"))
            )
            is_clickable = True
        except TimeoutException:
            is_clickable = False

        # Log the results
        logging.info(f"Save Barcode button check:")
        logging.info(f"- Expected text: '{expected_text}', Found: '{button_text}'")
        logging.info(f"- Button enabled: {is_enabled}")
        logging.info(f"- Button clickable: {is_clickable}")

        # Return comprehensive results
        return {
            "button_text": button_text,
            "text_correct": text_correct,
            "is_enabled": is_enabled,
            "is_clickable": is_clickable,
            "overall_success": text_correct and is_enabled and is_clickable
        }

    except TimeoutException:
        logging.error("Timeout occurred while checking Save Barcode button")
        return {
            "button_text": None,
            "text_correct": False,
            "is_enabled": False,
            "is_clickable": False,
            "overall_success": False
        }
    except Exception as e:
        logging.error(f"Error checking Save Barcode button: {str(e)}")
        return {
            "button_text": None,
            "text_correct": False,
            "is_enabled": False,
            "is_clickable": False,
            "overall_success": False
        }

def test_system(driver, system):
    logging.info(f"\n=== Testing {system['name']} ===")
    results = {
        "system_name": system['name'],
        "login_success": False,
        "document_success": False,
        "part_number_success": False,
        "barcode_success": False,
        "final_barcode": None,
        "additional_inputs_success": False,
        "box_condition_selected": False,
        "country_selected": False,
        "done_receiving_success": False,
        "edit_link_success": False,
        "save_barcode_button_results": None
    }

    # Login
    results["login_success"] = login(driver, "maxim.lupan@mteam.md", "12", system['url'])
    if not results["login_success"]:
        return results

    time.sleep(2)

    # Enter document number
    results["document_success"] = enter_data(driver, system['document_number'])
    if not results["document_success"]:
        return results

    time.sleep(2)

    # Enter part number
    results["part_number_success"] = enter_part_number(driver, system['part_number'])
    if not results["part_number_success"]:
        return results

    time.sleep(2)

    # Enter barcodes
    barcode_success, final_barcode = enter_barcodes(driver)
    results.update({
        "barcode_success": barcode_success,
        "final_barcode": final_barcode
    })

    if barcode_success:
        # Enter additional inputs
        results["additional_inputs_success"] = enter_additional_inputs(driver, "TEST123", "5")

        if results["additional_inputs_success"]:
            # Click Done Receiving button
            results["done_receiving_success"] = click_done_receiving(driver)

            if results["done_receiving_success"]:
                time.sleep(2)
                # Click Edit link
                results["edit_link_success"] = click_edit_link(driver)

                if results["edit_link_success"]:
                    time.sleep(2)
                    # Check Save Barcode button with enhanced functionality check
                    button_results = check_save_barcode_button(driver)
                    results["save_barcode_button_results"] = button_results

                    # If button check fails, exit with error code 1
                    if not button_results["overall_success"]:
                        logging.error("Critical failure: Save Barcode button check failed")
                        logging.error(f"Button state: Text correct: {button_results['text_correct']}, "
                                    f"Enabled: {button_results['is_enabled']}, "
                                    f"Clickable: {button_results['is_clickable']}")
                        sys.exit(1)

    return results

def generate_test_summary(all_results):
    logging.info("Generating complete test summary.")
    summary = "=== Complete Test Summary ===\n\n"

    for result in all_results:
        summary += f"System: {result['system_name']}\n"
        # [Previous summary items remain the same...]

        if result.get('save_barcode_button_results'):
            button_results = result['save_barcode_button_results']
            summary += "Save Barcode Button Check:\n"
            summary += f"- Text correct: {'Yes' if button_results['text_correct'] else 'No'}\n"
            summary += f"- Button enabled: {'Yes' if button_results['is_enabled'] else 'No'}\n"
            summary += f"- Button clickable: {'Yes' if button_results['is_clickable'] else 'No'}\n"
            if button_results['button_text']:
                summary += f"- Actual button text: '{button_results['button_text']}'\n"
            summary += f"- Overall button check: {'PASS' if button_results['overall_success'] else 'FAIL'}\n"

        summary += "\n" + "="*50 + "\n\n"

    return summary

if __name__ == "__main__":
    all_results = []

    for system in SYSTEMS:
        driver = setup_driver()
        try:
            results = test_system(driver, system)
            all_results.append(results)
            time.sleep(2)
        except SystemExit as e:
            # Re-raise SystemExit to ensure proper exit
            raise
        except Exception as e:
            logging.error(f"Error testing {system['name']}: {str(e)}")
            all_results.append({
                "system_name": system['name'],
                "error": str(e)
            })
        finally:
            driver.quit()

    summary = generate_test_summary(all_results)
    logging.info(summary)
