from common.config.base_urls import PROJECT_BASE_URLS

PAGE_PATH = "euwhse/stock/scan_barcodes.cfm"

def get_stocking_url(project_name: str = "sm_eu") -> str:
    """
    Возвращает полный URL для страницы сканирования штрих‑кодов.

    Строит ссылку вида:
        https://stage15.office.sovasystem.com/euwhse/stock/scan_barcodes.cfm
    используя базовый URL из PROJECT_BASE_URLS. Если базовый URL
    заканчивается на "sage/", этот сегмент удаляется перед добавлением
    относительного пути PAGE_PATH.

    Параметры
    ----------
    project_name : str, optional
        Ключ словаря PROJECT_BASE_URLS. По умолчанию "sm_eu".

    Возвращает
    ----------
    str
        Полная ссылка, готовая к использованию в тестах.
    """
    base_url = PROJECT_BASE_URLS[project_name]
    # Удаляем завершающий сегмент "sage/", если он присутствует
    if base_url.endswith("sage/"):
        base_url = base_url[:-len("sage/")]
    return f"{base_url}/euwhse/stock/scan_barcodes.cfm"
