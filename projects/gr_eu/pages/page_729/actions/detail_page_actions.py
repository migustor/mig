# detail_page_actions.py
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def check_language_and_level(driver, desired_language="Romanian", desired_level="Default", timeout=15):
    """
    Ищет хотя бы один блок .language_selector, в котором:
      select[name="language_id"] = desired_language
      select[name="language_level_id"] = desired_level
    Если находит, тест считается пройденным;
    Если нет, бросает AssertionError.
    """
    wait = WebDriverWait(driver, timeout)
    
    # Ждём, пока хотя бы один блок появится (или используем find_elements напрямую)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.language_selector")))
    
    # Находим все блоки с классом language_selector:
    language_blocks = driver.find_elements(By.CSS_SELECTOR, "div.language_selector")
    if not language_blocks:
        raise AssertionError("На странице не найдено ни одного блока .language_selector")

    found_match = False

    for block in language_blocks:
        # Ищем селекты внутри этого блока
        lang_select_el = block.find_element(By.CSS_SELECTOR, 'select[name="language_id"]')
        level_select_el = block.find_element(By.CSS_SELECTOR, 'select[name="language_level_id"]')

        # Получаем выбранный в селекте язык и уровень
        actual_lang = Select(lang_select_el).first_selected_option.text.strip()
        actual_lvl = Select(level_select_el).first_selected_option.text.strip()

        if actual_lang == desired_language and actual_lvl == desired_level:
            # Нашли нужную комбинацию (Romanian + Default)
            found_match = True
            break

    assert found_match, (
        f"Не найден блок, где язык = '{desired_language}' и уровень = '{desired_level}'. "
        "Судя по всему, в каждом блоке выбраны другие значения."
    )

