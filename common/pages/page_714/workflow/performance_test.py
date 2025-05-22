# common/pages/page_714/workflow/performance_test.py
import logging
import time

from common.pages.page_714.actions.measure_load_time import measure_page714_load_time

logger = logging.getLogger(__name__)

def run_load_performance_test(
        driver,
        url: str,
        expected_ms: int = 2000,
        timeout: int = 30,
        iterations: int = 3
    ):
    """
    Открывает url несколько раз и считает среднее / худшее время загрузки.
    Фейлит тест, если среднее > expected_ms.
    """
    total, worst = 0, 0

    for i in range(1, iterations + 1):
        logger.info(f"[714‑PERF] Итерация {i}/{iterations}")
        driver.get(url)

        res = measure_page714_load_time(driver, timeout=timeout)
        if not res["success"]:
            return res

        total += res["load_time_ms"]
        worst = max(worst, res["load_time_ms"])
        time.sleep(1)          # маленький «дышать» между перезагрузками

    avg = round(total / iterations)
    logger.info(f"[714‑PERF] Среднее {avg} мс, худшее {worst} мс "
                f"(порог {expected_ms} мс)")

    if avg > expected_ms:
        return {
            "success": False,
            "error": f"Среднее {avg} мс превысило лимит {expected_ms} мс",
            "avg_ms": avg,
            "worst_ms": worst
        }

    return {"success": True, "error": None, "avg_ms": avg, "worst_ms": worst}
