# common/pages/page_22/page_info.py
from common.config.base_urls import PROJECT_BASE_URLS

PAGE_ID = "22"

def get_page_22_url(project_name, item_id):
    """
    Returns the full URL for page with ID=22 with the specified item_id,
    based on the base URL for the project stored in PROJECT_BASE_URLS.
    
    Args:
        project_name (str): Project code (e.g., "ho_eu", "ra_eu")
        item_id (str): The specific item ID to include in the URL
        
    Returns:
        str: Full URL for page 22 with edit phase and item_id
    """
    base_url = PROJECT_BASE_URLS[project_name]
    return f"{base_url}index.cfm?page_id={PAGE_ID}&phase=edit&item_id={item_id}"