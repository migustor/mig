from common.config.base_urls import PROJECT_BASE_URLS

PAGE_PATH = "eu/intranet/warehouse/goods_delivery.cfm"

def get_goods_delivery_url(project_name="ra_eu"):
    """
    Returns the full URL for the goods delivery page,
    based on the project's base URL stored in PROJECT_BASE_URLS.
    """
    base_url = PROJECT_BASE_URLS[project_name]
    # Remove '/sage/' from the end if present
    if base_url.endswith('/sage/'):
        base_url = base_url[:-5]
    return f"{base_url}{PAGE_PATH}"