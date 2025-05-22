import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, ElementNotInteractableException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Test Configuration
TEST_URL = "https://stage15.office.grafit.md/sage/?logout"
LOGIN_NAME = "victor.moisei@mteam.md"
PASSWORD = "12"

# Given name parts:
first_name = "Anna"
middle_name = "Maria"
last_name = "Island"

# The original base version is "Anna Island Maria"
BASE_THREE_WORD_NAME = "Anna Island Maria"

single_word_tests = [first_name, last_name, middle_name]
two_word_tests = [
    f"{first_name} {last_name}",
    f"{last_name} {first_name}",
    f"{first_name} {middle_name}",
    f"{middle_name} {first_name}",
    f"{last_name} {middle_name}",
    f"{middle_name} {last_name}"
]

three_word_tests = [
    f"{first_name} {last_name} {middle_name}",
    f"{last_name} {first_name} {middle_name}",
    f"{first_name} {middle_name} {last_name}",
    f"{middle_name} {first_name} {last_name}",
    f"{last_name} {middle_name} {first_name}",
    f"{middle_name} {last_name} {first_name}"
]

space_tests = [
    f"  {first_name}  ",
    f"   {first_name} {last_name} {middle_name}   "
]

case_tests = [
    (first_name + " " + last_name + " " + middle_name).upper(),
    (first_name + " " + last_name + " " + middle_name).lower(),
    "AnNa MaRiA IsLaNd"
]

TEST_INPUTS = single_word_tests + two_word_tests + three_word_tests + space_tests + case_tests

# New tests with numbered variations
numbered_tests = [
    "Anna1 Maria1 Island1",
    "Anna12 Maria12 Island12"
]

steps_passed = 0
steps_failed = 0
test_results = []
log_history = []

def log_message(message):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    msg = f"[{current_time}] {message}"
    print(msg)
    log_history.append(msg)

def wait_for_results(driver, max_retries=3):
    """
    Waits for the results table to appear, with up to 3 retries if the element
    is not yet present due to slow loading or timeouts.
    """
    for attempt in range(max_retries):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.panel.panel-default[data-grid-view-form-id='frm_search']"))
            )
            results_panel = driver.find_element(By.CSS_SELECTOR, "div.panel.panel-default[data-grid-view-form-id='frm_search']")
            results_table = results_panel.find_element(By.CSS_SELECTOR, "table.table.table-bordered.table-striped")
            return results_table
        except (NoSuchElementException, TimeoutException) as e:
            if attempt < max_retries - 1:
                log_message(f"Retry attempt {attempt + 1} due to {e}. Waiting before retry...")
                time.sleep(2)
            else:
                raise

def find_candidate_position(results_table, search_input):
    # Returns (position_of_exact_match, result_count, top_candidate_name)
    rows = results_table.find_elements(By.CSS_SELECTOR, "tbody tr")
    result_count = len(rows)
    top_candidate_name = None
    exact_match_position = None
    
    for idx, row in enumerate(rows, start=1):
        try:
            candidate_link = row.find_element(By.CSS_SELECTOR, "td a")
            candidate_name = candidate_link.text.strip()
            if idx == 1:
                top_candidate_name = candidate_name

            # Check exact match against search_input
            if candidate_name.lower() == search_input.lower():
                exact_match_position = idx
        except NoSuchElementException:
            continue
    return exact_match_position, result_count, top_candidate_name

def verify_base_name_on_top(driver):
    # Ensure the base three-word name is at the top of the results
    results_table = driver.find_element(By.CSS_SELECTOR, "table.table.table-bordered.table-striped")
    exact_match_position, result_count, top_candidate_name = find_candidate_position(results_table, BASE_THREE_WORD_NAME)
    if exact_match_position == 1:
        log_message(f"PASS: Base name '{BASE_THREE_WORD_NAME}' is on top as per original version requirement.")
        return True
    else:
        log_message(f"FAIL: Base name '{BASE_THREE_WORD_NAME}' not on top. Found '{top_candidate_name}' at top instead.")
        return False

