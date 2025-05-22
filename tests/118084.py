from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# Define URLs and corresponding prefixes
urls_and_prefixes = {
    "https://stage15.office.sovasystem.com/sage/index.cfm?page_id=985": ("sm eu", "sm_eu"),
    "https://stage15.office.sovamaxusa.com/sage/index.cfm?page_id=985": ("sm us", "sm_us"),
    "https://stage15.office.ratrading.eu/sage/index.cfm?page_id=985": ("ra eu", "ra_eu"),
    "https://stage15.office.agavasystem.com/sage/index.cfm?page_id=985": ("ag eu", "ag_eu"),
    "https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=985": ("et eu", "et_eu"),
}

# Login credentials
username = "valeriu.bistritchi@mteam.md"
password = "12"

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")  # Start Chrome maximized

# Initialize WebDriver with options
driver = webdriver.Chrome(options=chrome_options)

test_results = []

# Loop through each URL and perform the test
for url, (expected_prefix, expected_prefix_underscore) in urls_and_prefixes.items():
    print(f"Opening URL: {url}")
    driver.get(url)
    
    # Log in
    print("Entering login credentials")
    driver.find_element(By.ID, 'login_name').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-info.btn-lg').click()
    
    # Wait for the button to appear and click it
    try:
        print("Waiting for button to appear and clicking it")
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.btn.btn-primary'))
        )
        button.click()
        time.sleep(2)  # Wait for the table to load
    except Exception as e:
        print(f"Error in navigating to table on {url}: {e}")
        continue
    
    # Find the file table and check filenames in the second column
    print("Checking file names in table")
    rows = driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
    result = f"{expected_prefix.upper()} NAME CORRECT"
    # Regex to match either space-separated or underscore-separated prefixes
    prefix_pattern = re.compile(rf"^({expected_prefix}|{expected_prefix_underscore})(_| |\b)", re.IGNORECASE)

    for row_index, row in enumerate(rows):
        try:
            # Get filename from the second column
            file_name_elements = row.find_elements(By.TAG_NAME, "td")
            if len(file_name_elements) < 2:
                print(f"Row {row_index + 1} does not contain enough columns, skipping")
                continue
            
            file_name = file_name_elements[1].text  # Text of the second column
            print(f"Found file name: {file_name}")
            
            # Skip rows with 'Browse…' links to avoid false positives
            if file_name.lower().strip() == "browse…":
                print(f"Row {row_index + 1} contains a 'Browse...' link, skipping")
                continue
            
            # Check if the filename starts with either the space-separated or underscore-separated prefix
            if not prefix_pattern.match(file_name):
                result = f"{expected_prefix.upper()} NAME INCORRECT"
                print(f"{expected_prefix.upper()} ERROR for document {file_name}")

        except Exception as e:
            print(f"Error processing row {row_index + 1}: {e}")
            result = f"{expected_prefix.upper()} NAME INCORRECT"
            break
    
    # Append result to test summary
    test_results.append(result)

# Print test summary
print("\n=== TEST SUMMARY ===")
all_ok = True
for result in test_results:
    print(result)
    if "INCORRECT" in result:
        all_ok = False

if all_ok:
    print("ALL OK on all projects")
else:
    print("Errors found in one or more projects")

# Close the browser
driver.quit()
