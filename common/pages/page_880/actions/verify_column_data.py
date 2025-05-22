# verify_column_data.py
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from common.pages.page_880.locators import OrdersPageLocators

def verify_column_data(driver, row_index=0, timeout=10):
    """
    Проверяет наличие данных в колонках 'Freight / Tax' и 'GP / GP%' для указанной строки.
    Также собирает информацию о типе заказа (Site) и Sales Rep.
    
    Args:
        driver: Selenium WebDriver
        row_index: Индекс строки для проверки (по умолчанию первая строка)
        timeout: Время ожидания загрузки элементов
        
    Returns:
        dict: Результат проверки в формате {'success': bool, 'error': str, 'data': dict}
    """
    logger = logging.getLogger('test')
    logger.info(f"Проверка данных в колонках для строки {row_index}")
    
    result = {
        'success': True,
        'error': None,
        'data': {
            'freight_tax_data': None,
            'gp_data': None,
            'site_type': None,
            'sales_rep': None,
            'order_id': None
        }
    }
    
    try:
        # Ожидаем загрузку таблицы
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(OrdersPageLocators.TABLE)
        )
        
        # Получаем все строки таблицы
        rows = driver.find_elements(*OrdersPageLocators.TABLE_ROWS)
        
        if row_index >= len(rows):
            error_msg = f"Строка с индексом {row_index} не найдена. Всего строк: {len(rows)}"
            logger.error(error_msg)
            result['success'] = False
            result['error'] = error_msg
            return result
        
        row = rows[row_index]
        
        # Получаем ID заказа (для логирования)
        try:
            order_link = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) a")
            result['data']['order_id'] = order_link.text.strip()
        except:
            result['data']['order_id'] = f"Row {row_index}"
        
        # Получаем тип заказа (Site)
        try:
            site_element = row.find_element(*OrdersPageLocators.SITE_INFO)
            result['data']['site_type'] = site_element.text.strip()
            logger.info(f"Тип заказа (Site): {result['data']['site_type']}")
        except:
            logger.info("Не удалось определить тип заказа (Site)")
        
        # Получаем Sales Rep
        try:
            sales_rep_element = row.find_element(*OrdersPageLocators.SALES_REP_INFO)
            result['data']['sales_rep'] = sales_rep_element.text.strip()
            logger.info(f"Sales Rep: {result['data']['sales_rep']}")
        except:
            logger.info("Не удалось определить Sales Rep")
        
        # Проверяем данные в колонке Freight / Tax
        try:
            freight_tax_cell = row.find_element(*OrdersPageLocators.FREIGHT_TAX_CELL)
            result['data']['freight_tax_data'] = freight_tax_cell.text.strip()
            logger.info(f"Данные в колонке 'Freight / Tax': {result['data']['freight_tax_data']}")
        except:
            logger.info("Не удалось получить данные из колонки 'Freight / Tax'")
        
        # Проверяем данные в колонке GP / GP%
        try:
            gp_cell = row.find_element(*OrdersPageLocators.GP_CELL)
            result['data']['gp_data'] = gp_cell.text.strip()
            logger.info(f"Данные в колонке 'GP / GP%': {result['data']['gp_data']}")
        except:
            logger.info("Не удалось получить данные из колонки 'GP / GP%'")
        
        return result
        
    except Exception as e:
        error_msg = f"Ошибка при проверке данных в колонках: {str(e)}"
        logger.error(error_msg)
        result['success'] = False
        result['error'] = error_msg
        return result