def verify_three_word_exact_match(driver, search_input):
    # If three words do not match the base set, we check exact match ordering
    results_table = driver.find_element(By.CSS_SELECTOR, "table.table.table-bordered.table-striped")
    exact_match_position, result_count, top_candidate_name = find_candidate_position(results_table, search_input)

    if exact_match_position == 1:
        log_message(f"PASS: Exact match '{search_input}' is on top.")
        return True
    else:
        log_message(f"FAIL: Exact match '{search_input}' not on top. Found '{top_candidate_name}' at top.")
        return False

def check_relevance_order(driver, search_input):
    words = search_input.strip().split()
    base_words_set = set(BASE_THREE_WORD_NAME.lower().split())
    input_words_set = set(w.lower() for w in words)

    if len(words) == 3:
        # If all three words match the base set of words,
        # we expect the base version (Anna Island Maria) to be on top.
        if base_words_set == input_words_set:
            return verify_base_name_on_top(driver)
        else:
            # If it's a three-word input but doesn't match the base set of words,
            # fall back to exact match logic for that particular input order.
            return verify_three_word_exact_match(driver, search_input)
    else:
        log_message("No strict full-name ordering check required for this input.")
        return True

def handle_pagination(driver):
    try:
        pagination_ul = driver.find_element(By.CSS_SELECTOR, "ul.pagination")
        log_message("Pagination found. Checking multiple pages.")
        while True:
            results_table = driver.find_element(By.CSS_SELECTOR, "table.table.table-bordered.table-striped")
            try:
                first_candidate = results_table.find_element(By.CSS_SELECTOR, "tbody tr:nth-of-type(1) td a").text
                log_message(f"First candidate on current page: {first_candidate}")
            except NoSuchElementException:
                log_message("No candidate found on this page.")

            try:
                pagination_ul = driver.find_element(By.CSS_SELECTOR, "ul.pagination")
                next_page_link = pagination_ul.find_element(By.XPATH, ".//li/a/span[@aria-hidden='true' and text()='»']/ancestor::a")
                next_li = next_page_link.find_element(By.XPATH, "./ancestor::li")
                if "disabled" in next_li.get_attribute("class"):
                    log_message("No more pages.")
                    break
                next_page_link.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered.table-striped"))
                )
            except NoSuchElementException:
                log_message("No next page link found. End of pagination.")
                break
    except NoSuchElementException:
        log_message("No pagination found. Only one page of results.")

try:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    log_message("STEP: Navigating to login page.")
    driver.get(TEST_URL)
    steps_passed += 1

    # Login
    try:
        log_message("Logging in.")
        login_name_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login_name")))
        login_name_field.clear()
        login_name_field.send_keys(LOGIN_NAME)
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(PASSWORD)
        password_field.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "name")))
        steps_passed += 1
    except Exception as e:
        log_message(f"ERROR: Login failed due to {e}")
        steps_failed += 1
        raise

    # Test each input from the main list
    for input_query in TEST_INPUTS:
        try:
            cleaned_input = input_query.strip()
            log_message("========================================")
            log_message(f"Testing input: '{input_query}' (cleaned: '{cleaned_input}')")

            # Enter query and pause briefly
            try:
                name_field = driver.find_element(By.NAME, "name")
                name_field.clear()
                name_field.send_keys(input_query)
                time.sleep(0.01)  # small pause
                name_field.send_keys(Keys.ENTER)
                steps_passed += 1
            except NoSuchElementException:
                log_message("ERROR: Name field not found.")
                steps_failed += 1
                test_results.append((input_query, "FAIL - Name field missing"))
                continue

            # Wait for results with up to 3 retries
            try:
                results_table = wait_for_results(driver)
                rows = results_table.find_elements(By.CSS_SELECTOR, "tbody tr")
                result_count = len(rows)

                if result_count > 0:
                    exact_match_position, total, top_candidate_name = find_candidate_position(results_table, cleaned_input)
                    if exact_match_position:
                        log_message(f"{result_count} results found for '{input_query}'. '{cleaned_input}' was found at position {exact_match_position}.")
                    else:
                        log_message(f"{result_count} results found for '{input_query}'. '{cleaned_input}' exact match not found.")
                    steps_passed += 1
                else:
                    log_message(f"WARNING: No results found for '{input_query}'.")
                    steps_failed += 1
                    test_results.append((input_query, "FAIL - No results"))
                    continue
            except (NoSuchElementException, TimeoutException):
                log_message(f"ERROR: Results not displayed for '{input_query}'.")
                steps_failed += 1
                test_results.append((input_query, "FAIL - Results not displayed"))
                continue

            # Check relevance and exact match logic
            if check_relevance_order(driver, cleaned_input):
                steps_passed += 1
                test_results.append((input_query, "PASS - Relevance/Ordering Check"))
            else:
                steps_failed += 1
                test_results.append((input_query, "FAIL - Relevance/Ordering Check"))

            # Check pagination
            handle_pagination(driver)
            steps_passed += 1

        except Exception as e:
            log_message(f"ERROR: Exception during test '{input_query}': {e}")
            steps_failed += 1
            test_results.append((input_query, f"FAIL - Exception: {e}"))

    # Test the numbered names
    for numbered_input in numbered_tests:
        try:
            cleaned_input = numbered_input.strip()
            log_message("========================================")
            log_message(f"Testing input: '{numbered_input}' (cleaned: '{cleaned_input}')")

            # Enter query and pause
            try:
                name_field = driver.find_element(By.NAME, "name")
                name_field.clear()
                name_field.send_keys(numbered_input)
                time.sleep(0.01)
                name_field.send_keys(Keys.ENTER)
                steps_passed += 1
            except NoSuchElementException:
                log_message("ERROR: Name field not found.")
                steps_failed += 1
                test_results.append((numbered_input, "FAIL - Name field missing"))
                continue

            # Wait for results with up to 3 retries
            try:
                results_table = wait_for_results(driver)
                rows = results_table.find_elements(By.CSS_SELECTOR, "tbody tr")
                result_count = len(rows)

                if result_count > 0:
                    exact_match_position, total, top_candidate_name = find_candidate_position(results_table, cleaned_input)
                    
                    if exact_match_position == 1:
                        log_message(f"PASS: Exact match '{cleaned_input}' is on top.")
                        test_results.append((numbered_input, "PASS - Numbered Name Relevance/Ordering Check"))
                        steps_passed += 1
                    else:
                        log_message(f"FAIL: Exact match '{cleaned_input}' not on top. Found '{top_candidate_name}' at top.")
                        test_results.append((numbered_input, "FAIL - Numbered Name Relevance/Ordering Check"))
                        steps_failed += 1
                else:
                    log_message(f"WARNING: No results found for '{numbered_input}'.")
                    steps_failed += 1
                    test_results.append((numbered_input, "FAIL - No results"))
                    continue

            except (NoSuchElementException, TimeoutException):
                log_message(f"ERROR: Results not displayed for '{numbered_input}'.")
                steps_failed += 1
                test_results.append((numbered_input, "FAIL - Results not displayed"))

            # Pagination check (if needed)
            handle_pagination(driver)
            steps_passed += 1

        except Exception as e:
            log_message(f"ERROR: Exception during test '{numbered_input}': {e}")
            steps_failed += 1
            test_results.append((numbered_input, f"FAIL - Exception: {e}"))

except Exception as e:
    log_message(f"TEST FAILURE: An exception occurred globally: {e}")
    steps_failed += 1
finally:
    # BEAUTIFUL TEST SUMMARY
    log_message("========================================")
    log_message("              TEST SUMMARY              ")
    log_message("========================================")
    log_message(f"TOTAL STEPS PASSED: {steps_passed}")
    log_message(f"TOTAL STEPS FAILED: {steps_failed}")
    log_message("----------------------------------------")
    for input_query, outcome in test_results:
        log_message(f"Input '{input_query}': {outcome}")
    log_message("========================================")

    failed_condition = any("FAIL" in outcome for _, outcome in test_results)

    if failed_condition:
        print("One or more tests have failed. Exiting with error.")
        sys.exit(1)
    else:
        print("All tests passed successfully.")
        sys.exit(0)

    driver.quit()
