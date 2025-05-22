import os
import time
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def wait_for_xls_and_check(download_dir, first_name_expected, timeout=30):
    """
    Ожидает появления *.xls-файла, в названии которого есть 'candidates_report',
    и проверяет, что в первой колонке найдено нужное имя (first_name_expected).
    Анализируем только самый свежий из подходящих файлов.
    """
    t0 = time.time()
    found_file = None
    
    
    time.sleep(5)

    while time.time() - t0 < timeout:
        # Ищем только файлы *.xls, в имени которых есть 'candidates_report'.
        xls_list = [
            f for f in os.listdir(download_dir)
            if f.lower().endswith(".xls") and "candidates_report" in f.lower()
        ]
        if xls_list:
            # Формируем список полных путей и выбираем самый свежий
            full_paths = [os.path.join(download_dir, fname) for fname in xls_list]
            found_file = max(full_paths, key=os.path.getctime)
            # Как только нашли подходящий файл (самый свежий), выходим из цикла
            break
        time.sleep(1)

    if not found_file:
        raise Exception(
            f"Не удалось найти *.xls файл (с 'candidates_report' в названии) в папке {download_dir} за {timeout} с."
        )

    logger.info(f"Found XLS: {found_file}, checking for '{first_name_expected}'")

    # Считываем xls
    df = pd.read_excel(found_file, header=None)
    col_values = df.iloc[:, 0].astype(str).tolist()

    # Ищем подстроку в первой колонке
    if any(first_name_expected in val for val in col_values):
        logger.info(f"[OK] '{first_name_expected}' найден в XLS: {os.path.basename(found_file)}")
    else:
        raise AssertionError(
            f"'{first_name_expected}' не найден в XLS ({os.path.basename(found_file)}).\n"
            #f"Значения первой колонки: {col_values}"
        )
        

    # Удаляем файл после проверки
    os.remove(found_file)
    logger.info(f"Removed {found_file} after check.")
