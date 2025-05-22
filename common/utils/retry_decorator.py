"""
Project-level retry decorator for test functions.
This decorator can retry entire project test iterations when they fail.
"""
import logging
import time
import functools
import traceback
from typing import Callable, Dict, Any

def with_retry(max_attempts: int = 3, retry_delay: int = 5):
    """
    Decorator for project test functions to add retry capability.
    
    Args:
        max_attempts: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        Decorated function with retry capability
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger('test')
            # Get project name from args or kwargs
            if 'project_code' in kwargs:
                project_name = kwargs['project_code']
            elif len(args) > 1 and isinstance(args[1], str):
                project_name = args[1]  # Assuming project_code is the second argument after driver
            else:
                project_name = 'unknown'
            
            for attempt in range(1, max_attempts + 1):
                try:
                    if attempt > 1:
                        logger.info(f"Retry attempt {attempt}/{max_attempts} for project {project_name}")
                    
                    # Call the original function
                    result = func(*args, **kwargs)
                    
                    # If it's a dict with success status, check it
                    if isinstance(result, dict) and not result.get('success', True):
                        error_msg = result.get('error', 'Unknown error')
                        logger.warning(f"Project {project_name} test failed with error: {error_msg}")
                        
                        # If we have more attempts, we'll retry
                        if attempt < max_attempts:
                            logger.info(f"Will retry in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            continue
                    
                    # Success or no more retries
                    return result
                    
                except Exception as e:
                    logger.error(f"Exception during test for {project_name}: {str(e)}")
                    
                    # If we have more attempts, retry
                    if attempt < max_attempts:
                        logger.info(f"Will retry in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        # No more retries, reraise or return failure
                        logger.error(f"All {max_attempts} retry attempts failed for {project_name}")
                        return {
                            "success": False,
                            "error": f"Failed after {max_attempts} attempts: {str(e)}",
                            "project_name": project_name
                        }
            
            # This should not be reached but just in case
            return {
                "success": False,
                "error": "Retry loop exited unexpectedly",
                "project_name": project_name
            }
        
        return wrapper
    return decorator


def retry_on_failure(test_func: Callable, *args, max_attempts: int = 3, 
                    retry_delay: int = 5, **kwargs) -> Dict[str, Any]:
    """
    Function to retry a test function on failure.
    This can be used when a decorator is not suitable.
    
    Args:
        test_func: The test function to call
        args: Positional arguments for the test function
        max_attempts: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        kwargs: Keyword arguments for the test function
        
    Returns:
        Result of the test function
    """
    logger = logging.getLogger('test')
    # Get project name from args or kwargs
    if 'project_code' in kwargs:
        project_name = kwargs['project_code']
    elif len(args) > 1 and isinstance(args[1], str):
        project_name = args[1]  # Assuming project_code is the second argument after driver
    else:
        project_name = 'unknown'
    
    for attempt in range(1, max_attempts + 1):
        try:
            if attempt > 1:
                logger.info(f"Retry attempt {attempt}/{max_attempts} for project {project_name}")
            
            # Call the test function
            result = test_func(*args, **kwargs)
            
            # If it's a dict with success status, check it
            if isinstance(result, dict) and not result.get('success', True):
                error_msg = result.get('error', 'Unknown error')
                logger.warning(f"Project {project_name} test failed with error: {error_msg}")
                
                # If we have more attempts, retry
                if attempt < max_attempts:
                    logger.info(f"Will retry in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
            
            # Success or no more retries
            return result
                
        except Exception as e:
            logger.error(f"Exception during test for {project_name}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # If we have more attempts, retry
            if attempt < max_attempts:
                logger.info(f"Will retry in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                # No more retries, return failure
                logger.error(f"All {max_attempts} retry attempts failed for {project_name}")
                return {
                    "success": False,
                    "error": f"Failed after {max_attempts} attempts: {str(e)}",
                    "project_name": project_name
                }
    
    # This should not be reached
    return {
        "success": False,
        "error": "Retry loop exited unexpectedly",
        "project_name": project_name
    }