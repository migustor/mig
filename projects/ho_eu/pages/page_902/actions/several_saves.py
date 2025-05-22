import logging
import time

logger = logging.getLogger("test")

def several_saves(driver):
    """
    Нажимает кнопку Save еще 3 раза в течение 3 секунд после создания коробки.
    
    Args:
        driver: WebDriver (уже передан в функцию).
    
    Returns:
        dict: Результат выполнения действия.
    """
    try:
        for i in range(3):
            time.sleep(1)  # Ожидание перед повторным нажатием
            save_buttons = driver.find_elements("css selector", "button.save_shipping_package")
            if save_buttons:
                save_buttons[0].click()
                logger.info(f"Additional Save attempts ({i + 1}/3)")
            else:
                logger.warning("Save button not found.")
        
        return {"success": True}

    except Exception as e:
        logger.error(f"ERROR while several saves: {str(e)}")
        return {"success": False, "error": str(e)}
