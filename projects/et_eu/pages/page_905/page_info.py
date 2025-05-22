"""
Page information for page 905 (Sage)
"""
from common.config.base_urls import PROJECT_BASE_URLS

def get_page_905_url(project_name, sales_order_id):
    """
    Returns the URL for page 905 for the specified project and company.
    
    Args:
        project_name: Name of the project (e.g., "ra_eu", "sage")
        sales_order_id: ID of the company (e.g., 102337)
        
    Returns:
        str: URL for page 905 with the provided sales_order_id, or None if base_url not found
    """
    base_url = PROJECT_BASE_URLS.get(project_name, "")
    if not base_url:
        return None

    return f"{base_url}?page_id=905&sales_order_id={sales_order_id}"
 