"""
Action to verify lead column in the history table
"""
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# Import locators
from common.pages.page_714.locators import LEAD_HISTORY_ELEMENTS

def verify_lead_column(driver, timeouts=None):
    """
    Verifies lead ID column and extracts leads
    
    Args:
        driver: Selenium WebDriver
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result of the action with lead verification data
    """
    logger = logging.getLogger('test')
    logger.info("Verifying lead column in history table")
    
    # Use timeouts from parameter if provided, otherwise use defaults
    timeouts = timeouts or {}
    table_timeout = timeouts.get("verification", {}).get("table", 30)
    rows_timeout = timeouts.get("verification", {}).get("rows", 35)
    
    result = {
        "success": False,
        "column_found": True,
        "leads_found": [],
        "total_leads": 0,
        "valid_links": 0,
        "error": None
    }
    
    try:
        # Wait for lead history table
        logger.info("Waiting for history table element")
        WebDriverWait(driver, table_timeout).until(
            EC.presence_of_element_located(LEAD_HISTORY_ELEMENTS["history_table"])
        )
        
        # Get all rows from the table, excluding the header
        logger.info("Waiting for history table rows")
        rows = WebDriverWait(driver, rows_timeout).until(
            lambda d: d.find_elements(*LEAD_HISTORY_ELEMENTS["history_rows"])
        )
        
        if not rows:
            logger.warning("No lead rows found in table")
            result["error"] = "No lead rows found in table"
            return result
        
        # Limit to 5 rows for verification
        rows = rows[:5]
        result["total_leads"] = len(rows)
        
        # Process each row to extract lead IDs
        for row in rows:
            try:
                cells = row.find_elements(*LEAD_HISTORY_ELEMENTS["lead_cell"])
                if not cells or len(cells) == 0:
                    continue
                
                # Last cell should contain lead ID
                lead_cell = cells[-1]
                link = lead_cell.find_element(*LEAD_HISTORY_ELEMENTS["lead_link"])
                href = link.get_attribute("href")
                lead_id = link.text.strip()
                
                if "lead_id=" in href and lead_id.isdigit():
                    result["leads_found"].append({
                        "id": lead_id,
                        "link": href
                    })
                    result["valid_links"] += 1
                    logger.info(f"Found valid lead: {lead_id}")
                else:
                    logger.warning(f"Found invalid lead link or ID: {lead_id} - {href}")
            except StaleElementReferenceException:
                logger.warning("Stale element detected when processing lead row, skipping")
                continue
            except Exception as e:
                logger.warning(f"Error processing lead row: {str(e)}")
                continue
        
        # Determine success based on found valid leads
        if result["valid_links"] > 0:
            result["success"] = True
            logger.info(f"Successfully verified leads: {result['valid_links']} valid leads found")
        else:
            result["error"] = "No valid leads found"
            logger.error("No valid leads found in table")
        
        return result
        
    except TimeoutException as te:
        error_msg = f"Timeout during lead verification: {str(te)}"
        logger.error(error_msg)
        result["column_found"] = False
        result["error"] = error_msg
        return result
        
    except Exception as e:
        error_msg = f"Error during lead verification: {str(e)}"
        logger.error(error_msg)
        result["column_found"] = False
        result["error"] = error_msg
        return result