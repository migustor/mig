# test_columns_visibility.py
import logging
import time
import traceback
from common.utils.driver_setup import setup_chrome_driver, release_driver
from common.utils.retry_decorator import with_retry
from common.utils.error_handling import jenkins_aware
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system
from common.pages.page_880.workflow.verify_columns_workflow import verify_columns_for_user

@jenkins_aware()
@with_retry(max_attempts=2)
def test_columns_visibility(projects=None):
    """
    Test to verify the visibility and presence of data in the columns 'Freight / Tax' and 'GP / GP%'
    for different user types across multiple projects according to requirements:
    
    1) Columns "Freight/Tax, Total" should be visible for "E-commerce Sales"
    2) Column "GP/GP%" should be visible for "Manager of E-commerce Selling"
    3) E-commerce users should only see ecommerce SOs in the report
    
    Args:
        projects: List of project codes to test. If None, default projects will be used.
    """
    logger = logging.getLogger('test')
    logger.info("Starting column visibility test")
    
    # Set projects to test
    if projects is None:
        projects = ["ag_eu", "ra_eu", "et_eu", "sm_eu", "at_eu"]
    
    # Users for testing
    users_to_test = {
        'ecommerce_sales': "ecommerce_sales",      # E-commerce Sales
        'ecommerce_manager': "ecommerce_manager"   # Manager of E-commerce Selling
    }
    
    # Results by project and user
    results = {}
    overall_result = {
        'success': True,
        'error': None,
        'project_results': {}
    }
    
    # Create driver
    driver = setup_chrome_driver(headless=True)
    
    try:
        # Test each project
        for project_name in projects:
            logger.info(f"===== Testing project: {project_name} =====")
            results[project_name] = {}
            project_success = True
            project_failures = []
            
            # Test each user in this project
            for user_role, user_id in users_to_test.items():
                logger.info(f"Checking for user {user_role} ({user_id}) in project {project_name}")
                
                try:
                    # Login to the system
                    login_result = login_as_user(driver, project_name, user_id)
                    
                    if login_result['success']:
                        # Verify columns and order types
                        results[project_name][user_role] = verify_columns_for_user(driver, project_name, user_id)
                        # Logout after the test
                        logout_from_system(driver)
                    else:
                        error_msg = f"Login error: {login_result.get('error', 'Unknown login error')}"
                        logger.error(error_msg)
                        results[project_name][user_role] = {
                            'success': False,
                            'error': error_msg,
                            'user_type': user_id,
                            'project': project_name
                        }
                        project_success = False
                        project_failures.append(f"Failed to login as {user_id}: {error_msg}")
                    
                    # Small pause between tests
                    time.sleep(2)
                    
                except Exception as e:
                    error_msg = f"Error during test for user {user_id} in project {project_name}: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    results[project_name][user_role] = {
                        'success': False,
                        'error': error_msg,
                        'user_type': user_id,
                        'project': project_name
                    }
                    project_success = False
                    project_failures.append(error_msg)
                    
                    # Try to logout if we're still logged in
                    try:
                        logout_from_system(driver)
                    except:
                        pass
            
            # Analyze results for this project
            logger.info(f"Analyzing results for project {project_name}")
            
            # Verify E-commerce Sales - Freight/Tax and Total should be visible, but GP/GP% not necessarily
            if user_data := results[project_name].get('ecommerce_sales'):
                if user_data.get('success') and 'steps' in user_data and 'columns_visibility' in user_data['steps']:
                    columns_data = user_data['steps']['columns_visibility']['data']
                    has_freight_tax = columns_data.get('freight_tax_visible', False)
                    has_total = columns_data.get('total_visible', False)
                    has_gp = columns_data.get('gp_visible', False)
                    only_ecommerce = columns_data.get('ecommerce_orders_found', False) and not columns_data.get('non_ecommerce_orders_found', True)
                    ebay_count = columns_data.get('ebay_count', 0)
                    amazon_count = columns_data.get('amazon_count', 0)
                    
                    logger.info(f"E-commerce Sales in {project_name}: Freight/Tax: {has_freight_tax}, "
                               f"Total: {has_total}, GP/GP%: {has_gp}, Only ecommerce orders: {only_ecommerce}, "
                               f"eBay orders: {ebay_count}, Amazon orders: {amazon_count}")
                    
                    # Check required columns
                    if not has_freight_tax:
                        project_success = False
                        project_failures.append(
                            f"E-commerce Sales should see the Freight/Tax column in {project_name}"
                        )
                        
                    if not has_total:
                        project_success = False
                        project_failures.append(
                            f"E-commerce Sales should see the Total column in {project_name}"
                        )
                    
                    # Check order types (only ecommerce)
                    if not only_ecommerce:
                        project_success = False
                        project_failures.append(
                            f"E-commerce Sales should only see ecommerce orders in {project_name}"
                        )
                else:
                    project_success = False
                    error = user_data.get('error', 'Unknown error in test execution')
                    project_failures.append(f"Test failed for E-commerce Sales in {project_name}: {error}")
            
            # Verify Manager of E-commerce Selling - Freight/Tax, Total, and GP/GP% should be visible
            if user_data := results[project_name].get('ecommerce_manager'):
                if user_data.get('success') and 'steps' in user_data and 'columns_visibility' in user_data['steps']:
                    columns_data = user_data['steps']['columns_visibility']['data']
                    has_freight_tax = columns_data.get('freight_tax_visible', False)
                    has_total = columns_data.get('total_visible', False)
                    has_gp = columns_data.get('gp_visible', False)
                    only_ecommerce = columns_data.get('ecommerce_orders_found', False) and not columns_data.get('non_ecommerce_orders_found', True)
                    ebay_count = columns_data.get('ebay_count', 0)
                    amazon_count = columns_data.get('amazon_count', 0)
                    
                    logger.info(f"E-commerce Manager in {project_name}: Freight/Tax: {has_freight_tax}, "
                               f"Total: {has_total}, GP/GP%: {has_gp}, Only ecommerce orders: {only_ecommerce}, "
                               f"eBay orders: {ebay_count}, Amazon orders: {amazon_count}")
                    
                    # Check required columns
                    if not has_freight_tax:
                        project_success = False
                        project_failures.append(
                            f"E-commerce Manager should see the Freight/Tax column in {project_name}"
                        )
                        
                    if not has_total:
                        project_success = False
                        project_failures.append(
                            f"E-commerce Manager should see the Total column in {project_name}"
                        )
                    
                    if not has_gp:
                        project_success = False
                        project_failures.append(
                            f"E-commerce Manager should see the GP/GP% column in {project_name}"
                        )
                    
                    # Check order types (only ecommerce)
                    if not only_ecommerce:
                        project_success = False
                        project_failures.append(
                            f"E-commerce Manager should only see ecommerce orders in {project_name}"
                        )
                else:
                    project_success = False
                    error = user_data.get('error', 'Unknown error in test execution')
                    project_failures.append(f"Test failed for E-commerce Manager in {project_name}: {error}")
            
            # Save project results
            overall_result['project_results'][project_name] = {
                'success': project_success,
                'failures': project_failures
            }
            
            # Update overall success status
            if not project_success:
                overall_result['success'] = False
            
            logger.info(f"Project {project_name} test {'PASSED' if project_success else 'FAILED'}")
            if project_failures:
                logger.warning(f"Failures in {project_name}:\n- " + "\n- ".join(project_failures))
        
        # Compile overall error message if any project failed
        if not overall_result['success']:
            failure_messages = []
            for project, proj_result in overall_result['project_results'].items():
                if not proj_result['success']:
                    failure_messages.append(f"Failures in {project}:")
                    for failure in proj_result['failures']:
                        failure_messages.append(f"  - {failure}")
            
            overall_result['error'] = "\n".join(failure_messages)
        
        # Include full results
        overall_result['detailed_results'] = results
        
        return overall_result
            
    except Exception as e:
        error_msg = f"Error during test execution: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': error_msg,
            'detailed_results': results
        }
    finally:
        # Release driver
        release_driver(driver)

if __name__ == "__main__":
    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Project list to test
    projects_to_test = ["ag_eu", "ra_eu", "et_eu", "sm_eu", "at_eu"]
    
    # Run test
    result = test_columns_visibility(projects_to_test)
    
    # Print overall result
    if result['success']:
        print("All tests passed successfully!")
    else:
        print("Test failures detected:")
        print(result['error'])
    
    # Print individual project results
    print("\nProject Results:")
    for project, proj_result in result['project_results'].items():
        status = "PASSED" if proj_result['success'] else "FAILED"
        print(f"{project}: {status}")