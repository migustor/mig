import logging
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


def _visible_container(driver):
    containers = driver.find_elements(
        By.CSS_SELECTOR, '.multiselect-container.dropdown-menu')
    return next((c for c in containers if c.is_displayed()), None)


def verify_positions_filtered(driver,
                              keyword: str,
                              timeout: int = 5):
    """
    Проверяет, что все видимые позиции в дроп-дауне содержат keyword.
    """
    container = _visible_container(driver)
    items = container.find_elements(By.CSS_SELECTOR,
                                    'li:not(.multiselect-item.filter):not(.multiselect-all) label')

    visible_items = [i for i in items if i.is_displayed()]
    assert visible_items, f'Нет видимых пунктов для «{keyword}»'

    mismatch = [
        i.text.strip() for i in visible_items
        if keyword.lower() not in i.text.lower()
    ]
    assert not mismatch, (f'Фильтрация неверна. '
                          f'Слово «{keyword}» отсутствует в: {mismatch}')

    logger.info(f'[OK] keyword «{keyword}» — проверка прошла '
                f'(видимых элементов: {len(visible_items)})')
