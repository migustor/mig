
# /common/pages/page_953/page_info.py
from common.config.base_urls import PROJECT_BASE_URLS

PAGE_ID = "953"

def get_page_953_url(project_name="ag_eu"):
    """
    Returns the full URL for page 953 (Vendor Evolution Report),
    based on the project's base URL stored in PROJECT_BASE_URLS.
    """
    base_url = PROJECT_BASE_URLS[project_name]
    return f"{base_url}index.cfm?page_id={PAGE_ID}"