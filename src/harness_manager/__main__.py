from __future__ import annotations

import sys


def main() -> int:
    from harness_manager.logging_config import configure_logging
    from harness_manager.gui.main_window import run_app

    configure_logging()
    return run_app(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
