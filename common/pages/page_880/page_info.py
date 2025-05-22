# page_info.py
from common.config.base_urls import PROJECT_BASE_URLS

PAGE_ID = "880"

def get_orders_page_url(project_name="ra_eu"):
    """
    Возвращает полный URL для страницы заказов (ID=880),
    исходя из базового URL проекта, хранящегося в PROJECT_BASE_URLS.
    """
    base_url = PROJECT_BASE_URLS[project_name]
    return f"{base_url}index.cfm?page_id={PAGE_ID}"