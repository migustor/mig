# common/pages/page_907/actions/generate_order_tracking_url.py
import urllib.parse

def generate_order_url(project_code, order_id, order_type="so"):
    """
    Генерирует прямую ссылку на отслеживание заказа на странице логистики (907)
    
    Args:
        project_code: Код проекта (например, "ra_eu", "gr_eu")
        order_id: Номер заказа для отслеживания
        order_type: Тип заказа ("so" для Sales Order, "po" для Purchase Order)
        
    Returns:
        str: URL для прямого доступа к странице отслеживания заказа
    """
    # Используем фиксированный домен для страницы логистики
    base_url = "https://stage15.office.grafit.md/sage/"
    
    # Формируем полный URL для отслеживания
    url = f"{base_url}index.cfm?page_id=907&project_id={project_code}&so_id={order_id}&order_type={order_type}"
    
    return url