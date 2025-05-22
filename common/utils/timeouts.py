"""
Shared time-control helpers for E2E flows.
"""

import logging
import time

# Readable presets (seconds)
PAUSE = {
    "short":  1.0,   # quick DOM repaint / click debounce
    "medium": 2.5,   # average page re-paint / Ajax finish
    "long":   5.0    # full navigation or slow network
}

def smart_sleep(kind: str = "short", reason: str = "") -> None:
    """
    Sleep for a preset period and log the reason.
    """
    sec = PAUSE.get(kind, 1.0)
    if reason:
        logging.getLogger("test").debug(f"[sleep] {sec:0.1f}s  ▶  {reason}")
    time.sleep(sec)
