"""
Page information for page 749 (Sage)
"""
from common.config.base_urls import PROJECT_BASE_URLS


def get_page_749_url(project_name):
    """
    Returns the URL for page 749 for the specified project.

    Args:
        project_name: Name of the project (e.g., "sm_eu")

    Returns:
        str: URL for page 749, or None if base_url not found
    """
    base_url = PROJECT_BASE_URLS.get(project_name, "")
    if not base_url:
        return None

    return f"{base_url}index.cfm?page_id=749"
