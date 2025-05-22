import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

CREATE_EMPLOYEE_LINK = (By.CSS_SELECTOR,
                        'a.btn.btn-primary[href*="page_id=57"][href*="phase=new"]')


def open_create_employee(driver, timeout: int = 15):
    """
    Нажимает синюю кнопку/ссылку «Create Employee» и ждёт,
    пока на форме появится первый селект позиции.
    """
    wait = WebDriverWait(driver, timeout)
    try:
        btn = wait.until(EC.element_to_be_clickable(CREATE_EMPLOYEE_LINK))
        btn.click()
        logger.info('Clicked [Create Employee]')

        # дожидаемся первого скрытого <select name="position_id">
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'select[name="position_id"]')))
        logger.info('Create-Employee form is ready')

    except TimeoutException:
        logger.error('Create-Employee button not found / not clickable')
        raise
