import logging
import json
import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LayoutTester:
    def __init__(self):
        self.driver = None
        self.device_resolutions = {
            'Desktop 1920x1080': (1920, 1080),
            'Desktop 1366x768': (1366, 768),
            'Laptop 1280x800': (1280, 800),
        }
        self.current_page_state = None

    def setup_driver(self):
        """Setup and start the Chrome driver"""
        try:
            logging.info("Setting up Chrome driver")
            options = Options()
            options.add_argument('--start-maximized')
            # options.add_argument('--headless')  # Uncomment for headless mode

            # Initialize the driver
            self.driver = webdriver.Chrome(options=options)
            logging.info("Chrome driver successfully started")
            return True
        except Exception as e:
            logging.error(f"Error setting up driver: {str(e)}")
            return False

    def login(self, url, username, password):
        """Perform login to the site"""
        try:
            logging.info(f"Attempting login for user {username}")
            self.driver.get(url)
            time.sleep(2)  # Wait for the page to load

            # Locate and fill in the fields
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "login_name"))
            )
            password_input = self.driver.find_element(By.ID, "password")

            username_input.send_keys(username)
            password_input.send_keys(password)

            # Click the login button
            submit_button = self.driver.find_element(By.XPATH, '//button[text()="Submit"]')
            submit_button.click()

            time.sleep(2)  # Wait for login to complete
            logging.info("Login successful")
            return True
        except Exception as e:
            logging.error(f"Error during login: {str(e)}")
            return False

    def enter_data(self, document_number):
        """Enter the document number"""
        try:
            logging.info(f"Entering document number: {document_number}")
            # Wait for the input field to appear
            document_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "document_number"))
            )
            document_input.send_keys(document_number)

            # Wait for the button and click it
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "start_receiving"))
            )
            submit_button.click()

            time.sleep(2)  # Wait for processing
            logging.info("Document number entered successfully")
            return True
        except Exception as e:
            logging.error(f"Error entering document number: {str(e)}")
            return False

    def enter_part_number(self, part_number):
        """Enter the part number"""
        try:
            logging.info(f"Entering part number: {part_number}")
            # Wait for the input field to appear
            part_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "part_number"))
            )
            part_input.send_keys(part_number)

            # Wait for the button and click it
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "register_product"))
            )
            submit_button.click()

            time.sleep(2)  # Wait for processing
            logging.info("Part number entered successfully")
            return True
        except Exception as e:
            logging.error(f"Error entering part number: {str(e)}")
            return False

    def enter_barcodes(self):
        """Enter barcodes"""
        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            try:
                barcode = f"0X{random.randint(0, 9999):04}"
                logging.info(f"Attempting to enter barcode: {barcode}")

                # Wait for the input field to appear
                barcode_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "barcodes"))
                )
                barcode_input.send_keys(barcode)

                # Wait for the button and click it
                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "submit_btn"))
                )
                submit_button.click()

                time.sleep(2)  # Wait for processing

                # Check for errors
                error_elements = self.driver.find_elements(By.CLASS_NAME, "scan_barcode_error")
                if error_elements:
                    error_message = error_elements[0].text
                    if "already exists in the system" in error_message:
                        logging.warning(f"Error: {error_message}. Generating new barcode.")
                        attempt += 1
                        continue

                logging.info("Barcode entered successfully")
                self.save_page_state()
                return True

            except Exception as e:
                logging.error(f"Error entering barcode: {str(e)}")
                attempt += 1

        logging.error("Maximum number of barcode entry attempts exceeded")
        return False

    def save_page_state(self):
        """Save the state of the page after entering the barcode"""
        try:
            self.current_page_state = {
                'url': self.driver.current_url,
                'html': self.driver.page_source
            }
            logging.info("Page state saved")
        except Exception as e:
            logging.error(f"Error saving page state: {str(e)}")

    def restore_page_state(self):
        """Restore the state of the page"""
        try:
            if self.current_page_state:
                current_url = self.driver.current_url
                if current_url != self.current_page_state['url']:
                    self.driver.get(self.current_page_state['url'])
                time.sleep(1)  # Allow time for the page to load
                logging.info("Page state restored")
                return True
            return False
        except Exception as e:
            logging.error(f"Error restoring page state: {str(e)}")
            return False

    def get_element_layout_info(self):
        """Get information about the layout of elements and their styles"""
        try:
            elements_info = {}

            # Find all interactive elements
            elements = self.driver.find_elements(By.XPATH, "//input[not(@type='hidden')] | //button | //select")

            for element in elements:
                try:
                    element_id = element.get_attribute('id') or element.get_attribute('name') or 'unnamed'

                    # Get CSS properties of the element
                    css_properties = {
                        'position': element.value_of_css_property('position'),
                        'display': element.value_of_css_property('display'),
                        'float': element.value_of_css_property('float'),
                        'flex': element.value_of_css_property('flex'),
                        'grid': element.value_of_css_property('grid'),
                        'margin': element.value_of_css_property('margin'),
                        'padding': element.value_of_css_property('padding'),
                        'width': element.value_of_css_property('width'),
                        'max-width': element.value_of_css_property('max-width'),
                        'min-width': element.value_of_css_property('min-width'),
                    }

                    # Get relative position of the element
                    parent = element.find_element(By.XPATH, './..')
                    parent_id = parent.get_attribute('id') or parent.get_attribute('class') or 'unknown'

                    # Check if there are media queries for the element
                    responsive_styles = self.driver.execute_script("""
                        var styles = window.getComputedStyle(arguments[0]);
                        return {
                            isResponsive: styles.maxWidth.includes('%') ||
                                         styles.width.includes('%') ||
                                         styles.flex !== 'none' ||
                                         styles.display === 'flex' ||
                                         styles.display === 'grid'
                        };
                    """, element)

                    elements_info[element_id] = {
                        'tag_name': element.tag_name,
                        'parent_element': parent_id,
                        'css_properties': css_properties,
                        'is_responsive': responsive_styles['isResponsive'],
                        'viewport_visibility': self.is_element_in_viewport(element)
                    }

                except Exception as e:
                    logging.warning(f"Failed to get information for element: {str(e)}")
                    continue

            return elements_info

        except Exception as e:
            logging.error(f"Error getting layout information: {str(e)}")
            return None

    def is_element_in_viewport(self, element):
        """Check if the element is visible in the viewport"""
        return self.driver.execute_script("""
            var rect = arguments[0].getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        """, element)

    def analyze_layout_changes(self, baseline_info, current_info):
        """Analyze layout changes between different resolutions"""
        changes = {
            'responsive_elements': [],
            'static_elements': [],
            'layout_shifts': [],
            'visibility_changes': []
        }

        for element_id, current_data in current_info.items():
            if element_id in baseline_info:
                baseline_data = baseline_info[element_id]

                # Check CSS property changes
                css_changes = []
                for prop, value in current_data['css_properties'].items():
                    if baseline_data['css_properties'][prop] != value:
                        css_changes.append({
                            'property': prop,
                            'from': baseline_data['css_properties'][prop],
                            'to': value
                        })

                # Determine type of element (responsive/static)
                if current_data['is_responsive']:
                    changes['responsive_elements'].append({
                        'element_id': element_id,
                        'css_changes': css_changes
                    })
                else:
                    changes['static_elements'].append({
                        'element_id': element_id,
                        'css_changes': css_changes
                    })

                # Check for parent element changes
                if baseline_data['parent_element'] != current_data['parent_element']:
                    changes['layout_shifts'].append({
                        'element_id': element_id,
                        'from_parent': baseline_data['parent_element'],
                        'to_parent': current_data['parent_element']
                    })

                # Check for visibility changes
                if baseline_data['viewport_visibility'] != current_data['viewport_visibility']:
                    changes['visibility_changes'].append({
                        'element_id': element_id,
                        'was_visible': baseline_data['viewport_visibility'],
                        'is_visible': current_data['viewport_visibility']
                    })

        return changes

    def check_layout_adaptation(self):
        """Check layout responsiveness"""
        try:
            logging.info("Starting layout responsiveness check")
            results = {
                'summary': {
                    'is_responsive': False,
                    'responsive_elements_count': 0,
                    'static_elements_count': 0,
                    'layout_issues': []
                },
                'details': {}
            }

            # Set baseline resolution
            baseline_resolution = 'Desktop 1920x1080'
            self.driver.set_window_size(*self.device_resolutions[baseline_resolution])
            time.sleep(2)
            baseline_info = self.get_element_layout_info()

            # Check each resolution
            for device_name, resolution in self.device_resolutions.items():
                if device_name == baseline_resolution:
                    continue

                logging.info(f"Checking resolution: {device_name} ({resolution[0]}x{resolution[1]})")
                self.driver.set_window_size(resolution[0], resolution[1])
                time.sleep(3)

                current_info = self.get_element_layout_info()
                layout_changes = self.analyze_layout_changes(baseline_info, current_info)

                results['details'][device_name] = layout_changes

                # Update overall statistics
                results['summary']['responsive_elements_count'] = len(layout_changes['responsive_elements'])
                results['summary']['static_elements_count'] = len(layout_changes['static_elements'])

                # Check for layout issues
                if layout_changes['layout_shifts']:
                    results['summary']['layout_issues'].append({
                        'device': device_name,
                        'issue': 'Layout structure changes detected',
                        'affected_elements': len(layout_changes['layout_shifts'])
                    })

                if layout_changes['visibility_changes']:
                    results['summary']['layout_issues'].append({
                        'device': device_name,
                        'issue': 'Visibility issues detected',
                        'affected_elements': len(layout_changes['visibility_changes'])
                    })

            # Determine overall page responsiveness
            results['summary']['is_responsive'] = (
                results['summary']['responsive_elements_count'] >
                results['summary']['static_elements_count']
            )

            return results

        except Exception as e:
            logging.error(f"Error during layout responsiveness check: {str(e)}")
            return None

    def generate_test_summary(self, results):
        """Generate final report based on the test results"""
        logging.info("Generating test summary.")
        summary = "== Test Summary ==\n"

        # Overall summary
        summary += f"Responsive elements: {results['summary']['responsive_elements_count']}\n"
        summary += f"Static elements: {results['summary']['static_elements_count']}\n"
        if results['summary']['layout_issues']:
            summary += "Layout issues detected:\n"
            for issue in results['summary']['layout_issues']:
                summary += f"  Device: {issue['device']}, Issue: {issue['issue']}, Affected Elements: {issue['affected_elements']}\n"
        else:
            summary += "No layout issues found.\n"

        # Differences between different resolutions
        for device_name, changes in results['details'].items():
            summary += f"\nDevice: {device_name}\n"

            if changes['layout_shifts']:
                summary += "Layout shifts detected:\n"
                for shift in changes['layout_shifts']:
                    summary += f"  Element ID: {shift['element_id']}, Moved from: {shift['from_parent']} to: {shift['to_parent']}\n"

            if changes['visibility_changes']:
                summary += "Visibility issues detected:\n"
                for visibility in changes['visibility_changes']:
                    summary += f"  Element ID: {visibility['element_id']}, Was Visible: {visibility['was_visible']}, Is Visible: {visibility['is_visible']}\n"

            if not changes['layout_shifts'] and not changes['visibility_changes']:
                summary += "No layout issues detected.\n"

        logging.info("Test summary generated.")
        return summary

    def run_test(self, url, username, password, document_number, part_number):
        """Main test execution method"""
        try:
            # Initialize the driver
            if not self.setup_driver():
                return False

            # Login to the site
            if not self.login(url, username, password):
                return False

            # Enter data
            if not self.enter_data(document_number):
                return False

            # Enter part number
            if not self.enter_part_number(part_number):
                return False

            # Enter barcode
            if not self.enter_barcodes():
                return False

            # Check layout responsiveness
            results = self.check_layout_adaptation()

            # Generate final report
            if results:
                summary = self.generate_test_summary(results)
                print(summary)

            return True

        except Exception as e:
            logging.error(f"Error during test execution: {str(e)}")
            return False

        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Chrome driver closed")

# Entry point
if __name__ == "__main__":
    try:
        tester = LayoutTester()
        success = tester.run_test(
            url="https://stage28.office.eminiasystem.com/euwhse/receive/enter_po_number.cfm",
            username="user3364@mteam.test",
            password="12",
            document_number="132341",
            part_number="31402415"
        )

        if not success:
            logging.error("Test completed with errors")

    except KeyboardInterrupt:
        logging.info("Test interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
