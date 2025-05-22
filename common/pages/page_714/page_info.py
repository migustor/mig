"""
URL generation functions for lead history page (ID: 714)
"""
from common.config.base_urls import PROJECT_BASE_URLS

PAGE_ID = "714"

def get_page_714_url(project_name="ra_eu", item_id=None):
    """
    Returns full URL for the lead history page (ID=714),
    based on the project's base URL from PROJECT_BASE_URLS.
    
    Args:
        project_name (str): Project code (e.g., "ra_eu", "at_eu")
        item_id (str): Item ID to view history for
        
    Returns:
        str: Complete URL to the lead history page
    """
    base_url = PROJECT_BASE_URLS[project_name]
    url = f"{base_url}index.cfm?page_id={PAGE_ID}"
    
    if item_id:
        url += f"&item_id={item_id}"
    
    return url