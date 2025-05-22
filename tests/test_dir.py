import os
from datetime import datetime
import logging
import sys

# Configure basic logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler('test_log.txt', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)

def test_local_path_write_delete(local_path):
    """
    Tests the ability to write and delete a file in the specified local folder.

    Args:
        local_path (str): The path to the local folder.
    """
    logger.info(f"Starting test to write and delete a file in the local folder: '{local_path}'")
    test_filename = f"test_write_delete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    test_filepath = os.path.join(local_path, test_filename)

    try:
        # Check if the folder exists and create it if it doesn't
        os.makedirs(local_path, exist_ok=True)
        logger.info(f"Successfully checked or created directory: '{local_path}'")

        # Attempt to create and write to the file with UTF-8 encoding
        with open(test_filepath, 'w', encoding='utf-8') as f:
            f.write("Test write in English.")
        logger.info(f"Successfully created and wrote to file: '{test_filepath}'")

        # Attempt to delete the file
        os.remove(test_filepath)
        logger.info(f"Successfully deleted file: '{test_filepath}'")
        print(f"Successfully tested writing and deleting a file in '{local_path}'.")
        return True
    except Exception as e:
        logger.error(f"An error occurred while testing writing and deleting a file in '{local_path}': {str(e)}")
        print(f"Error while testing writing and deleting a file in '{local_path}': {e}")
        return False

if __name__ == "__main__":
    local_path = r"E:\Documents\Error_Screens"
    test_local_path_write_delete(local_path)