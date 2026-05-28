from __future__ import annotations

import logging
import os


LOG_LEVEL_ENV = "HARNESS_MANAGER_LOG_LEVEL"


def configure_logging(force: bool = False) -> None:
    level_name = os.environ.get(LOG_LEVEL_ENV, "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=force,
    )
    logging.getLogger("harness_manager").setLevel(level)
