"""
Модуль для выполнения выхода из системы.
"""
import logging
import time

def logout_from_system(driver, project_name=None, skip_for_projects=None):
    """
    Выполняет выход из системы и очистку данных сессии.
    
    Args:
        driver: Selenium WebDriver
        project_name: Название проекта (например, "ra_eu", "sm_us", и т.д.)
        skip_for_projects: Список проектов, для которых нужно пропустить логаут
        
    Returns:
        bool: True если выход успешен, False в противном случае
    """
    logger = logging.getLogger('test')
    
    # Если задан список проектов для пропуска, и текущий проект в этом списке
    if skip_for_projects and project_name in skip_for_projects:
        logger.info(f"Skipping logout for project {project_name} as requested")
        return True
        
    try:
        project_info = f" from project {project_name}" if project_name else ""
        logger.info(f"Logging out{project_info}")
        current_url = driver.current_url
        
        # Construct logout URL based on current URL
        if "sage" in current_url:
            base_parts = current_url.split("sage")
            logout_url = base_parts[0] + "sage/?logout"
            
            driver.get(logout_url)
            time.sleep(2)  # Wait for logout to complete
            
            # Clear cookies and storage
            driver.delete_all_cookies()
            try:
                driver.execute_script("localStorage.clear();")
                driver.execute_script("sessionStorage.clear();")
            except:
                pass  # Ignore if storage clearing fails
                
            logger.info(f"Successfully logged out{project_info}")
            return True
        else:
            logger.warning(f"Cannot determine logout URL{project_info} from {current_url}")
            return False
    except Exception as e:
        project_info = f" from {project_name}" if project_name else ""
        logger.error(f"Error during logout{project_info}: {str(e)}")
        return False