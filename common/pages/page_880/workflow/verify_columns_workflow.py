# verify_columns_workflow.py
import logging
import time
from selenium.common.exceptions import TimeoutException
from common.pages.page_880.page_info import get_orders_page_url
from common.pages.page_880.actions.verify_columns_visibility import verify_columns_visibility

def verify_columns_for_user(driver, project_name, user_type, timeout=15):
    """
    Workflow for checking column visibility and order types for a specific user.
    
    Args:
        driver: Selenium WebDriver
        project_name: Project name (e.g., "ra_eu")
        user_type: User type (e.g., "ecommerce_sales", "ecommerce_manager")
        timeout: Element wait timeout
        
    Returns:
        dict: Check result
    """
    logger = logging.getLogger('test')
    logger.info(f"Starting column check for user {user_type} in project {project_name}")
    
    result = {
        'success': True,
        'error': None,
        'steps': {},
        'user_type': user_type,
        'project': project_name
    }
    
    try:
        # Step 1: Open orders page
        logger.info(f"Opening orders page for project {project_name}")
        orders_url = get_orders_page_url(project_name)
        driver.get(orders_url)
        
        # Add page load wait
        logger.info("Waiting for page to load")
        time.sleep(3)
        
        # Step 2: Check column visibility and order types
        logger.info("Checking column visibility")
        columns_result = verify_columns_visibility(driver, user_type, timeout, project_name)
        result['steps']['columns_visibility'] = columns_result
        
        if not columns_result['success']:
            result['success'] = False
            result['error'] = columns_result['error']
            logger.warning(f"Column visibility check failed: {columns_result['error']}")
        else:
            logger.info("Column visibility check passed")
        
        return result
        
    except TimeoutException as te:
        error_msg = f"Timeout while checking columns for {user_type} in {project_name}: {str(te)}"
        logger.error(error_msg)
        result['success'] = False
        result['error'] = error_msg
        return result
    except Exception as e:
        error_msg = f"Error in column check workflow: {str(e)}"
        logger.error(error_msg)
        result['success'] = False
        result['error'] = error_msg
        return result