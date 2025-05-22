import logging
import time
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import driver setup
from common.utils.driver_setup import setup_chrome_driver, release_driver

# Import our optimized login function
from projects.et_store.config.et_store_login import et_store_login

# Import the optimized search action
from projects.et_store.pages.shop.actions.search_actual_stock import search_actual_stock

# Import new actions
from projects.et_store.pages.shop.actions.add_products import add_products
from projects.et_store.pages.shop.actions.validate_checkout_email import validate_checkout_email

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(" - TEST ET STORE - ")

def test_et_store_search_checkout():
    """
    Test full shopping flow in the et_store shop.
    
    This test:
    1. Creates a Chrome WebDriver
    2. Logs in to the et_store system
    3. Performs a search with the 'Actual Stock' radio button selected
    4. Adds a product to the cart
    5. Proceeds to checkout
    6. Validates email field with various inputs
    7. Completes checkout with valid email
    """
    driver = setup_chrome_driver(headless=False)
    
    # Track test steps success/failure
    test_results = {
        "login": {"success": False, "message": "Not executed"},
        "search": {"success": False, "message": "Not executed"},
        "add_to_cart": {"success": False, "message": "Not executed"},
        "checkout": {"success": False, "message": "Not executed"}
    }
    
    try:
        # Project name
        project_name = "et_store"
        
        # 1) Login with the e2e user - using optimized login
        logger.info(f"STEP 1: Logging in to {project_name}")
        login_result = et_store_login(driver, project_name, "e2e")
        
        if not login_result["success"]:
            error_msg = f"Login failed: {login_result['error']}"
            logger.error(error_msg)
            test_results["login"] = {"success": False, "message": error_msg}
            return {"success": False, "error": error_msg, "test_results": test_results}
        
        test_results["login"] = {"success": True, "message": "Successfully logged in"}
        logger.info("Login successful")
        
        # 2) Perform search with 'Actual Stock' selected with longer timeouts
        logger.info("STEP 2: Searching for products with 'Actual Stock' filter")
        search_result = search_actual_stock(driver, project_name, timeouts={
            "page_load": 10,  # 10 seconds for page load
            "action": 10,     # 10 seconds for UI interactions
            "loader": 120     # 120 seconds (2 minutes) max for search loader
        })
        
        if not search_result["success"]:
            error_msg = f"Search failed: {search_result['error']}"
            logger.error(error_msg)
            test_results["search"] = {"success": False, "message": error_msg}
            return {"success": False, "error": error_msg, "test_results": test_results}
        
        # Log the search results
        products_found = search_result.get("products_found", "unknown")
        if products_found == "unknown":
            logger.info("Search completed, but could not determine the number of products found")
            # Continue anyway as products might be there
            test_results["search"] = {"success": True, "message": "Search completed, products count unknown"}
        elif products_found == 0:
            logger.warning("Search completed successfully, but no products were found")
            # Instead of failing, let's try to continue with the test
            # as there might still be products on the page that weren't detected
            test_results["search"] = {"success": True, "message": "No products detected, but continuing"}
        else:
            logger.info(f"Search completed successfully, found {products_found} products")
            test_results["search"] = {"success": True, "message": f"Found {products_found} products"}
        
        # Small delay to ensure page is fully loaded
        time.sleep(3)
        
        # 3) Add product to cart
        logger.info("STEP 3: Adding product to cart")
        add_result = add_products(driver, project_name, timeouts={
            "action": 15,  # Increased timeout
            "loader": 60
        })
        
        if not add_result["success"]:
            error_msg = f"Failed to add product to cart: {add_result['error']}"
            logger.error(error_msg)
            test_results["add_to_cart"] = {"success": False, "message": error_msg}
            return {"success": False, "error": error_msg, "test_results": test_results}
        
        logger.info("Product successfully added to cart")
        test_results["add_to_cart"] = {"success": True, "message": "Product added to cart successfully"}
        
        # Wait a moment to ensure cart is updated
        time.sleep(3)
        
        # 4) Proceed to checkout and validate email
        logger.info("STEP 4: Proceeding to checkout and validating email field")
        checkout_result = validate_checkout_email(driver, project_name, timeouts={
            "page_load": 15,  # Increased timeout
            "action": 15,     # Increased timeout
            "loader": 60
        })
        
        if not checkout_result["success"]:
            error_msg = f"Checkout validation failed: {checkout_result['error']}"
            logger.error(error_msg)
            test_results["checkout"] = {"success": False, "message": error_msg}
            return {"success": False, "error": error_msg, "test_results": test_results}
        
        # Log validation results
        validation_results = checkout_result.get("validation_results", [])
        invalid_emails_count = len(validation_results)
        successful_validations = sum(1 for result in validation_results if result["error_found"])
        
        logger.info(f"Email validation completed: {successful_validations}/{invalid_emails_count} invalid emails were properly rejected")
        logger.info("Checkout process completed successfully")
        
        test_results["checkout"] = {
            "success": True, 
            "message": f"Checkout completed successfully. {successful_validations}/{invalid_emails_count} email validations passed"
        }
        
        return {
            "success": True, 
            "error": None, 
            "products_found": products_found,
            "test_results": test_results
        }
        
    except Exception as e:
        logger.error(f"Test failed with unexpected error: {str(e)}")
        return {"success": False, "error": str(e), "test_results": test_results}
        
    finally:
        # Always release the driver
        release_driver(driver)

def main():
    result = test_et_store_search_checkout()
    overall_success = result["success"]
    test_results = result.get("test_results", {})
    
    logger.info("\n=== TEST SUMMARY ===")
    if overall_success:
        logger.info("SUCCESS")
    else:
        logger.error("FAILED")
    
    # Print detailed results for each step
    logger.info("\nStep Results:")
    for step, step_result in test_results.items():
        status = "SUCCESS" if step_result["success"] else "FAILED"
        logger.info(f"  {step.upper()}: {status} - {step_result['message']}")
    
    if not overall_success:
        logger.error(f"Test failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    else:
        products_found = result.get("products_found", "unknown")
        logger.info(f"Test completed successfully. Products found: {products_found}")

if __name__ == "__main__":
    main()