from __future__ import annotations

import importlib
import logging


def test_logging_uses_environment_level(monkeypatch):
    monkeypatch.setenv("HARNESS_MANAGER_LOG_LEVEL", "DEBUG")
    module = importlib.import_module("harness_manager.logging_config")

    module.configure_logging(force=True)

    assert logging.getLogger("harness_manager").getEffectiveLevel() == logging.DEBUG


def test_logging_defaults_to_info(monkeypatch):
    monkeypatch.delenv("HARNESS_MANAGER_LOG_LEVEL", raising=False)
    module = importlib.import_module("harness_manager.logging_config")

    module.configure_logging(force=True)

    assert logging.getLogger("harness_manager").getEffectiveLevel() == logging.INFO
