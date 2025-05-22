import os
import time
import json
import psutil
import logging
import platform
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# Define the diagnostic directory
DIAGNOSTIC_DIR = r"C:\Users\valeriu.bistritchi\Desktop\E2E_Testing"
os.makedirs(DIAGNOSTIC_DIR, exist_ok=True)

# Setup logging
log_file = os.path.join(DIAGNOSTIC_DIR, f"chrome_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# ChromeDriver path - keeping as requested
CHROME_DRIVER_PATH = r"F:\Users\java.test\.cache\selenium\chromedriver\win64\133.0.6943.141\chromedriver.exe"

# Test URL to verify browser works
TEST_URL = "https://www.google.com"

def save_system_info():
    """Collect and save system information for diagnostics"""
    try:
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "memory": {
                "total": psutil.virtual_memory().total // (1024 ** 2),  # MB
                "available": psutil.virtual_memory().available // (1024 ** 2)  # MB
            },
            "chrome_driver_path": CHROME_DRIVER_PATH,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Try to get Chrome version
        try:
            if platform.system() == 'Windows':
                cmd = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    import re
                    match = re.search(r'version\s+REG_SZ\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if match:
                        system_info["chrome_version"] = match.group(1)
        except Exception as e:
            system_info["chrome_version_error"] = str(e)
            
        # Save to file
        file_path = os.path.join(DIAGNOSTIC_DIR, f"system_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(file_path, 'w') as f:
            json.dump(system_info, f, indent=4)
            
        logging.info(f"System information saved to {file_path}")
        return system_info
    except Exception as e:
        logging.error(f"Failed to collect system information: {e}")
        return None

def take_screenshot(driver, name):
    """Take a screenshot if driver is initialized"""
    if driver:
        try:
            filename = os.path.join(DIAGNOSTIC_DIR, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            driver.save_screenshot(filename)
            logging.info(f"Screenshot saved to {filename}")
            return filename
        except Exception as e:
            logging.error(f"Failed to take screenshot: {e}")
    return None

def check_processes():
    """Check for Chrome and ChromeDriver processes"""
    chrome_count = 0
    chromedriver_count = 0
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'chrome' in proc.info['name'].lower():
                chrome_count += 1
            if 'chromedriver' in proc.info['name'].lower():
                chromedriver_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    logging.info(f"Found {chrome_count} Chrome processes and {chromedriver_count} ChromeDriver processes")
    return chrome_count, chromedriver_count

def kill_chrome_processes():
    """Kill all Chrome and ChromeDriver processes"""
    killed = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'chrome' in proc.info['name'].lower() or 'chromedriver' in proc.info['name'].lower():
                proc.kill()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    logging.info(f"Killed {killed} Chrome/ChromeDriver processes")
    return killed

def test_case_1(service):
    """Test Case 1: Default headless mode setup"""
    logging.info("=== Test Case 1: Default headless mode ===")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-gpu")
    
    return try_initialize_driver(service, options, "test_case_1")

def test_case_2(service):
    """Test Case 2: Headless=new option"""
    logging.info("=== Test Case 2: Headless=new ===")
    options = Options()
    options.add_argument("--headless=new")  # New headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    return try_initialize_driver(service, options, "test_case_2")

def test_case_3(service):
    """Test Case 3: Non-headless mode"""
    logging.info("=== Test Case 3: Non-headless mode ===")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    return try_initialize_driver(service, options, "test_case_3")

def test_case_4(service):
    """Test Case 4: Additional Chrome flags for stability"""
    logging.info("=== Test Case 4: Additional Chrome flags ===")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--enable-logging")
    options.add_argument("--v=1")
    
    return try_initialize_driver(service, options, "test_case_4")

def test_case_5(service):
    """Test Case 5: Using ChromeOptions.binary_location"""
    logging.info("=== Test Case 5: Using binary_location ===")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Try to find Chrome executable path
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    
    chrome_exe = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_exe = path
            break
    
    if chrome_exe:
        logging.info(f"Found Chrome executable at: {chrome_exe}")
        options.binary_location = chrome_exe
    else:
        logging.warning("Chrome executable not found in standard locations")
    
    return try_initialize_driver(service, options, "test_case_5")

def try_initialize_driver(service, options, test_name, max_attempts=3):
    """Try to initialize WebDriver with multiple attempts"""
    for attempt in range(1, max_attempts + 1):
        logging.info(f"Attempt {attempt} to initialize driver for {test_name}")
        
        # Check and report existing Chrome processes
        chrome_count, chromedriver_count = check_processes()
        
        # If retry and processes exist, try to kill them
        if attempt > 1 and (chrome_count > 0 or chromedriver_count > 0):
            kill_chrome_processes()
            time.sleep(2)  # Wait for processes to be fully terminated
        
        driver = None
        try:
            logging.info(f"Starting ChromeDriver with options: {options.arguments}")
            driver = webdriver.Chrome(service=service, options=options)
            logging.info(f"ChromeDriver started successfully for {test_name}")
            
            # Try to load a test URL
            logging.info(f"Navigating to {TEST_URL}")
            driver.get(TEST_URL)
            logging.info(f"Successfully loaded {TEST_URL}")
            
            # Get page title to verify browser is working
            title = driver.title
            logging.info(f"Page title: {title}")
            
            # Take a screenshot to verify page loaded
            take_screenshot(driver, f"{test_name}_success")
            
            return {
                "success": True,
                "driver": driver,
                "test_name": test_name
            }
        
        except Exception as e:
            if driver:
                try:
                    take_screenshot(driver, f"{test_name}_error")
                except:
                    pass
                
                try:
                    driver.quit()
                except:
                    pass
            
            error_details = str(e)
            logging.error(f"Failed to initialize driver for {test_name} on attempt {attempt}: {error_details}")
            
            # Save extra debug information
            debug_file = os.path.join(DIAGNOSTIC_DIR, f"{test_name}_error_{attempt}.txt")
            with open(debug_file, 'w') as f:
                f.write(f"Error details: {error_details}\n\n")
                f.write(f"Chrome options: {options.arguments}\n\n")
                
            # Wait before retry
            if attempt < max_attempts:
                wait_time = 5
                logging.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
    
    return {
        "success": False,
        "driver": None,
        "test_name": test_name,
        "error": "All attempts failed"
    }

def main():
    """Main function to run all test cases"""
    # Save system information
    system_info = save_system_info()
    logging.info(f"Starting diagnostic tests with system info: {system_info}")
    
    # Create service
    service = Service(executable_path=CHROME_DRIVER_PATH)
    
    # Start clean - kill any existing Chrome processes
    kill_chrome_processes()
    
    # Run test cases
    test_cases = [
        test_case_1,
        test_case_2,
        test_case_3,
        test_case_4,
        test_case_5
    ]
    
    results = []
    
    for test_func in test_cases:
        result = test_func(service)
        results.append(result)
        
        logging.info(f"Test {result['test_name']} result: {'Success' if result['success'] else 'Failed'}")
        
        # Clean up if driver was created
        if result['success'] and result['driver']:
            try:
                result['driver'].quit()
                logging.info(f"Driver closed for {result['test_name']}")
            except Exception as e:
                logging.error(f"Error closing driver for {result['test_name']}: {e}")
            
        # Kill any remaining processes before next test
        kill_chrome_processes()
        
        # Wait between tests
        time.sleep(3)
    
    # Final summary
    logging.info("=== Diagnostic Results Summary ===")
    successful_tests = [r['test_name'] for r in results if r['success']]
    failed_tests = [r['test_name'] for r in results if not r['success']]
    
    logging.info(f"Successful tests: {successful_tests or 'None'}")
    logging.info(f"Failed tests: {failed_tests or 'None'}")
    
    print("=== Diagnostic Complete ===")
    print(f"Tests passed: {len(successful_tests)}/{len(test_cases)}")
    print(f"Logs saved to: {log_file}")
    print(f"Check {DIAGNOSTIC_DIR} for full diagnostic information")

if __name__ == "__main__":
    main()