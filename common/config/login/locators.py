"""
Локаторы для страницы логина (ID: 1)
"""
from selenium.webdriver.common.by import By

# Основные элементы формы логина
LOGIN_FORM = {
    "username_field": (By.ID, "login_name"),
    "password_field": (By.ID, "password"),
    "submit_button": (By.XPATH, '//button[text()="Submit"]'),
    "remember_me_checkbox": (By.ID, "remember_me"),
    "forgot_password_link": (By.XPATH, "//a[contains(text(), 'Forgot Password')]")
}

# Элементы сообщений об ошибках
ERROR_ELEMENTS = {
    "general_error": (By.CLASS_NAME, "alert-danger"),
    "username_error": (By.ID, "login_name_error"),
    "password_error": (By.ID, "password_error"),
    "validation_error": (By.CSS_SELECTOR, "div.validation-error")
}
