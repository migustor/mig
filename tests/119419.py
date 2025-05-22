import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import difflib
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    logging.info("Setting up the Chrome driver.")
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    return webdriver.Chrome(options=options)

def login(driver, username, password):
    logging.info(f"Logging in as {username}")
    driver.get("https://stage5.office.eminiasystem.com/sage/index.cfm?page_id=864")
    try:
        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login_name")))
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()
        logging.info("Login successful.")
    except TimeoutException:
        logging.error(f"Timeout occurred while logging in for user {username}")

def find_first_link_in_table(driver):
    logging.info("Finding the first link in the table.")
    try:
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "td > a[target='_blank'][href*='page_id=864'][href*='phase=edit'][href*='id=']"))
        )
        href = table.get_attribute('href')
        logging.info(f"Found link: {href}")
        return href
    except (TimeoutException, NoSuchElementException):
        logging.error("Failed to find the required table or link.")
        return None

def normalize_element_string(element_str):
    logging.info(f"Normalizing element string: {element_str}")
    element_str = re.sub(r'([#.][a-zA-Z_]+)[_\d]+', r'\1', element_str)
    element_str = re.sub(r'_+', '_', element_str)
    element_str = re.sub(r'_\.', '.', element_str)
    return element_str.rstrip('_')

def normalize_content(content):
    logging.info("Normalizing content.")
    content = re.sub(r'(\w+)_\d+', r'\1_X', content)
    content = re.sub(r"random_int\s*:\s*'\d+'", "random_int : 'X'", content)
    return content

def get_page_elements_and_content(driver):
    logging.info("Getting page elements and content.")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    start_element = soup.select_one('h1.xmb0 b#title_page_name')

    if not start_element:
        logging.warning("Start element not found.")
        return set(), {}

    elements = set()
    content = {}
    for element in start_element.find_all_next():
        element_str = f"{element.name}"
        if element.get('id'):
            element_str += f"#{element['id']}_X"
        if element.get('class'):
            element_str += f".{'.'.join(element['class'])}"

        normalized_element_str = normalize_element_string(element_str)
        elements.add(normalized_element_str)
        content[normalized_element_str] = normalize_content(element.get_text(strip=True))

    logging.info(f"Extracted {len(elements)} elements and their content.")
    return elements, content

def compare_element_content(content1, content2):
    logging.info("Comparing element content.")
    lines1 = [line.strip() for line in content1.split('\n') if line.strip()]
    lines2 = [line.strip() for line in content2.split('\n') if line.strip()]

    differ = difflib.Differ()
    diff = list(differ.compare(lines1, lines2))

    differences = [line for line in diff if line.startswith('- ') or line.startswith('+ ')]
    summarized_differences = []

    for line in differences:
        if line.startswith('- '):
            summarized_differences.append(f"Only in user112615@mteam.test: {line[2:]}")
        elif line.startswith('+ '):
            summarized_differences.append(f"Only in user1121@mteam.test: {line[2:]}")

    return summarized_differences

def categorize_element(element):
    logging.info(f"Categorizing element: {element}")
    frontend_indicators = ['div', 'span', 'p', 'a', 'button', 'input', 'select', 'textarea', 'form', 'img',
                           'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th',
                           'thead', 'tbody', 'tfoot', 'script', 'style']
    backend_indicators = ['cfoutput', 'cfif', 'cfelse', 'cfelseif', 'cfloop', 'cfquery', 'cffunction',
                          'cfargument', 'cfset', 'cfreturn']

    element_parts = element.lower().split('.')
    element_name = element_parts[0].split('#')[0]

    if element_name in frontend_indicators or any(indicator in element for indicator in ['class', 'id']):
        return "Frontend"
    elif element_name in backend_indicators:
        return "Backend"
    else:
        return "Unknown"

