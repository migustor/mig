# /common/pages/page_953/actions/verify_purchase_table_actions.py
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By

# Import locators
from common.pages.page_953.locators import REPORT_RESULTS

def verify_purchase_table_headers(driver, wait_timeout=10):
    """
    Verifies that the purchase history table has the expected headers
    
    Args:
        driver: Selenium WebDriver
        wait_timeout: Timeout for waiting elements
        
    Returns:
        dict: Result with keys 'success', 'message'
    """
    logger = logging.getLogger('test')
    
    try:
        logger.info("Verifying purchase history table headers")
        
        # Wait for table headers
        headers = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_all_elements_located(REPORT_RESULTS["table_headers"])
        )
        
        # Check header count
        if len(headers) != REPORT_RESULTS["expected_header_count"]:
            logger.error(f"Expected {REPORT_RESULTS['expected_header_count']} headers, but found {len(headers)}")
            return {
                "success": False,
                "message": f"Header count mismatch: expected {REPORT_RESULTS['expected_header_count']}, found {len(headers)}"
            }
        
        # Check header texts
        header_texts = [header.text.strip() for header in headers]
        logger.info(f"Found headers: {header_texts}")
        
        for i, expected_header in enumerate(REPORT_RESULTS["expected_headers"]):
            if i >= len(header_texts):
                logger.error(f"Missing header: {expected_header}")
                return {
                    "success": False,
                    "message": f"Missing header: {expected_header}"
                }
            
            # Special case for empty header (last column)
            if expected_header == "" and header_texts[i] == "":
                continue
                
            if expected_header not in header_texts[i]:
                logger.error(f"Header mismatch: expected '{expected_header}', found '{header_texts[i]}'")
                return {
                    "success": False,
                    "message": f"Header mismatch: expected '{expected_header}', found '{header_texts[i]}'"
                }
        
        logger.info("Table headers verified successfully")
        return {
            "success": True,
            "message": "Purchase history table headers match expected format"
        }
        
    except Exception as e:
        logger.error(f"Error verifying table headers: {str(e)}")
        return {
            "success": False,
            "message": f"Error verifying table headers: {str(e)}"
        }

def verify_purchase_table_data(driver, wait_timeout=10):
    """
    Verifies that the purchase history table contains data rows
    
    Args:
        driver: Selenium WebDriver
        wait_timeout: Timeout for waiting elements
        
    Returns:
        dict: Result with keys 'success', 'row_count', 'message'
    """
    logger = logging.getLogger('test')
    
    try:
        logger.info("Verifying purchase history table data")
        
        # Wait for data rows
        rows = WebDriverWait(driver, wait_timeout).until(
            EC.presence_of_all_elements_located(REPORT_RESULTS["items_rows"])
        )
        
        row_count = len(rows)
        
        # Check if we have data rows
        if row_count == 0:
            logger.warning("No data rows found in purchase history table")
            return {
                "success": False,
                "row_count": 0,
                "message": "No data rows found in purchase history table"
            }
        
        # Check if data rows have the expected columns
        for i, row in enumerate(rows[:min(5, row_count)]):  # Check max 5 rows for performance
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) != REPORT_RESULTS["expected_header_count"]:
                logger.error(f"Row {i+1} has {len(cells)} cells, expected {REPORT_RESULTS['expected_header_count']}")
                return {
                    "success": False,
                    "row_count": row_count,
                    "message": f"Row {i+1} has {len(cells)} cells, expected {REPORT_RESULTS['expected_header_count']}"
                }
        
        # Sample first row data for verification
        if row_count > 0:
            first_row = rows[0]
            cells = first_row.find_elements(By.TAG_NAME, "td")
            
            sample_data = {}
            for i, header in enumerate(REPORT_RESULTS["expected_headers"]):
                if header and i < len(cells):
                    sample_data[header] = cells[i].text.strip()
            
            logger.info(f"Sample data from first row: {sample_data}")
        
        logger.info(f"Purchase history table contains {row_count} data rows")
        return {
            "success": True,
            "row_count": row_count,
            "message": f"Purchase history table contains {row_count} data rows",
            "sample_data": sample_data if row_count > 0 else None
        }
        
    except Exception as e:
        logger.error(f"Error verifying table data: {str(e)}")
        return {
            "success": False,
            "row_count": 0,
            "message": f"Error verifying table data: {str(e)}"
        }

def export_purchase_history(driver, wait_timeout=10):
    """
    Clicks the Export button to download the purchase history
    
    Args:
        driver: Selenium WebDriver
        wait_timeout: Timeout for waiting elements
        
    Returns:
        dict: Result with keys 'success', 'message'
    """
    logger = logging.getLogger('test')
    
    try:
        logger.info("Attempting to export purchase history")
        
        # Find and click the Export button
        export_button = WebDriverWait(driver, wait_timeout).until(
            EC.element_to_be_clickable(REPORT_RESULTS["export_button"])
        )
        
        logger.info("Found Export button, clicking...")
        export_button.click()
        
        # Wait a moment for download to start
        time.sleep(2)
        
        logger.info("Export initiated successfully")
        return {
            "success": True,
            "message": "Purchase history export initiated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error exporting purchase history: {str(e)}")
        return {
            "success": False,
            "message": f"Error exporting purchase history: {str(e)}"
        }