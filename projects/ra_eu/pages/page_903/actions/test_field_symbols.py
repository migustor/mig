# common/pages/page_903/actions/test_field_symbols.py
import logging
import time

def test_field_symbols(driver, field_element, symbols, timeouts=None):
    """
    Tests a field element with special symbols to see which are accepted and which are rejected
    
    Args:
        driver: Selenium WebDriver
        field_element: The input field element to test
        symbols: String of symbols to test
        timeouts: Dictionary with timeouts for various operations
        
    Returns:
        dict: Result with lists of accepted and rejected symbols
    """
    logger = logging.getLogger('test')
    field_id = field_element.get_attribute("id") or field_element.get_attribute("name") or "unknown"
    logger.info(f"Testing field {field_id} with symbols: {symbols}")
    
    results = {"accepted": [], "rejected": []}
    
    try:
        # Clear the field first
        field_element.clear()
        
        # Test each symbol
        for symbol in symbols:
            field_element.send_keys(symbol)
            time.sleep(0.1)  # Short wait for DOM update
            
            current_value = field_element.get_attribute("value")
            
            if symbol in current_value:
                logger.info(f"Symbol '{symbol}' was accepted in field {field_id}")
                results["accepted"].append(symbol)
            else:
                logger.info(f"Symbol '{symbol}' was rejected in field {field_id}")
                results["rejected"].append(symbol)
                
            # Clear for next symbol
            field_element.clear()
            time.sleep(0.05)
        
        return results
            
    except Exception as e:
        error_msg = f"Error testing field {field_id} with symbols: {str(e)}"
        logger.error(error_msg)
        # Return partial results if available
        results["error"] = error_msg
        return results