# projects/gr_eu/pages/page_57/locators.py
from selenium.webdriver.common.by import By

# ссылка «Create Employee»
CREATE_EMPLOYEE_BTN = (
    By.XPATH,
    '//a[@class="btn btn-primary" and contains(@href,"phase=new")]'
)

# кнопка-«чип» multiselect-а «Position»
POSITION_DROPDOWN_BTN = (
    By.CSS_SELECTOR,
    'button.item_function_select.dropdown-toggle'
)

# ввод поисковой строки внутри выпавшего списка
POSITION_SEARCH_INPUT = (
    By.CSS_SELECTOR,
    'ul.multiselect-container input.multiselect-search'
)

# видимые (отфильтрованные) варианты позиций
POSITION_VISIBLE_ITEMS = (
    By.CSS_SELECTOR,
    'ul.multiselect-container li:not(.multiselect-filter):not(.multiselect-group)'
    ' label'
)
# кнопка «Add new Position»
ADD_NEW_POSITION_BTN = (By.ID, "add_new_position")

# базовый контейнер со всеми селектами позиций
POSITION_DIV        = (By.ID, "position_div")