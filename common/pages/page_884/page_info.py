"""
Page information for page 884
"""
from common.config.base_urls import PROJECT_BASE_URLS

def get_page_884_url(project_name=""):
    """
    Returns the URL for page 884 for the specified project
    
    Args:
        project_name: Name of the project (e.g., "ag_eu")
        
    Returns:
        str: URL for page 884
    """
    base_url = PROJECT_BASE_URLS.get(project_name)
    if not base_url:
        raise ValueError(f"Unknown project name: {project_name}")
        
    return f"{base_url}index.cfm?page_id=884"