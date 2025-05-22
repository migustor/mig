# Пример, как генерировать URL для page_id=442

from common.config.base_urls import PROJECT_BASE_URLS

PAGE_ID = "shop"

def get_page_shop_url(project_name=""):
    """
    Возвращает полный URL для данной страницы,
    исходя из базового URL проекта, хранящегося в PROJECT_BASE_URLS.
    """
    base_url = PROJECT_BASE_URLS.get(project_name)
    if not base_url:
        raise ValueError(f"Unknown project name: {project_name}")
    return f"{base_url}index.php?page={PAGE_ID}"