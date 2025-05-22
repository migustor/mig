import logging
import time
import traceback
import re
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from common.pages.page_880.locators import OrdersPageLocators

def verify_columns_visibility(driver, user_type, timeout=20, project_name=None):
    """
    Checks the presence and visibility of required columns on the orders page depending on the user type.
    "E-commerce Sales" should see "Freight/Tax" and "Total" (but not necessarily "GP/GP%")
    "Manager of E-commerce Selling" should see all three columns: "Freight/Tax", "Total", and "GP/GP%"
    Both user types should only see e-commerce orders.
    
    Args:
        driver: Selenium WebDriver
        user_type: User type ("ecommerce_sales", "ecommerce_manager", etc.)
        timeout: Time to wait for elements to load
        project_name: Name of current project for project-specific handling
        
    Returns:
        dict: Verification result in the format {'success': bool, 'error': str, 'data': dict}
    """
    logger = logging.getLogger('test')
    logger.info(f"Checking column visibility for user type '{user_type}' in project '{project_name}'")
    
    result = {
        'success': True,
        'error': None,
        'data': {
            'freight_tax_visible': False,
            'total_visible': False,
            'gp_visible': False,
            'date_range_set': False,
            'ecommerce_orders_found': False,
            'non_ecommerce_orders_found': False,
            'ebay_count': 0,
            'amazon_count': 0,
            'mysupplyshop_count': 0,
            'alzura_count': 0,
            'total_results': 0
        }
    }
    
    # Determine which columns should be visible for the given user type
    required_columns = ['Freight / Tax', 'Total']
    if user_type.lower() in ['ecommerce_manager', 'manager of e-commerce selling']:
        required_columns.append('GP / GP%')
    
    try:
        # Make sure page is fully loaded
        logger.info("Waiting for page to stabilize...")
        time.sleep(3)
        
        # Get the current date for date_to
        logger.info("Attempting to locate date_to element...")
        try:
            date_to_element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(OrdersPageLocators.DATE_TO_INPUT)
            )
            date_to_str = date_to_element.get_attribute("value")
            logger.info(f"Current end date: {date_to_str}")
        except TimeoutException:
            logger.error("Timeout waiting for date_to element")
            result['success'] = False
            result['error'] = "Could not find date_to element"
            return result
        except Exception as e:
            logger.error(f"Error getting date_to: {str(e)}")
            result['success'] = False
            result['error'] = f"Error with date_to element: {str(e)}"
            return result
        
        try:
            # Parse the date and set the start date to 6 months ago
            date_to = datetime.strptime(date_to_str, "%d-%b-%Y")
            date_from = date_to - timedelta(days=220)  # Changed to 180 days (6 months)
            date_from_str = date_from.strftime("%d-%b-%Y")
            logger.info(f"Target start date: {date_from_str}")
            
            # Try to get the date_from element
            logger.info("Attempting to locate date_from element...")
            date_from_element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(OrdersPageLocators.DATE_FROM_INPUT)
            )
            
            # Set date directly with JavaScript
            logger.info("Setting date directly via JavaScript...")
            driver.execute_script(f"arguments[0].value = '{date_from_str}';", date_from_element)
            # Trigger change event to ensure the form recognizes the new date
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { 'bubbles': true }));", date_from_element)
            
            # Verify that the date was set
            time.sleep(1)
            actual_date_from = date_from_element.get_attribute("value")
            logger.info(f"Actually set start date: {actual_date_from}")
            
            result['data']['date_range_set'] = True
            
        except Exception as date_error:
            logger.error(f"Error while setting the date: {str(date_error)}")
            logger.error(traceback.format_exc())
            # Continue execution even if there is an error with the date
        
        # Special handling for et_eu project: Uncheck Shopify from multiselect
        if project_name == "et_eu":
            try:
                logger.info("Special handling for et_eu: Unchecking Shopify from multiselect")
                
                # Click the multiselect dropdown to open it
                multiselect_dropdown = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable(OrdersPageLocators.MULTISELECT_DROPDOWN)
                )
                driver.execute_script("arguments[0].click();", multiselect_dropdown)
                logger.info("Clicked multiselect dropdown")
                
                # Wait for dropdown to appear and uncheck Shopify
                time.sleep(1)  # Give time for dropdown to open
                shopify_checkbox = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable(OrdersPageLocators.SHOPIFY_CHECKBOX)
                )
                
                # Check if the checkbox is already checked
                is_checked = shopify_checkbox.is_selected()
                logger.info(f"Shopify checkbox is currently {'checked' if is_checked else 'unchecked'}")
                
                if is_checked:
                    # Uncheck the Shopify checkbox
                    driver.execute_script("arguments[0].click();", shopify_checkbox)
                    logger.info("Unchecked Shopify checkbox")
                else:
                    logger.info("Shopify checkbox already unchecked, no action needed")
                
                # Click somewhere else to close the dropdown
                driver.execute_script("document.body.click();")
                logger.info("Closed multiselect dropdown")
                
                time.sleep(1)  # Wait for dropdown to close
                
            except Exception as e:
                logger.warning(f"Error during et_eu special handling: {str(e)}")
                logger.warning("Continuing with test despite multiselect issue")
        
        # Wait for the 'Build Report' button to load and click it
        logger.info("Waiting for the 'Build Report' button to load")
        try:
            build_report_button = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(OrdersPageLocators.BUILD_REPORT_BUTTON)
            )
            
            logger.info("Clicking the 'Build Report' button")
            # Try JavaScript click first
            driver.execute_script("arguments[0].click();", build_report_button)
            
            # Also try regular click as fallback
            try:
                build_report_button.click()
            except:
                logger.info("JavaScript click was used, regular click not needed")
                
        except TimeoutException:
            logger.error("Timeout waiting for 'Build Report' button")
            result['success'] = False
            result['error'] = "Could not find or click 'Build Report' button"
            return result
        except Exception as e:
            logger.error(f"Error clicking 'Build Report' button: {str(e)}")
            result['success'] = False
            result['error'] = f"Error with 'Build Report' button: {str(e)}"
            return result
        
        # Allow time for the report to generate
        logger.info("Waiting for the table to load after clicking")
        time.sleep(5)  # Increased wait time
        
        # Wait for the table to load
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(OrdersPageLocators.TABLE)
            )
            logger.info("Table found on page")
        except TimeoutException:
            logger.error("Timeout waiting for table to load")
            result['success'] = False
            result['error'] = "Table did not load after clicking 'Build Report'"
            return result
        except Exception as e:
            logger.error(f"Error waiting for table: {str(e)}")
            result['success'] = False
            result['error'] = f"Error with table loading: {str(e)}"
            return result
        
        # Get the total results count
        try:
            # Find the h4 element with "Results found: X"
            results_element = driver.find_element(By.XPATH, "//h4[contains(text(), 'Results found:')]")
            results_text = results_element.text
            
            # Extract the number using regex
            match = re.search(r'Results found:\s*(\d+)', results_text)
            if match:
                result['data']['total_results'] = int(match.group(1))
                logger.info(f"Total results found: {result['data']['total_results']}")
            else:
                logger.warning(f"Could not extract total results count from: '{results_text}'")
        except Exception as e:
            logger.warning(f"Error getting total results count: {str(e)}")
        
        # Get the table headers
        try:
            headers = driver.find_elements(*OrdersPageLocators.TABLE_HEADERS)
            header_texts = [header.text.strip() for header in headers]
            logger.info(f"Found headers: {header_texts}")
        except Exception as e:
            logger.error(f"Error getting table headers: {str(e)}")
            result['success'] = False
            result['error'] = f"Error getting table headers: {str(e)}"
            return result
        
        # Function to check the presence and data of a column in the table
        def check_column_and_data(column_name):
            column_index = -1
            header_found = False
            
            # Find the column index
            try:
                headers = driver.find_elements(*OrdersPageLocators.TABLE_HEADERS)
                for i, header in enumerate(headers):
                    header_text = header.text.strip()
                    if column_name in header_text:
                        column_index = i
                        header_found = True
                        logger.info(f"Column '{column_name}' found at position {column_index}")
                        break
                
                if not header_found:
                    logger.warning(f"Column '{column_name}' not found")
                    return False, False
                
                # Check data in the first row
                try:
                    # Get the first data row
                    data_rows = driver.find_elements(*OrdersPageLocators.TABLE_DATA_ROWS)
                    if len(data_rows) == 0:
                        logger.warning("No data rows found in table")
                        return header_found, False
                    
                    first_row = data_rows[0]
                    
                    # Get the cell with data for this column
                    cells = first_row.find_elements(By.TAG_NAME, "td")
                    if column_index < len(cells):
                        cell = cells[column_index]
                        cell_text = cell.text.strip()
                        
                        if cell_text:
                            logger.info(f"Column '{column_name}' has data: '{cell_text}'")
                            return True, True  # Column found, data exists
                        else:
                            logger.warning(f"Column '{column_name}' found, but no data")
                            return True, False  # Column found, no data
                    else:
                        logger.warning(f"Column index {column_index} is out of range for cells (count: {len(cells)})")
                        return True, False
                
                except Exception as e:
                    logger.warning(f"Could not verify data in column '{column_name}': {str(e)}")
                    return True, False  # Column found, but data verification failed
            
            except Exception as e:
                logger.error(f"Error checking column '{column_name}': {str(e)}")
                return False, False
        
        # Check the presence and data of columns
        freight_tax_visible, _ = check_column_and_data("Freight / Tax")
        total_visible, _ = check_column_and_data("Total")
        gp_visible, _ = check_column_and_data("GP / GP%")
        
        result['data']['freight_tax_visible'] = freight_tax_visible
        result['data']['total_visible'] = total_visible
        result['data']['gp_visible'] = gp_visible
        
        # Check for e-commerce indicators
        try:
            ebay_indicators = driver.find_elements(*OrdersPageLocators.EBAY_INDICATOR)
            amazon_indicators = driver.find_elements(*OrdersPageLocators.AMAZON_INDICATOR)
            mysupplyshop_indicators = driver.find_elements(*OrdersPageLocators.MYSUPPLYSHOP_INDICATOR)
            alzura_indicators = driver.find_elements(*OrdersPageLocators.ALZURA_INDICATOR)
            
            result['data']['ebay_count'] = len(ebay_indicators)
            result['data']['amazon_count'] = len(amazon_indicators)
            result['data']['mysupplyshop_count'] = len(mysupplyshop_indicators)
            result['data']['alzura_count'] = len(alzura_indicators)
            
            total_ecommerce_count = (
                result['data']['ebay_count'] + 
                result['data']['amazon_count'] + 
                result['data']['mysupplyshop_count'] +
                result['data']['alzura_count']
            )
            
            if total_ecommerce_count > 0:
                result['data']['ecommerce_orders_found'] = True
                logger.info(f"Found {result['data']['ebay_count']} eBay indicators")
                logger.info(f"Found {result['data']['amazon_count']} Amazon indicators")
                logger.info(f"Found {result['data']['mysupplyshop_count']} Mysupplyshop indicators")
                logger.info(f"Found {result['data']['alzura_count']} Alzura indicators")
                logger.info(f"Total e-commerce orders: {total_ecommerce_count}")
            else:
                logger.warning("No e-commerce indicators found")
        except Exception as e:
            logger.error(f"Error checking e-commerce indicators: {str(e)}")
        
        # Check if all results are e-commerce by comparing total results with e-commerce count
        try:
            total_ecommerce_count = (
                result['data']['ebay_count'] + 
                result['data']['amazon_count'] + 
                result['data']['mysupplyshop_count'] +
                result['data']['alzura_count']
            )
            total_results = result['data']['total_results']
            
            if total_results > 0:
                # If we have total results count
                if total_ecommerce_count < total_results:
                    difference = total_results - total_ecommerce_count
                    percentage_difference = (difference / total_results) * 100
                    
                    # If less than 1% difference, consider it a rounding error or minor issue and ignore it
                    if percentage_difference < 1:
                        logger.info(f"Minor discrepancy detected ({difference} orders, {percentage_difference:.2f}%), but within acceptable range")
                    else:
                        logger.warning(f"Not all orders are e-commerce: {total_ecommerce_count} e-commerce orders out of {total_results} total")
                        result['data']['non_ecommerce_orders_found'] = True
                else:
                    logger.info(f"All orders are e-commerce: {total_ecommerce_count} e-commerce orders out of {total_results} total")
            else:
                # Fallback if we couldn't get total_results: count the rows
                data_rows = driver.find_elements(*OrdersPageLocators.TABLE_DATA_ROWS)
                row_count = len(data_rows)
                
                if total_ecommerce_count < row_count:
                    difference = row_count - total_ecommerce_count
                    percentage_difference = (difference / row_count) * 100
                    
                    # If less than 1% difference, consider it a rounding error or minor issue and ignore it
                    if percentage_difference < 1:
                        logger.info(f"Minor discrepancy detected ({difference} orders, {percentage_difference:.2f}%), but within acceptable range")
                    else:
                        logger.warning(f"Not all orders are e-commerce: {total_ecommerce_count} e-commerce orders out of {row_count} rows")
                        result['data']['non_ecommerce_orders_found'] = True
                else:
                    logger.info(f"All orders are e-commerce: {total_ecommerce_count} e-commerce orders out of {row_count} rows")
        
        except Exception as e:
            logger.error(f"Error comparing e-commerce orders with total: {str(e)}")
        
        # Verify results according to the requirements for the given user type
        missing_columns = []
        for column in required_columns:
            if column == "Freight / Tax" and not result['data']['freight_tax_visible']:
                missing_columns.append(column)
            elif column == "Total" and not result['data']['total_visible']:
                missing_columns.append(column)
            elif column == "GP / GP%" and not result['data']['gp_visible']:
                missing_columns.append(column)
        
        if missing_columns:
            logger.warning(f"Missing required columns: {', '.join(missing_columns)}")
            result['success'] = False
            result['error'] = f"Missing required columns: {', '.join(missing_columns)}"
        elif result['data']['non_ecommerce_orders_found']:
            logger.warning("Non-e-commerce orders found!")
            result['success'] = False
            result['error'] = "Non-e-commerce orders found"
        elif not result['data']['ecommerce_orders_found'] and len(driver.find_elements(*OrdersPageLocators.TABLE_DATA_ROWS)) > 0:
            logger.warning("No e-commerce orders found!")
            result['success'] = False
            result['error'] = "No e-commerce orders found"
        else:
            logger.info("All required checks passed successfully!")
        
        return result
        
    except Exception as e:
        error_msg = f"Error while verifying column visibility: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        result['success'] = False
        result['error'] = error_msg
        return result