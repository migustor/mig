import logging
import time
from projects.et_eu.pages.page_902.page_info import get_page_902_url
from projects.et_eu.pages.page_902.locators import NewBoxLocators
from common.utils.error_handling import jenkins_aware

@jenkins_aware()
def create_package(driver, project_name, sales_order_id):
    """
    Открывает страницу создания упаковки, вводит значения и сохраняет.

    Args:
        driver: WebDriver (передается из другого файла).
        project_name: Название проекта (например, "ra_eu", "et_eu").
        sales_order_id: ID заказа.

    Returns:
        dict: Результат выполнения действия.
    """
    logger = logging.getLogger('test')
    logger.info(f"Creating package for sales_order_id={sales_order_id} in {project_name}.")

    # Генерируем URL
    page_url = get_page_902_url(project_name, sales_order_id)
    if not page_url:
        return {"success": False, "error": "Could not generate URL for the page."}
    
    driver.get(page_url)

    # Ждем загрузку страницы
    logger.info("Waiting for page to load...")
    time.sleep(5)  # Ожидание полной загрузки страницы
    
    try:
        # Если проект et_eu, сначала выбираем сектора
        if project_name == "et_eu":
            logger.info("Selecting warehouse sector for et_eu...")
            script = """
            (() => {
                // Изменяем первый select на "A"
                let select1 = document.querySelector("#warehouse_sector");
                if (select1) {
                    select1.value = "A"; 
                    select1.dispatchEvent(new Event('change', { bubbles: true }));
                } else {
                    console.error("Элемент #warehouse_sector не найден.");
                }

                // Изменяем второй select на "WHSE 1-Sector 1" (значение "1|1")
                let select2 = document.querySelector('select[name="whse_sector_new"]');
                if (select2) {
                    select2.value = "1|1"; 
                    select2.dispatchEvent(new Event('change', { bubbles: true }));
                } else {
                    console.error('Элемент select[name="whse_sector_new"] не найден.');
                }
            })();
            """
            driver.execute_script(script)
            time.sleep(2)  # Даем время для применения выбора

        # Ввод значений в поля размеров и веса
        driver.find_element(*NewBoxLocators.LENGTH_INPUT).send_keys("10")
        driver.find_element(*NewBoxLocators.WIDTH_INPUT).send_keys("10")
        driver.find_element(*NewBoxLocators.HEIGHT_INPUT).send_keys("10")
        driver.find_element(*NewBoxLocators.WEIGHT_INPUT).send_keys("10")
        
        # Клик на заголовок страницы, чтобы зафиксировать введенные данные
        driver.find_element(*NewBoxLocators.PAGE_TITLE).click()
        logger.info("Clicked on page title to confirm input.")
        
        # Небольшая пауза перед сохранением
        time.sleep(3)
        
        # Нажатие кнопки Save
        driver.find_element(*NewBoxLocators.SAVE_BUTTON).click()
        logger.info("Package created successfully.")
        return {"success": True, "error": None}
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