def compare_pages(driver1, driver2):
    logging.info("Comparing pages.")
    elements1, content1 = get_page_elements_and_content(driver1)
    elements2, content2 = get_page_elements_and_content(driver2)

    unique_to_user1 = elements1 - elements2
    unique_to_user2 = elements2 - elements1

    unique_to_user1 = {elem for elem in unique_to_user1 if '_X' not in elem}
    unique_to_user2 = {elem for elem in unique_to_user2 if '_X' not in elem}

    content_differences = {}
    for element in elements1.intersection(elements2):
        if content1[element] != content2[element]:
            diff = compare_element_content(content1[element], content2[element])
            if diff:
                content_differences[element] = diff

    logging.info(f"Comparison complete. Unique elements to user1: {len(unique_to_user1)}, Unique elements to user2: {len(unique_to_user2)}, Content differences: {len(content_differences)}.")
    return unique_to_user1, unique_to_user2, content_differences

def generate_test_summary(unique_to_user1, unique_to_user2, content_differences):
    logging.info("Generating test summary.")
    summary = "== Test Summary ==\n"

    total_differences = len(unique_to_user1) + len(unique_to_user2) + len(content_differences)
    summary += f"Total differences found: {total_differences}\n\n"

    summary += f"Elements unique to user112615@mteam.test: {len(unique_to_user1)}\n"
    summary += f"Elements unique to user1121@mteam.test: {len(unique_to_user2)}\n"
    summary += f"Elements with content differences: {len(content_differences)}\n\n"

    frontend_diff = backend_diff = unknown_diff = 0
    for elem in unique_to_user1.union(unique_to_user2).union(content_differences.keys()):
        category = categorize_element(elem)
        if category == "Frontend":
            frontend_diff += 1
        elif category == "Backend":
            backend_diff += 1
        else:
            unknown_diff += 1

    summary += "Differences by category:\n"
    summary += f"Frontend: {frontend_diff}\n"
    summary += f"Backend: {backend_diff}\n"
    summary += f"Unknown: {unknown_diff}\n"

    logging.info("Test summary generated.")
    return summary

def main():
    driver1 = setup_driver()
    driver2 = setup_driver()

    try:
        login(driver1, "user112615@mteam.test", "12")
        login(driver2, "user1121@mteam.test", "12")

        for driver in [driver1, driver2]:
            logging.info("Clicking the submit button.")
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input#submit_btn[type='submit'][value='Submit']"))
            )
            submit_button.click()

        href = find_first_link_in_table(driver1)
        if href:
            logging.info("Navigating to the link on both drivers.")
            driver1.get(href)
            driver2.get(href)

            logging.info("Comparing pages after navigating to the link.")
            unique_to_user1, unique_to_user2, content_differences = compare_pages(driver1, driver2)

            if not unique_to_user1 and not unique_to_user2 and not content_differences:
                logging.info("The pages are identical. No differences found.")
                print("The pages are identical. No differences found.")
            else:
                if unique_to_user1:
                    logging.info(f"Elements unique to user112615@mteam.test: {len(unique_to_user1)}")
                    print("Elements unique to user112615@mteam.test:")
                    for elem in unique_to_user1:
                        category = categorize_element(elem)
                        print(f"{elem} - {category}")

                if unique_to_user2:
                    logging.info(f"Elements unique to user1121@mteam.test: {len(unique_to_user2)}")
                    print("\nElements unique to user1121@mteam.test:")
                    for elem in unique_to_user2:
                        category = categorize_element(elem)
                        print(f"{elem} - {category}")

                if content_differences:
                    logging.info(f"Differences in content of common elements: {len(content_differences)}")
                    print("\nDifferences in content of common elements:")
                    for elem, diff in content_differences.items():
                        category = categorize_element(elem)
                        print(f"Element: {elem} - {category}")
                        for line in diff:
                            if "Only in user112615@mteam.test" in line or "Only in user1121@mteam.test" in line:
                                print(f"  {line}")
                        print()

            summary = generate_test_summary(unique_to_user1, unique_to_user2, content_differences)
            logging.info("Printing the test summary.")
            print(summary)
        else:
            logging.error("Failed to find the required link.")

    finally:
        logging.info("Closing drivers.")
        time.sleep(1)  # Give time to view the results
        driver1.quit()
        driver2.quit()

if __name__ == "__main__":
    main()
