import os
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    NOT_RUN = "Not Run"
    PASSED = "Passed"
    FAILED = "Failed"
    ERROR = "Error"

@dataclass
class TestResult:
    name: str
    status: TestStatus
    message: str = ""
    error: Exception = None

class ImageUploadTester:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.username = os.getenv('DEFAULT_USERNAME')
        self.password = os.getenv('DEFAULT_PASSWORD')
        
        # Test configuration
        self.valid_formats = ('.jpg', '.jpeg', '.png', '.bmp')
        self.file_paths = {}
        
        # Initialize test results tracking
        self.test_results: Dict[str, TestResult] = {
            'login': TestResult(name='Login Test', status=TestStatus.NOT_RUN),
            'attach_element': TestResult(name='Attachment Element Present', status=TestStatus.NOT_RUN),
            'images_only': TestResult(name='Images Only Validation', status=TestStatus.NOT_RUN),
            'image_upload': TestResult(name='Image Upload Test', status=TestStatus.NOT_RUN),
            'non_image_upload': TestResult(name='Non-Image Upload Test', status=TestStatus.NOT_RUN)
        }
        
        self.completed_tests: List[str] = []

    def setup_webdriver(self):
        """Initialize and configure WebDriver with proper waiting"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        # Uncomment the line below to run in headless mode (no GUI)
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        """Perform login with explicit waits"""
        try:
            logger.info("Starting login process...")
            self.driver.get('https://stage4.office.eminiasystem.com/sage/?logout')
            
            login_field = self.wait.until(EC.presence_of_element_located((By.ID, 'login_name')))
            password_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'password')))
            
            login_field.send_keys(self.username)
            password_field.send_keys(self.password)
            
            submit_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[@class="btn btn-info btn-lg" and text()="Submit"]')
                )
            )
            submit_button.click()
            
            # Verify login success
            self.wait.until(EC.url_changes('https://stage4.office.eminiasystem.com/sage/?logout'))
            
            self.test_results['login'].status = TestStatus.PASSED
            self.test_results['login'].message = "Successfully logged in"
            self.completed_tests.append('login')
            logger.info("Login successful")
            
        except Exception as e:
            self.test_results['login'].status = TestStatus.ERROR
            self.test_results['login'].message = f"Login failed: {str(e)}"
            self.test_results['login'].error = e
            logger.error(f"Login failed: {str(e)}")
            raise

    def generate_test_files(self):
        """Generate test files with proper cleanup handling"""
        logger.info("Creating test files...")
        test_files = {
            'images': ['jpg', 'png', 'jpeg', 'bmp'],
            'videos': ['mp4', 'avi', 'mov'],
            'documents': ['txt', 'csv', 'docx'],
            'audio': ['mp3', 'wav', 'aac']
        }
        
        try:
            for category, extensions in test_files.items():
                for ext in extensions:
                    file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + f'.{ext}'
                    file_path = os.path.abspath(file_name)
                    with open(file_path, 'w') as f:
                        f.write(f"Test content for {category} file")
                    self.file_paths[file_name] = file_path
                    logger.info(f"Created {category} file: {file_name}")
        except Exception as e:
            logger.error(f"Error creating test files: {str(e)}")
            self.cleanup()
            raise

    def verify_image_attachments(self):
        """Verify existing image attachments"""
        try:
            logger.info("Verifying existing image attachments...")
            
            # Test for attachment element presence
            try:
                attached_pictures = self.wait.until(
                    EC.presence_of_element_located((By.ID, 'attached_pictures'))
                )
                self.test_results['attach_element'].status = TestStatus.PASSED
                self.test_results['attach_element'].message = "Attachment element found"
                self.completed_tests.append('attach_element')
            except TimeoutException as e:
                self.test_results['attach_element'].status = TestStatus.FAILED
                self.test_results['attach_element'].message = "Attachment element not found"
                self.test_results['attach_element'].error = e
                raise
            
            # Test for images only
            image_links = attached_pictures.find_elements(By.TAG_NAME, 'a')
            invalid_links = []
            for link in image_links:
                href = link.get_attribute('href')
                if not href.lower().endswith(self.valid_formats):
                    invalid_links.append(href)
            
            if not invalid_links:
                self.test_results['images_only'].status = TestStatus.PASSED
                self.test_results['images_only'].message = "All attachments are valid images"
            else:
                self.test_results['images_only'].status = TestStatus.FAILED
                self.test_results['images_only'].message = f"Found invalid image links: {', '.join(invalid_links)}"
            
            self.completed_tests.append('images_only')
            
        except Exception as e:
            logger.error(f"Error verifying attachments: {str(e)}")
            if 'images_only' not in self.completed_tests:
                self.test_results['images_only'].status = TestStatus.ERROR
                self.test_results['images_only'].message = f"Error during verification: {str(e)}"
                self.test_results['images_only'].error = e
            raise

    def safe_upload_file(self, file_path):
        """Perform file upload using Selenium's send_keys method"""
        try:
            # Find the file input element (adjust the locator as needed)
            file_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
            )
            # If the input is hidden, make it visible
            self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
            # Send the file path to the input element
            file_input.send_keys(file_path)
            time.sleep(2)  # Wait for upload to complete
        except Exception as e:
            logger.error(f"Error during file upload: {str(e)}")
            raise

    def test_image_uploads(self):
        """Test valid image uploads"""
        try:
            success_count = 0
            image_files = [f for f in self.file_paths if f.endswith(self.valid_formats)]
            total_images = len(image_files)
            
            for file_name in image_files:
                try:
                    # Click the upload button if necessary
                    upload_button = self.wait.until(
                        EC.element_to_be_clickable((By.ID, 'pickup_address_link'))
                    )
                    upload_button.click()
                    # Upload the file
                    self.safe_upload_file(self.file_paths[file_name])
                    success_count += 1
                    logger.info(f"Uploaded image: {file_name}")
                except Exception as e:
                    logger.error(f"Failed to upload {file_name}: {str(e)}")
            
            if success_count == total_images:
                self.test_results['image_upload'].status = TestStatus.PASSED
                self.test_results['image_upload'].message = f"Successfully uploaded {success_count} images"
            else:
                self.test_results['image_upload'].status = TestStatus.FAILED
                self.test_results['image_upload'].message = f"Only {success_count}/{total_images} images uploaded successfully"
            
            self.completed_tests.append('image_upload')
            
        except Exception as e:
            self.test_results['image_upload'].status = TestStatus.ERROR
            self.test_results['image_upload'].message = f"Error during image uploads: {str(e)}"
            self.test_results['image_upload'].error = e
            raise

    def test_non_image_uploads(self):
        """Test invalid file upload rejection"""
        try:
            non_image_files = [f for f in self.file_paths if not f.endswith(self.valid_formats)]
            error_count = 0
            total_non_images = len(non_image_files)
            
            for file_name in non_image_files:
                try:
                    # Click the upload button if necessary
                    upload_button = self.wait.until(
                        EC.element_to_be_clickable((By.ID, 'pickup_address_link'))
                    )
                    upload_button.click()
                    # Attempt to upload the non-image file
                    self.safe_upload_file(self.file_paths[file_name])
                    
                    # Verify error message
                    error_message_element = self.wait.until(
                        EC.presence_of_element_located((By.ID, 'response_attached_picture_block'))
                    )
                    error_message = error_message_element.text
                    if "Wrong file format!" in error_message:
                        error_count += 1
                        logger.info(f"Non-image upload correctly rejected: {file_name}")
                    else:
                        logger.error(f"Non-image upload not rejected as expected: {file_name}")
                except Exception as e:
                    logger.error(f"Error testing non-image upload {file_name}: {str(e)}")
            
            if error_count == total_non_images:
                self.test_results['non_image_upload'].status = TestStatus.PASSED
                self.test_results['non_image_upload'].message = "All non-image uploads were properly rejected"
            else:
                self.test_results['non_image_upload'].status = TestStatus.FAILED
                self.test_results['non_image_upload'].message = f"Only {error_count}/{total_non_images} non-image uploads were rejected"
            
            self.completed_tests.append('non_image_upload')
            
        except Exception as e:
            self.test_results['non_image_upload'].status = TestStatus.ERROR
            self.test_results['non_image_upload'].message = f"Error during non-image upload tests: {str(e)}"
            self.test_results['non_image_upload'].error = e
            raise

    def run_tests(self):
        """Execute all tests with proper error handling"""
        try:
            self.setup_webdriver()
            self.login()
            
            # Navigate to test page
            self.driver.get('https://stage4.office.eminiasystem.com/eu/intranet/warehouse/receiving/review.cfm?receipt_id=32490')
            
            self.verify_image_attachments()
            self.generate_test_files()
            self.test_image_uploads()
            self.test_non_image_uploads()
            
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
            raise
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        
        # Delete test files
        for file_name, file_path in self.file_paths.items():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted file: {file_name}")
            except Exception as e:
                logger.error(f"Failed to delete {file_name}: {str(e)}")
        
        # Close browser
        if hasattr(self, 'driver'):
            self.driver.quit()

    def print_results(self):
        """Print detailed test results summary"""
        logger.info("\nTest Results Summary:")
        logger.info("=" * 50)
        
        # Calculate overall test status
        total_tests = len(self.test_results)
        completed_tests = len(self.completed_tests)
        passed_tests = sum(1 for result in self.test_results.values() if result.status == TestStatus.PASSED)
        
        logger.info(f"Tests Completed: {completed_tests}/{total_tests}")
        logger.info(f"Tests Passed: {passed_tests}/{total_tests}")
        logger.info("=" * 50)
        
        for test_name, result in self.test_results.items():
            logger.info(f"\nTest: {result.name}")
            logger.info(f"Status: {result.status.value}")
            if result.message:
                logger.info(f"Message: {result.message}")
            if result.error:
                logger.info(f"Error: {str(result.error)}")
            logger.info("-" * 30)

if __name__ == "__main__":
    tester = ImageUploadTester()
    try:
        tester.run_tests()
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
    finally:
        tester.print_results()
