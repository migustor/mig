import logging
import time
from selenium.webdriver.common.by import By

logger = logging.getLogger("test")

def several_saves(driver):
    """
    Нажимает кнопку Save (id="save_btn") несколько раз на странице 905.
    После создания коробки проверяем, не будет ли дублей.
    """
    try:
        for i in range(3):
            time.sleep(1)  # Небольшая задержка
            # Ищем кнопку "Save" по id="save_btn"
            save_buttons = driver.find_elements(By.ID, "save_btn")
            if save_buttons:
                save_buttons[0].click()
                logger.info(f"Add. clicks on Save ({i + 1}/3)")
            else:
                logger.warning("Save button not found for add. clicks.")
        
        return {"success": True, "error": None}

    except Exception as e:
        error_msg = f"ERROR while several clicks of Save (905): {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
