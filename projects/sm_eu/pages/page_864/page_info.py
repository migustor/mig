"""
Page information for page 864 (Document Management)
"""
from common.config.base_urls import PROJECT_BASE_URLS

def get_page_864_url(project_name, document_id):
    """
    Returns the URL for page 864 for a specific document
    
    Args:
        project_name: Name of the project (e.g., "sm_eu")
        document_id: ID of the document to open
        
    Returns:
        str: URL for page 864 with the provided document_id, or None if base_url not found
    """
    base_url = PROJECT_BASE_URLS.get(project_name, "")
    if not base_url:
        return None

    return f"{base_url}index.cfm?page_id=864&phase=edit&id={document_id}"

def get_page_864_main_url(project_name):
    """
    Returns the main URL for page 864 (search page)
    
    Args:
        project_name: Name of the project (e.g., "sm_eu")
        
    Returns:
        str: URL for page 864 main search page, or None if base_url not found
    """
    base_url = PROJECT_BASE_URLS.get(project_name, "")
    if not base_url:
        return None

    return f"{base_url}?page_id=864"