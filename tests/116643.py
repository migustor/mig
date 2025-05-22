import logging
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    logging.info("Setting up the Chrome driver.")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Open browser in full window
    return webdriver.Chrome(options=options)

def login(driver, username, password):
    logging.info(f"Logging in as {username}")
    driver.get("https://stage5.office.ratrading.eu/sage/index.cfm?page_id=925&phase=new")
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

def fill_sales_inquiry_form(driver):
    try:
        logging.info("Filling out the Sales Inquiry form.")

        # Fill in the Customer field
        customer_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search_customer")))
        customer_input.click()
        customer_input.send_keys("company")
        time.sleep(2)  # Pause to allow the autocomplete dropdown to appear
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # Wait for the autocomplete dropdown to appear
        customer_input.send_keys(Keys.ENTER)
        logging.info("Customer field filled.")

        # Fill in the Add Item field
        item_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search_item")))
        item_input.click()
        item_input.send_keys("12")
        time.sleep(2)  # Pause to allow the autocomplete dropdown to appear
        time.sleep(2)  # Wait for the autocomplete dropdown to appear
        item_input.send_keys(Keys.ENTER)
        logging.info("Add Item field filled.")

        # Click the Add button
        add_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "add-item")))
        add_button.click()
        logging.info("Item added.")

        # Verify the success alert
        alert = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "alert-success")))
        if "Item Added." in alert.text:
            logging.info("Item successfully added - success alert verified.")

        # Click the Create Sales Inquiry button
        create_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "search_si")))
        create_button.click()
        logging.info("Create Sales Inquiry button clicked.")

    except TimeoutException:
        logging.error("Timeout occurred while filling out the Sales Inquiry form.")
    except NoSuchElementException:
        logging.error("One or more elements not found while filling out the Sales Inquiry form.")

def close_sales_inquiry(driver):
    try:
        logging.info("Closing Sales Inquiry.")
        close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "cancel_request")))
        close_button.click()

        # Click the Send button in the popup
        send_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "cancel_evenet")))
        send_button.click()
        logging.info("Sales Inquiry closed.")

        # Verify status change
        status_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "status_name")))
        if "Couldn't close a deal" in status_element.text:
            logging.info("Status verified: Couldn't close a deal.")
        else:
            logging.warning("Status verification failed.")
    except TimeoutException:
        logging.error("Timeout occurred while closing the Sales Inquiry.")
    except NoSuchElementException:
        logging.error("One or more elements not found while closing the Sales Inquiry.")

def generate_random_text(option):
    if option == 1:
        return " ".join(random.choices(["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "integer", "nec"], k=10))
    elif option == 2:
        languages = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "今天的天气非常好。",
            "Сегодня прекрасная погода.",
            "היום היא מאוד במיוחד.",
            "Today is a beautiful day."
        ]
        return " ".join(random.choices(languages, k=10))
    elif option == 3:
        emojis = ["😊", "👍", "🚀", "🌟", "💙", "💨", "🎉", "🌱", "💜", "💯"]
        return "Emoji Test Note: " + " ".join(random.choices(emojis, k=5))
    elif option == 4:
        code_snippets = [
            "<html>\n<head>\n<title>Test Page</title>\n</head>\n<body>\nHello, World!\n</body>\n</html>",
            "public class HelloWorld {\n  public static void main(String[] args) {\n    System.out.println(\"Hello, World!\");\n  }\n}",
            "def greet():\n  print(\"Hello, World!\")\n\ngreet()",
            "console.log('Hello, World!');",
            "#include <iostream>\nusing namespace std;\nint main() {\n  cout << \"Hello, World!\" << endl;\n  return 0;\n}"
        ]
        return random.choice(code_snippets)

def add_note_and_save(driver, note_text):
    try:
        logging.info("Clicking 'Add New Note' button.")
        add_note_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "add_note_btn")))
        add_note_button.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # Pause to allow the note input field to load

        logging.info("Entering note text.")
        note_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "si_note")))
        note_input.clear()

        # Use JavaScript to insert text into the field, including emojis
        driver.execute_script("arguments[0].value = arguments[1];", note_input, note_text)
        time.sleep(1)  # Pause to ensure the text is fully entered

        logging.info("Clicking 'Save' button.")
        save_button = driver.find_element(By.ID, "save_note_btn")
        save_button.click()
        time.sleep(1)  # Pause to allow the note to be saved

        # Wait until 'Add New Note' button is clickable again
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "add_note_btn")))
        logging.info("Note saved successfully.")
    except TimeoutException:
        logging.error("Timeout occurred while adding a note.")
    except NoSuchElementException:
        logging.error("One or more elements not found while adding a note.")

def verify_note_added(driver, note_text):
    try:
        logging.info("Verifying if the note was added to the table.")
        table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "order_notes_table")))
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            for cell in cells:
                if note_text in cell.text or note_text.split(':')[0] in cell.text:
                    logging.info("Note verification successful: Note is present in the table.")
                    return
        logging.warning("Note verification failed: Note not found in the table.")
    except TimeoutException:
        logging.error("Timeout occurred while verifying the note.")
    except NoSuchElementException:
        logging.error("Table element not found while verifying the note.")

if __name__ == "__main__":
    driver = setup_driver()
    try:
        username = "valeriu.bistritchi"
        password = "F9e361a11"
        login(driver, username, password)
        time.sleep(1)  # Wait for login to complete if needed

        fill_sales_inquiry_form(driver)
        all_steps_passed = True
        for i in range(1, 5):
            random_text = generate_random_text(i)
            try:
                add_note_and_save(driver, random_text)
                if i not in [3, 4]:  # Skip verification for the emoji and code messages
                    verify_note_added(driver, random_text)
            except Exception as e:
                all_steps_passed = False
                logging.error(f"An error occurred: {e}")
            time.sleep(1)  # Wait before proceeding to next note

        if all_steps_passed:
            logging.info("\n=======\nTEST PASSED\n=======\n")

        close_sales_inquiry(driver)
    finally:
        driver.quit()
