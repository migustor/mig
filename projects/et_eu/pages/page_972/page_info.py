# /common/pages/page_972/page_info.py
"""
Page info for page 972
"""

from common.config.base_urls import PROJECT_BASE_URLS

def get_page_972_url(project_name):
    """
    Constructs the base URL for page 972 (Presale search page).

    :param project_name: The project code (e.g., 'sm_eu').
    :return: Constructed URL string or None if project_name not in base URLs.
    """
    base_url = PROJECT_BASE_URLS.get(project_name, "")
    if not base_url:
        return None

    return f"{base_url}index.cfm?page_id=972"

def get_presale_creation_url(project_name, lead_id):
    """
    Constructs the URL for creating a new presale with a given lead_id.

    :param project_name: The project code (e.g., 'sm_eu').
    :param lead_id: The lead ID captured from page 634 action.
    :return: Constructed URL string or None if project_name not in base URLs.
    """
    base_url = PROJECT_BASE_URLS.get(project_name, "")
    if not base_url:
        return None

    return f"{base_url}index.cfm?page_id=972&lead_id_list={lead_id}&action=new"

def get_created_presale_url(project_name, presale_id):
    """
    Constructs the URL for editing an existing presale.

    :param project_name: The project code (e.g., 'sm_eu').
    :param presale_id: The ID of the existing presale.
    :return: Constructed URL string or None if project_name not in base URLs.
    """
    base_url = PROJECT_BASE_URLS.get(project_name, "")
    if not base_url:
        return None

    return f"{base_url}index.cfm?page_id=972&id={presale_id}&action=edit"
