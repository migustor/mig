"""
Page information for page 839 (Purchase-Order Details)
"""
from common.config.base_urls import PROJECT_BASE_URLS


def get_page_839_url(project_name, po_id):
    """
    Returns the URL for page 839 for a specific purchase order.

    Args:
        project_name: Name of the project (e.g., "sm_eu")
        po_id: Purchase-order ID to open

    Returns:
        str: URL for page 839 with the provided po_id,
             or None if base_url not found
    """
    base_url = PROJECT_BASE_URLS.get(project_name, "")
    if not base_url:
        return None

    return f"{base_url}index.cfm?page_id=839&po_id={po_id}"
