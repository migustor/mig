import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import CREDENTIALS, PROJECTS

def login(driver, project_name, user_type="user1"):
    """
    Выполняет вход в систему используя данные из конфигурации

    Args:
        driver: Selenium WebDriver
        project_name: Название проекта из конфигурации PROJECTS
        user_type: Ключ пользователя из конфигурации (по умолчанию "user1")

    Returns:
        bool: True если вход успешен, False в противном случае
    """
    if user_type not in CREDENTIALS:
        logging.error(f"User type '{user_type}' not found in credentials")
        return False

    if project_name not in PROJECTS:
        logging.error(f"Project '{project_name}' not found in projects configuration")
        return False

    username = CREDENTIALS[user_type]["username"]
    password = CREDENTIALS[user_type]["password"]
    login_url = PROJECTS[project_name]["login_url"]

    logging.info(f"Logging in as {username} to {project_name}")

    # Специальная обработка для проекта grafit
    if project_name == "grafit":
        driver.get(f"{login_url}index.cfm?page_id=730")
    else:
        driver.get(f"{login_url}index.cfm?page_id=442")

    try:
        username_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "login_name"))
        )
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "password"))
        )

        username_input.send_keys(username)
        password_input.send_keys(password)

        submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
        submit_button.click()

        logging.info(f"Login successful to {project_name}")
        return True

    except TimeoutException:
        logging.error(f"Timeout occurred while logging in to {project_name}")
        return False
