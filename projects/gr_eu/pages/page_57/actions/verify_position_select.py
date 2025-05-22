import logging
from selenium.webdriver.support.ui import Select

logger = logging.getLogger(__name__)


def verify_position_select(driver,
                           select_el,
                           keyword: str,
                           expected_value: str):
    """
    Удостоверяется, что в переданном select уже выбрано
    значение expected_value (по value),
    а его текст содержит keyword.
    """
    sel = Select(select_el)
    option = sel.first_selected_option
    actual_value = option.get_attribute("value")

    assert actual_value == expected_value, (
        f'value mismatch: expected {expected_value}, got {actual_value}')

    assert keyword.lower() in option.text.lower(), (
        f'text mismatch: keyword «{keyword}» not in «{option.text}»')

    logger.info('[OK] Проверка выбранного значения селекта прошла успешно')
