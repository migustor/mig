# common/pages/page_730/locators.py
from selenium.webdriver.common.by import By

LANGUAGE_SELECT = (By.NAME, "language_id")
LANGUAGE_LEVEL_SELECT = (By.NAME, "language_level_id")
SEARCH_BUTTON = (
    By.XPATH,
    '//button[@type="submit" and contains(.,"Search")]'
)
TABLE_CONTAINER = (
    By.CSS_SELECTOR,
    'div.panel.panel-default[data-grid-view-form-id="frm_search"]'
)

# Пример локатора для мультиселекта проектов (если он общий для 730)
# Иначе перенесите в другой locators.py
CANDIDATE_PROJECT = (By.ID, "candidate_project")
# 1) Заголовок колонки Status (th) - кликаем, чтобы отсортировать
STATUS_HEADER_TH = (
    By.XPATH,
    '//th[@data-sort-attribute="status_name"]'
)

# 2) Дропдаун "date_type"
DATE_TYPE_SELECT = (By.ID, "date_type")

# 3) Календарь (datepicker), кнопка "today" или класс "today day"
#    Чтобы открыть календарь, скорее всего, есть input/иконка.
#    Здесь локатор на сам элемент или на "td.today.day", если хотим кликнуть
TODAY_DAY_IN_CALENDAR = (
    By.CSS_SELECTOR,
    'td.today.day'  # или '.today.day'
)