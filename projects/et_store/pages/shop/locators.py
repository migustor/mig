from selenium.webdriver.common.by import By

class EtStoreLocators:
    ACTUAL_STOCK = (By.XPATH, '//*[@id="stock-type-3"]')
    SEARCH = (By.XPATH, '//*[@id="direct-search"]/div[5]/button[2]')
    ADD_PRODUCT = (By.XPATH, '//*[@id="result"]/div[1]/div[1]/div/div[2]/div[2]/div[2]/button')
    CHECKOUT = (By.XPATH, '/html/body/header/div/div[2]/div/div[1]/span/a')
    EMAIL_FIELD = (By.XPATH, '//*[@id="customer_email"]')
    ERROR_MESSAGE = (By.XPATH, '//*[@id="customer_email-error"]')
    MY_CART = (By.XPATH, '//*[@id="headerNavbar"]/ul/li[2]/a')
    CLEAR_CART = (By.XPATH, '/html/body/div[5]/div/div[1]/div[1]/div[1]/div[2]/button[1]')