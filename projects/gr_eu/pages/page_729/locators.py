# common/pages/page_729/locators.py

from selenium.webdriver.common.by import By

# Селект для статуса (name="status_id")
STATUS_ID_SELECT = (By.ID, "status_id")

# Селект для проектов на 729 (candidate_projects_1)
CANDIDATE_PROJECTS_1_SELECT = (By.ID, "candidate_projects_1")

# Кнопка "Save" (здесь ориентируемся на class="btn btn-primary" и текст "Save")
SAVE_BUTTON = (
    By.XPATH,
    '//button[@type="submit" and contains(text(),"Save")]'
)
ADD_NEW_POSITION_BTN = (By.ID, "add_new_position")        # кнопка “add new Position”
POSITIONS_CONTAINER  = (By.ID, "position_div")            # общий блок с селектами
POSITION_SELECTS     = (By.CSS_SELECTOR, "select[name='position_id']")