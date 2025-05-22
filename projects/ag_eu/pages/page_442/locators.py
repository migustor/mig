from selenium.webdriver.common.by import By

class CompanyCreationLocators:
    COMPANY_NAME_FIELD = (By.ID, "company_name")
    COUNTRY_INFO_DROPDOWN = (By.ID, "country_info")  
    SEGMENTATION_DROPDOWN = (By.ID, "segmentation_id")
    ADDRESS_LINE_ONE_FIELD = (By.ID, "address_line_one")
    CITY_FIELD = (By.ID, "city")
    ADDRESS_POSTAL_CODE_FIELD = (By.ID, "address_postal_code")
    CONTACT_PHONE_NUMBER_FIELD = (By.NAME, "contact_phone_number_1")
    CONTACT_EMAIL_FIELD = (By.NAME, "contact_email") 
    VAT_NUMBER_FIELD = (By.ID, "vat_number") 
    CREATE_COMPANY_BUTTON = (By.XPATH, '//button[text()="Create Company"]')