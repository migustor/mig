from common.config.base_urls import PROJECT_BASE_URLS

def get_page_864_url(project_name, document_id):
    """
    Returns the URL for page 864 (invoice document edit page)

    Args:
        project_name: Name of the project (e.g., "sm_eu")
        document_id: ID of the invoice document

    Returns:
        str: Full URL to open document in edit mode, or None if base_url not found
    """
    base_url = PROJECT_BASE_URLS.get(project_name, "")
    if not base_url:
        return None

    return f"{base_url}index.cfm?page_id=864&phase=edit&id={document_id}"
