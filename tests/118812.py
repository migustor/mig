"""
Automated test to verify lead history across multiple systems
Uses a single browser session for all projects.
"""
import logging
import sys
import time
import os
from datetime import datetime
from typing import Dict, List
import uuid  

# Import functions for working with driver from settings
from common.utils.driver_setup import setup_chrome_driver, release_driver

# Import login and logout functions
from common.config.login.login_as_user import login_as_user
from common.config.logout.logout_from_system import logout_from_system

# Import workflow for lead verification
from common.pages.page_714.workflow.verify_leads_workflow import verify_leads_workflow

# Import page info for URL generation
from common.pages.page_714.page_info import get_page_714_url

# Import error handling decorator and retry mechanism
from common.utils.error_handling import jenkins_aware
from common.utils.retry_decorator import with_retry, retry_on_failure

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

TEST_ID = f"118812_{str(uuid.uuid4())[:8]}"
logger = logging.getLogger(TEST_ID)

# Timeout settings for different elements
TIMEOUTS = {
    "login": 20,
    "navigation": {
        "dropdown": 35,
        "history_button": 35,
        "history_table": 35,
        "page_load": 30
    },
    "verification": {
        "table": 30,
        "rows": 35,
        "cells": 30
    }
}

# Map of project codes to their item IDs for verification
PROJECT_ITEMS = {
    "ra_eu": "35644",
    "at_eu": "41800",
    "ag_eu": "65585",
    "sm_us": "7488",
    "sm_eu": "1426",
    "et_eu": "10354716",
    "ho_eu": "44779",
    "lt_eu": "194118",
    "dr_eu": "1257",
    "argon": "524",
    "aro_eu": "1"
}

# No need for project name mapping, we'll use the codes directly

@with_retry(max_attempts=3, retry_delay=10)
def verify_system(driver, project_code: str, user_type: str = "ml", **kwargs) -> Dict:
    """
    Verify leads for a specific project using the new structure
    With automatic retry capability
    
    Args:
        driver: Selenium WebDriver
        project_code: Project code (e.g. "ra_eu", "at_eu")
        user_type: User type for login
        **kwargs: Additional parameters
        
    Returns:
        dict: Result of system verification
    """
    system_result = {
        "name": project_code,
        "success": False,
        "leads": None
    }
    
    try:
        # Step 1: Login to the system
        logging.info(f"Starting login process for project {project_code}")
        login_result = login_as_user(driver, user_type=user_type, project_name=project_code, timeouts=TIMEOUTS)
        
        if not login_result["success"]:
            logging.error(f"Login error for {project_code}: {login_result['error']}")
            system_result["error"] = login_result["error"]
            return system_result
        
        logging.info(f"Login successful for {project_code}")
        
        # Step 2: Run lead verification workflow
        item_id = PROJECT_ITEMS.get(project_code)
        if not item_id:
            error_msg = f"No item ID configured for project {project_code}"
            logging.error(error_msg)
            system_result["error"] = error_msg
            return system_result
        
        url = get_page_714_url(project_code, item_id)
        
        # Run the complete workflow
        workflow_result = verify_leads_workflow(driver, url, TIMEOUTS)
        
        # Process workflow results
        if workflow_result["success"]:
            system_result["success"] = True
            system_result["leads"] = {
                "total_leads": workflow_result["total_leads"],
                "valid_links": workflow_result["valid_leads"],
                "leads_found": workflow_result["leads_found"]
            }
            logging.info(f"Successfully verified leads in {project_code}: {workflow_result['valid_leads']} valid leads found")
        else:
            system_result["error"] = workflow_result["error"]
            system_result["failed_step"] = workflow_result["failed_step"]
            logging.error(f"Workflow failed for {project_code} at step '{workflow_result['failed_step']}': {workflow_result['error']}")
    
    except Exception as e:
        error_msg = f"Error verifying system {project_code}: {str(e)}"
        logging.error(error_msg)
        system_result["error"] = error_msg
    
    finally:
        # Always attempt to logout before returning
        try:
            logout_from_system(driver, project_code)
        except Exception as e:
            logging.error(f"Error during logout from {project_code}: {str(e)}")
    
    return system_result

def test_multiple_projects(project_codes, user_type="ml"):
    """Run tests for multiple projects using a single browser session"""
    # Use headless mode setting from environment
    headless_mode = os.environ.get('HEADLESS', 'False').lower() == 'true'
    
    # Get driver from centralized pool - do this just once
    driver = setup_chrome_driver(headless=headless_mode, test_id=TEST_ID)
    
    # Track results
    results = []
    
    try:
        for project_code in project_codes:
            logging.info(f"\nChecking system: {project_code}")
            
            # Add kwargs for retry mechanism
            # Don't pass project_code twice, just pass additional args
            kwargs = {
                'user_type': user_type
            }
            
            try:
                result = verify_system(driver, project_code, **kwargs)
                results.append(result)
            except Exception as e:
                logging.error(f"Unexpected error testing {project_code}: {str(e)}")
                results.append({
                    "name": project_code,
                    "success": False,
                    "error": str(e)
                })
            
            # Add some separation between project tests
            print("\n" + "-"*50 + "\n")
            
    except Exception as e:
        logging.error(f"Process failed with unexpected error: {str(e)}")
        raise  # Re-raise for jenkins_aware decorator to handle
    finally:
        # Здесь мы теперь явно указываем quit=True для надежного закрытия
        release_driver(driver, quit=True)
        logger.info(f"Test run {TEST_ID} completed for all projects")
    
    return results

def generate_summary(results: List[Dict]) -> str:
    """Generate summary report for all systems"""
    summary = "\n=== SYSTEMS VERIFICATION SUMMARY ===\n"
    total_systems = len(results)
    successful_systems = sum(1 for r in results if r["success"])
    
    summary += f"Total Systems: {total_systems}\n"
    summary += f"Successful: {successful_systems}\n"
    summary += f"Failed: {total_systems - successful_systems}\n\n"
    
    for system in results:
        summary += f"\n{system['name']}:\n"
        if not system["success"]:
            summary += "[-] Verification Failed\n"
            if "error" in system:
                summary += f"    Error: {system['error']}\n"
            continue
            
        leads = system["leads"]
        if leads["total_leads"] == 0:
            summary += "[-] No leads found\n"
            continue
            
        # Determine status without percentages
        if leads["valid_links"] == leads["total_leads"]:
            status = "COMPLETE"
            icon = "[+]"
        elif leads["valid_links"] > 0:
            status = "PARTIAL"
            icon = "[!]"
        else:
            status = "FAILED"
            icon = "[-]"
        
        # Show count without percentage
        summary += f"{icon} Valid Leads: {leads['valid_links']}/{leads['total_leads']}\n"
        
        # Print each lead ID only once
        if leads["leads_found"]:
            # Add each lead only once
            summary += "    Lead IDs:\n"
            for lead in leads["leads_found"]:
                summary += f"    - {lead['id']}\n"
                
    summary += "\n=================\n"
    return summary

@jenkins_aware()
def main():
    # Define projects to test
    projects_to_test = [
        "ra_eu", "at_eu"
    ]
    
    # Run tests for all projects
    results = test_multiple_projects(projects_to_test, user_type="ml")
    
    # Generate and print summary
    summary = generate_summary(results)
    print(summary)
    
    # If any project failed verification, exit with error
    if any(not r["success"] for r in results):
        return {"success": False, "error": "One or more systems failed verification"}
    return {"success": True}

if __name__ == "__main__":
    main()