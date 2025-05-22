# /common/pages/page_925/page_info.py
from common.config.base_urls import PROJECT_BASE_URLS

PAGE_ID = "925"

def get_page_925_url(project_name="ra_eu"):
    """
    Returns the full URL for page 925 (Sales Inquiry page),
    based on the project's base URL stored in PROJECT_BASE_URLS.
    """
    base_url = PROJECT_BASE_URLS[project_name]
    return f"{base_url}index.cfm?page_id={PAGE_ID}"

def get_si_editor_url(project_name, si_id):
    """
    Returns the URL for the SI editor page with the specific SI ID.
    """
    base_url = PROJECT_BASE_URLS[project_name]
    return f"{base_url}index.cfm?page_id={PAGE_ID}&phase=edit&id={si_id}"