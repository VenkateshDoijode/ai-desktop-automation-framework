"""
logger.py
---------
Configures a colorised console + rotating-file logger for the framework.
Call setup_logging() once from conftest.py.
"""

import logging
import logging.handlers
import os
from pathlib import Path

try:
    import colorlog  # type: ignore
    _COLOR = True
except ImportError:
    _COLOR = False

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "automation.log"
MAX_BYTES = 5 * 1024 * 1024   # 5 MB
BACKUP_COUNT = 3


def setup_logging(level: str = "INFO") -> None:
    """
    Initialise logging for the entire test run.

    Creates a ``logs/`` directory and writes to ``automation.log``
    with a rotating file handler, plus a coloured console handler.
    """
    LOG_DIR.mkdir(exist_ok=True)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Remove any handlers pytest may have already attached
    root.handlers.clear()

    # ---- Console handler -------------------------------------------------
    if _COLOR:
        fmt = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)-8s]%(reset)s "
            "%(cyan)s%(name)s%(reset)s: %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "white",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    else:
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(numeric_level)
    root.addHandler(ch)

    # ---- File handler ----------------------------------------------------
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
    )
    file_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
    )
    fh.setFormatter(file_fmt)
    fh.setLevel(logging.DEBUG)   # always write DEBUG to file
    root.addHandler(fh)

    logging.getLogger("pywinauto").setLevel(logging.WARNING)
    logging.getLogger("comtypes").setLevel(logging.WARNING)
