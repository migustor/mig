import logging
import re
import time
from datetime import datetime
from typing import Dict, Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException

from common.utils.driver_setup import setup_chrome_driver, release_driver

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('validation_test')

def retry_on_exception(retries: int = 3, delay: int = 2) -> Callable:
    """Decorator for retry logic with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Dict:
            last_exception = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1}/{retries} failed for {func.__name__}. Retrying in {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
            logger.error(f"All {retries} attempts failed for {func.__name__}: {str(last_exception)}")
            raise last_exception
        return wrapper
    return decorator

def wait_for_clickable_and_click(driver, locator, timeout: int = 15, retries: int = 3) -> bool:
    """Wait for element to be clickable and click it with retry logic"""
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
            try:
                element.click()
            except:
                driver.execute_script("arguments[0].click();", element)
            logger.info(f"Clicked element {locator}")
            return True
        except (ElementClickInterceptedException, StaleElementReferenceException) as e:
            if attempt == retries - 1:
                logger.error(f"Failed to click {locator} after {retries} attempts: {str(e)}")
                return False
            time.sleep(2 * (2 ** attempt))
    return False

class ValidationTest:
    def __init__(self):
        self.max_wait_time = 30
        self.retry_attempts = 3
        self.results = {
            "test_name": "VAT and IBAN Validation Test",
            "timestamp": datetime.now().isoformat(),
            "steps_results": {}
        }
        self.vat_validation_text = None
        self.vat_number = None
        self.iban_validation_text = None
        self.iban_number = None

    @retry_on_exception(retries=3, delay=2)
    def login_to_system(self, driver) -> Dict:
        """Login to eminia system"""
        try:
            logger.info("Navigating to login page")
            driver.get("https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=442")
            username_input = WebDriverWait(driver, self.max_wait_time).until(
                EC.presence_of_element_located((By.ID, "login_name"))
            )
            password_input = driver.find_element(By.ID, "password")
            username_input.clear()
            username_input.send_keys("user125900@mteam.test")
            password_input.clear()
            password_input.send_keys("12")

            submit_button = driver.find_element(By.XPATH, '//button[text()="Submit"]')
            submit_button.click()

            WebDriverWait(driver, 15).until(
                EC.invisibility_of_element_located((By.ID, "login_name"))
            )
            logger.info("Login successful")
            return {"success": True}
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return {"success": False, "error": str(e)}

    @retry_on_exception(retries=3, delay=2)
    def check_vat_button(self, driver) -> Dict:
        """Check VAT button and wait for validation text to appear"""
        try:
            logger.info("Looking for VAT check button")
            vat_button_locator = (By.ID, "check_vat")
            if wait_for_clickable_and_click(driver, vat_button_locator, self.max_wait_time, self.retry_attempts):
            # Wait for popup
                popup = WebDriverWait(driver, self.max_wait_time).until(
                    EC.presence_of_element_located((By.ID, "vat-popup"))
                )

            # Wait for VAT validation text to appear
                def vat_text_present(driver):
                    popup_text = popup.text
                    return any("VAT#:" in line for line in popup_text.splitlines())

                WebDriverWait(driver, 30).until(vat_text_present)
                logger.info("VAT validation text found")
                return {"success": True}

            return {"success": False, "error": "Failed to click VAT button"}
        except TimeoutException as e:
            logger.error(f"Timeout waiting for VAT validation text: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"VAT button check failed: {str(e)}")
            return {"success": False, "error": str(e)}

    @retry_on_exception(retries=3, delay=2)
    def validate_vat_popup(self, driver) -> Dict:
        """Validate VAT popup content and close it"""
        try:
            logger.info("Waiting for VAT popup")
            popup = WebDriverWait(driver, self.max_wait_time).until(
                EC.visibility_of_element_located((By.ID, "vat-popup"))
            )

        # Get popup text and find VAT line
            popup_text = popup.text
            vat_line = next((line.strip() for line in popup_text.splitlines()
                        if "VAT#:" in line), None)

            if vat_line:
                self.vat_validation_text = vat_line
            # Extract VAT number from the line if needed
                self.vat_number = vat_line.split("VAT#:")[1].strip().split()[0]
                logger.info(f"VAT LINE FOUND: {self.vat_validation_text}")
            else:
                logger.warning("VAT validation line not found")

        # Close the VAT popup
            close_button_locator = (By.ID, "cancel_popup_vat_check")
            if wait_for_clickable_and_click(driver, close_button_locator, timeout=10, retries=3):
                logger.info("VAT popup closed successfully")
            else:
                logger.warning("Failed to close VAT popup with standard click, trying JavaScript")
                close_button = driver.find_element(*close_button_locator)
                driver.execute_script("arguments[0].click();", close_button)
                logger.info("VAT popup closed via JavaScript")

            return {"success": True, "vat_number": self.vat_number} if self.vat_validation_text else {"success": False, "error": "VAT validation not found"}
        except TimeoutException:
            logger.error("VAT popup timeout")
            return {"success": False, "error": "Popup timeout"}
        except Exception as e:
            logger.error(f"VAT popup validation failed: {str(e)}")
            return {"success": False, "error": str(e)}

    @retry_on_exception(retries=3, delay=2)
    def check_iban_button(self, driver) -> Dict:
        """Check IBAN button, click it, then click info_icon, wait for data"""
        try:
            logger.info("Looking for IBAN check button")
            iban_button_locator = (By.ID, "iban_check")
            if not wait_for_clickable_and_click(driver, iban_button_locator, self.max_wait_time, self.retry_attempts):
                return {"success": False, "error": "Failed to click IBAN button"}

            logger.info("Waiting 10 seconds for info_icon to appear after IBAN check")
            time.sleep(10)  # Wait for the info_icon to appear

            # Click the info_icon button
            info_icon_locator = (By.CSS_SELECTOR, "img.info_icon")
            if wait_for_clickable_and_click(driver, info_icon_locator, timeout=10, retries=3):
                logger.info("Waiting 10 seconds for IBAN popup data to load after info_icon click")
                time.sleep(10)  # Wait for popup data to load
                return {"success": True}
            return {"success": False, "error": "Failed to click info_icon button"}
        except Exception as e:
            logger.error(f"IBAN button check failed: {str(e)}")
            return {"success": False, "error": str(e)}

    @retry_on_exception(retries=3, delay=2)
    def validate_iban_popup(self, driver) -> Dict:
        """Validate IBAN popup content"""
        try:
            logger.info("Waiting for IBAN popup")
            popup = WebDriverWait(driver, self.max_wait_time).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.dialog_box.ui-dialog-content"))
            )
            popup_text = popup.text
            # More general IBAN pattern: matches any IBAN followed by a validation message
            iban_pattern = r"IBAN\s+(\w+).*?(checksum\s+is\s+correct|valid)"  # \w+ matches any alphanumeric IBAN
            iban_match = re.search(iban_pattern, popup_text, re.IGNORECASE)

            if iban_match:
                self.iban_number = iban_match.group(1)
                self.iban_validation_text = f"IBAN {self.iban_number}: The IBAN is valid"
                logger.info(f"IBAN VALID: {self.iban_validation_text}")
                return {"success": True, "iban_number": self.iban_number}
            logger.warning("IBAN validation pattern not found")
            return {"success": False, "error": "IBAN validation not found"}
        except TimeoutException:
            logger.error("IBAN popup timeout")
            return {"success": False, "error": "Popup timeout"}
        except Exception as e:
            logger.error(f"IBAN popup validation failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def run_test(self):
        """Run the validation test"""
        logger.info("=== Starting VAT and IBAN Validation Test ===")
        driver = setup_chrome_driver(headless=False)

        try:
            # Login
            self.results["steps_results"]["login"] = self.login_to_system(driver)
            if not self.results["steps_results"]["login"]["success"]:
                logger.error("Test aborted: Login failed")
                return self.generate_test_summary()

            # Navigate to payment page
            driver.get("https://stage15.office.eminiasystem.com/sage/index.cfm?page_id=864&phase=edit&id=15133&payment_request_id=25115")

            # VAT validation
            self.results["steps_results"]["check_vat_button"] = self.check_vat_button(driver)
            if self.results["steps_results"]["check_vat_button"]["success"]:
                self.results["steps_results"]["validate_vat_popup"] = self.validate_vat_popup(driver)

            # IBAN validation (VAT popup should be closed by now)
            self.results["steps_results"]["check_iban_button"] = self.check_iban_button(driver)
            if self.results["steps_results"]["check_iban_button"]["success"]:
                self.results["steps_results"]["validate_iban_popup"] = self.validate_iban_popup(driver)

        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
        finally:
            driver.quit()

        return self.generate_test_summary()

    def generate_test_summary(self) -> str:
        """Generate test summary"""
        summary = f"Test: {self.results['test_name']}\nTimestamp: {self.results['timestamp']}\n\n"

        # Login Result
        summary += "=== Login ===\n"
        if self.results["steps_results"]["login"]["success"]:
            summary += "Status: SUCCESS\n"
        else:
            summary += f"Status: FAILED\nError: {self.results['steps_results']['login'].get('error', 'Unknown')}\n"

        # VAT Results
        summary += "\n=== VAT Validation ===\n"
        if self.vat_validation_text:
            summary += f"{self.vat_validation_text}\nStatus: VALID\n"
        else:
            summary += "Status: FAILED\n"
            if "validate_vat_popup" in self.results["steps_results"]:
                summary += f"Error: {self.results['steps_results']['validate_vat_popup'].get('error', 'Unknown')}\n"

        # IBAN Results
        summary += "\n=== IBAN Validation ===\n"
        if self.iban_validation_text:
            summary += f"{self.iban_validation_text}\nStatus: VALID\n"
        else:
            summary += "Status: FAILED\n"
            if "validate_iban_popup" in self.results["steps_results"]:
                summary += f"Error: {self.results['steps_results']['validate_iban_popup'].get('error', 'Unknown')}\n"

        logger.info("Test summary generated")
        return summary

if __name__ == "__main__":
    test = ValidationTest()
    summary = test.run_test()
    print("\n" + summary)
