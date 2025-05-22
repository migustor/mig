"""
Page information for page 879 (Receipt Details)
"""
from common.config.base_urls import PROJECT_BASE_URLS


def get_page_879_url(project_name, receipt_id):
    """
    Returns the URL for page 879 for a specific goods receipt.

    Args:
        project_name: Name of the project (e.g., "sm_eu")
        receipt_id: ID of the receipt to open

    Returns:
        str: URL for page 879 with the provided receipt_id,
             or None if base_url not found
    """
    base_url = PROJECT_BASE_URLS.get(project_name, "")
    if not base_url:
        return None

    # warehouse_site_id is fixed at 4
    return f"{base_url}index.cfm?page_id=879&warehouse_site_id=4&receipt_id={receipt_id}"
