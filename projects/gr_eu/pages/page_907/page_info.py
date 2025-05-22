# projects/gr_eu/pages/page_907/page_info.py
"""
Page information for page 907 (Sales Order tracking)
"""
from common.config.base_urls import PROJECT_BASE_URLS

def get_page_907_url(project_name="", order_type="so"):
    """
    Returns the URL for page 907 (Sales Order tracking) for the specified project
    
    Args:
        project_name: Name of the project (e.g., "gr_eu")
        order_type: Type of order (default: "so")
        
    Returns:
        str: URL for page 907
    """
    base_url = PROJECT_BASE_URLS.get(project_name)
    if not base_url:
        raise ValueError(f"Unknown project name: {project_name}")
        
    return f"{base_url}index.cfm?page_id=907&order_type={order_type}"