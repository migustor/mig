# tests/multiple_projects/test_special_characters.py
import os
import time
import logging
import sys
import uuid
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Generate a unique test ID for this test run
TEST_ID = f"special_chars_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Import configuration
from common.config.special_chars_test.test_config import SPECIAL_SYMBOLS, TEST_DOMAINS, TEST_USER, TIMEOUTS

# Import workflow
from common.pages.page_903.workflow.test_domain_workflow import test_domain_workflow

# Import driver setup and error handling if available
try:
    from common.utils.driver_setup import setup_chrome_driver, release_driver
    from common.utils.error_handling import jenkins_aware
    USE_DRIVER_POOL = True
except ImportError:
    USE_DRIVER_POOL = False
    # Define a simple decorator to replace jenkins_aware if it's not available
    def jenkins_aware():
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def print_domain_summary(domain_results):
    """
    Print a summary of test results for a domain
    
    Args:
        domain_results: Results dictionary from test_domain_workflow
    """
    domain = domain_results["domain"]
    print(f"\n=== Test Summary for domain: {domain} ===")
    
    fields_info = domain_results["fields_tested"]
    
    if isinstance(fields_info, str):
        # This means we got a direct message like "No row found..."
        print(f"  {fields_info}")
        return
    
    for field_id, outcome in fields_info.items():
        accepted = outcome.get("accepted", [])
        rejected = outcome.get("rejected", [])
        print(f"  Field '{field_id}':")
        print(f"    Accepted: {accepted if accepted else 'None'}")
        print(f"    Rejected: {rejected if rejected else 'None'}")
    
    if "error" in domain_results and domain_results["error"]:
        print(f"  Error: {domain_results['error']}")

@jenkins_aware()
def run_test(driver=None):
    """
    Main test execution function
    
    Args:
        driver: Selenium WebDriver (optional, will create one if not provided)
        
    Returns:
        dict: Overall test results
    """
    logger.info(f"Starting test execution with ID: {TEST_ID}")
    
    # Track results for each domain
    results = {}
    
    # Flag to track if we created our own driver
    created_own_driver = False
    
    try:
        for domain_config in TEST_DOMAINS:
            domain = domain_config["domain"]
            doc_id = domain_config["doc_id"]
            
            logger.info(f"Testing domain {domain} with document ID {doc_id}")
            print(f"\n--- Starting test for: {domain} ---")
            
            # Create a new WebDriver instance for each domain
            # We always create a new driver for each domain to avoid state conflicts
            domain_driver = webdriver.Chrome()
            domain_driver.maximize_window()
            
            try:
                # Run test workflow for this domain
                domain_result = test_domain_workflow(
                    domain_driver,
                    domain=domain,
                    doc_id=doc_id,
                    symbols=SPECIAL_SYMBOLS,
                    username=TEST_USER["username"],
                    password=TEST_USER["password"],
                    timeouts=TIMEOUTS
                )
                
                # Store results
                results[domain] = domain_result
                
                # Print summary
                print_domain_summary(domain_result)
                
            except Exception as e:
                error_msg = f"Error testing domain {domain}: {str(e)}"
                logger.error(error_msg)
                results[domain] = {
                    "success": False,
                    "domain": domain,
                    "error": error_msg,
                    "fields_tested": {}
                }
                print(f"  Error: {error_msg}")
            finally:
                # Close browser for this domain
                domain_driver.quit()
                print(f"--- Finished test for: {domain} ---")
        
        # Print overall summary
        print("\n=========== OVERALL TEST SUMMARY ===========")
        success_count = sum(1 for r in results.values() if r.get("success", False))
        total_count = len(results)
        print(f"Domains tested: {total_count}")
        print(f"Successful tests: {success_count}")
        print(f"Failed tests: {total_count - success_count}")
        
        # Return overall results
        return {
            "success": success_count == total_count,
            "domains_tested": total_count,
            "successful_tests": success_count,
            "domain_results": results
        }
            
    except Exception as e:
        error_msg = f"Unexpected error during test execution: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

def main():
    """
    Main entry point
    """
    # Check if headless mode is requested
    headless_mode = os.environ.get('HEADLESS', 'False').lower() == 'true'
    
    if USE_DRIVER_POOL:
        # Use the centralized driver pool
        driver = setup_chrome_driver(headless=headless_mode, test_id=TEST_ID)
        try:
            # Run the test with the provided driver
            result = run_test(driver)
        finally:
            # Always release the driver
            release_driver(driver)
    else:
        # Run the test without using the driver pool
        result = run_test()
    
    # Exit with appropriate code
    if not result.get("success", False):
        sys.exit(1)

if __name__ == "__main__":
    main()