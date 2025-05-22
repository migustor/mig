"""
Действие для проверки баланса компании (Sales и Buying значения).
Поддерживает разные валюты: евро (€) и доллары ($).
"""
import logging
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from common.pages.page_830.locators import Page830Locators

def verify_sales_buying_values(driver, timeouts=None):
    """
    Проверяет и извлекает значения Sales и Buying на странице компании.
    Поддерживает разные валюты (€, $).
    
    Args:
        driver: Selenium WebDriver
        timeouts: Словарь с таймаутами для различных операций
        
    Returns:
        dict: Результат проверки с данными о балансе
    """
    logger = logging.getLogger('test')
    logger.info("Checking Sales and Buying values")
    
    timeouts = timeouts or {}
    action_timeout = timeouts.get("action", 15)
    
    try:
        # Ожидаем появления элемента Sales
        logger.info("Waiting for the Sales element...")
        sales_element = WebDriverWait(driver, action_timeout).until(
            EC.visibility_of_element_located(Page830Locators.SALES_VALUE)
        )
        
        # Ожидаем появления элемента Buying
        logger.info("Waiting for the Buying element...")
        buying_element = WebDriverWait(driver, action_timeout).until(
            EC.visibility_of_element_located(Page830Locators.BUYING_VALUE)
        )
        
        # Получаем текст из элементов
        sales_text = sales_element.text.strip()
        buying_text = buying_element.text.strip()
        
        logger.info(f"Found Sales text: {sales_text}")
        logger.info(f"Found Buying text: {buying_text}")
        
        # Извлекаем числовые значения с помощью регулярных выражений, поддерживающих разные валюты
        # Для Buying ищем как евро, так и доллары
        buying_value_match = re.search(r'Buying: [€$]([\d,\.]+)', buying_text)
        buying_value = buying_value_match.group(1) if buying_value_match else None
        
        # Для Sales, обрабатываем случай "Credit Limit:"
        sales_value = None
        if "Credit Limit:" in sales_text:
            # Когда "Credit Limit:" показан без значения, предполагаем 0
            sales_value = "0.00"
            logger.info("Found 'Credit Limit:' with no value, assuming Sales: 0.00")
        else:
            # Пробуем исходный шаблон с поддержкой разных валют
            sales_value_match = re.search(r'Sales: [€$]([\d,\.]+)', sales_text)
            sales_value = sales_value_match.group(1) if sales_value_match else None
        
        if sales_value is not None and buying_value is not None:
            logger.info(f"Successfully extracted values - Sales: {sales_value}, Buying: {buying_value}")
            
            # Преобразуем в float для потенциальных вычислений
            try:
                sales_float = float(sales_value.replace(',', ''))
                buying_float = float(buying_value.replace(',', ''))
                
                # Проверка на ненулевой баланс: если хотя бы одно значение не равно нулю
                has_non_zero_balance = (sales_float != 0 or buying_float != 0)
                logger.info(f"Non-zero balance check: {has_non_zero_balance}")
                
                return {
                    "success": True,
                    "error": None,
                    "sales_text": sales_text,
                    "buying_text": buying_text,
                    "sales_value": sales_value,
                    "buying_value": buying_value,
                    "sales_float": sales_float,
                    "buying_float": buying_float,
                    "has_non_zero_balance": has_non_zero_balance
                }
            except ValueError:
                logger.warning("Could not convert values to float")
                # Если не удалось преобразовать в float, проверяем строковое представление
                has_non_zero_balance = (sales_value != "0.00" or buying_value != "0.00")
                logger.info(f"Non-zero balance check (string comparison): {has_non_zero_balance}")
                
                return {
                    "success": True,
                    "error": None,
                    "sales_text": sales_text,
                    "buying_text": buying_text,
                    "sales_value": sales_value,
                    "buying_value": buying_value,
                    "has_non_zero_balance": has_non_zero_balance
                }
        else:
            error_msg = "Failed to extract numeric values from Sales and Buying text"
            logger.warning(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "sales_text": sales_text,
                "buying_text": buying_text
            }
            
    except TimeoutException as te:
        error_msg = f"Timeout waiting for Sales or Buying elements: {str(te)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        error_msg = f"Error verifying Sales and Buying values: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}