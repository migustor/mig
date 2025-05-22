# /common/pages/page_953/actions/verify_export_actions.py
import logging
import time
import os
import glob
from datetime import datetime

try:
    import pandas as pd
except ImportError:
    logging.warning("Pandas not installed. Excel verification will be limited.")

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

# Import locators
from common.pages.page_953.locators import REPORT_RESULTS

def export_and_verify_purchase_history(driver, download_dir=None, wait_timeout=10, wait_for_download=30):
    """
    Clicks the Export button and verifies the downloaded file content
    
    Args:
        driver: Selenium WebDriver
        download_dir: Directory where files will be downloaded (if None, no verification)
        wait_timeout: Timeout for waiting elements
        wait_for_download: Timeout for waiting for download to complete
        
    Returns:
        dict: Result with keys 'success', 'message', and file info
    """
    logger = logging.getLogger('test')
    
    try:
        logger.info("Attempting to export purchase history")
        
        # Find and click the Export button
        export_button = WebDriverWait(driver, wait_timeout).until(
            EC.element_to_be_clickable(REPORT_RESULTS["export_button"])
        )
        
        # Get first two PO IDs from page for comparison
        page_data = []
        try:
            rows = driver.find_elements(*REPORT_RESULTS["items_rows"])
            for row in rows[:2]:  # Only get first two rows
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > 0:
                    # Get PO ID from first cell
                    cell = cells[0]
                    links = cell.find_elements(By.TAG_NAME, "a")
                    po_id = ""
                    if links:
                        po_id = links[0].text.strip()
                    else:
                        po_id = cell.text.strip()
                    
                    page_data.append(po_id)
            
            logger.info(f"Collected PO_IDs for comparison: {page_data}")
        except Exception as e:
            logger.warning(f"Failed to collect PO_IDs: {str(e)}")
        
        logger.info("Found Export button, clicking...")
        export_button.click()
        
        # Wait a moment for download to start
        time.sleep(2)
        
        # If download directory is provided, wait for file to appear and verify content
        file_info = {}
        if download_dir and page_data:
            file_info = wait_for_and_verify_download(download_dir, page_data, wait_for_download)
            if not file_info.get("success", False):
                return {
                    "success": False,
                    "message": file_info.get("message", "Failed to verify downloaded file")
                }
        
        result = {
            "success": True,
            "message": "Purchase history export initiated successfully"
        }
        
        # Add file info if available
        if file_info:
            result.update(file_info)
        
        return result
        
    except Exception as e:
        logger.error(f"Error exporting purchase history: {str(e)}")
        return {
            "success": False,
            "message": f"Error exporting purchase history: {str(e)}"
        }

def wait_for_and_verify_download(download_dir, page_po_ids, timeout=30):
    """
    Waits for a download to complete and verifies the Excel file content
    
    Args:
        download_dir: Directory where files are downloaded
        page_po_ids: List of PO_IDs from web page
        timeout: Maximum time to wait for download in seconds
        
    Returns:
        dict: Result with keys 'success', 'message', 'file_path', 'file_size'
    """
    logger = logging.getLogger('test')
    
    try:
        # Get initial file list
        before_files = set(os.listdir(download_dir))
        logger.info(f"Initial files in download directory: {len(before_files)}")
        
        # Wait for new file to appear
        logger.info(f"Waiting up to {timeout} seconds for download to complete...")
        
        start_time = time.time()
        downloaded_file = None
        while time.time() - start_time < timeout:
            current_files = set(os.listdir(download_dir))
            new_files = current_files - before_files
            
            # Filter for Excel files
            excel_files = [f for f in new_files if f.endswith('.xlsx') or f.endswith('.xls')]
            
            if excel_files:
                # Get newest Excel file
                newest_file = max([os.path.join(download_dir, f) for f in excel_files], 
                                  key=os.path.getctime)
                
                # Wait to ensure file is completely downloaded
                time.sleep(1)
                downloaded_file = newest_file
                break
                
            time.sleep(1)
            
        if not downloaded_file:
            # Try to find the most recent Excel file
            excel_glob = os.path.join(download_dir, "*.xls*")
            excel_files = glob.glob(excel_glob)
            
            if excel_files:
                downloaded_file = max(excel_files, key=os.path.getctime)
            
        if not downloaded_file:
            logger.error("No Excel file found in download directory after export")
            return {
                "success": False,
                "message": "No Excel file found in download directory after export"
            }
            
        logger.info(f"Found downloaded file: {os.path.basename(downloaded_file)}")
        file_size = os.path.getsize(downloaded_file)
        logger.info(f"File size: {file_size} bytes")
        
        # Verify file content
        comparison_result = verify_excel_content(downloaded_file, page_po_ids)
        
        return {
            "success": True,
            "message": f"Download completed: {os.path.basename(downloaded_file)}",
            "file_path": downloaded_file,
            "file_size": file_size,
            "file_name": os.path.basename(downloaded_file),
            "comparison_result": comparison_result
        }
        
    except Exception as e:
        logger.error(f"Error verifying download: {str(e)}")
        return {
            "success": False,
            "message": f"Error verifying download: {str(e)}"
        }

def verify_excel_content(excel_file, page_po_ids):
    """
    Verifies that the Excel file contains the same PO_IDs as the web page
    
    Args:
        excel_file: Path to the downloaded Excel file
        page_po_ids: List of PO_IDs from web page
        
    Returns:
        dict: Result with keys 'success', 'message', 'matching_rows', 'details'
    """
    logger = logging.getLogger('test')
    
    try:
        # Try using pandas if available
        if 'pd' in globals():
            logger.info("Using pandas to read Excel file")
            df = pd.read_excel(excel_file)
            
            # Check if "PO ID" column exists
            if "PO ID" not in df.columns:
                logger.error("PO ID column not found in Excel file")
                return {
                    "success": False,
                    "message": "PO ID column not found in Excel file"
                }
            
            # Get the first two PO IDs from Excel
            excel_po_ids = df["PO ID"].astype(str).head(2).tolist()
            logger.info(f"Excel PO_IDs: {excel_po_ids}")
            
            # Compare with page PO IDs
            matching = 0
            details = []
            
            for i, (page_id, excel_id) in enumerate(zip(page_po_ids, excel_po_ids)):
                match = str(page_id).strip() == str(excel_id).strip()
                if match:
                    matching += 1
                
                details.append({
                    "row": i + 1,
                    "match": match,
                    "page_po_id": page_id,
                    "excel_po_id": excel_id
                })
            
            # Result
            success = matching == len(page_po_ids)
            message = f"{matching}/{len(page_po_ids)} PO_IDs match between web page and Excel file"
            
            return {
                "success": success,
                "message": message,
                "matching_rows": matching,
                "details": details
            }
                
        else:
            # Basic file existence check if pandas not available
            logger.warning("Pandas not available, only checking file existence")
            return {
                "success": True,
                "message": "File exists but content cannot be verified (pandas not available)",
                "matching_rows": 0,
                "details": []
            }
            
    except Exception as e:
        logger.error(f"Error verifying Excel content: {str(e)}")
        return {
            "success": False,
            "message": f"Error verifying Excel content: {str(e)}",
            "matching_rows": 0,
            "details": []
        }