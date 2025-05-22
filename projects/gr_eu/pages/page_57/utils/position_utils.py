# projects/gr_eu/pages/page_57/utils/position_utils.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def open_multiselect_of(driver, select_el, timeout=10):
    """
    Получает <select>, находит рядом кнопку-тогглер multiselect
    и кликает по ней, надёжно дожидаясь открытия дроп-дауна.
    """
    toggle_btn = select_el.find_element(By.XPATH, 'following-sibling::div/button')

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});", toggle_btn
    )
    toggle_btn.click()

    # ждём, пока появится ul.dropdown-menu, привязанный к кнопке
    WebDriverWait(driver, timeout).until(
        EC.visibility_of(toggle_btn.find_element(By.XPATH, 'following-sibling::ul'))
    )
