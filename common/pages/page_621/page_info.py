from common.config.base_urls import PROJECT_BASE_URLS

def get_page_621_url(project_name, company_id):
    """
    Returns the URL for page 621 for the specified project and company.
    
    Args:
        project_name: Name of the project (e.g., "sm_eu")
        company_id: ID of the company (e.g., 500000)
        
    Returns:
        str: URL for page 621 with the provided company_id, or None if base_url not found
    """
    base_url = PROJECT_BASE_URLS.get(project_name, "")
    if not base_url:
        return None
        
    return f"{base_url}index.cfm?page_id=621&company_id={company_id}"