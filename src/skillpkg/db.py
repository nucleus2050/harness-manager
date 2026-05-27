from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  default_path TEXT,
  custom_path TEXT,
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  source_client TEXT,
  relative_path TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS packages (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS package_skills (
  package_id TEXT NOT NULL REFERENCES packages(id) ON DELETE CASCADE,
  skill_id TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (package_id, skill_id)
);

CREATE TABLE IF NOT EXISTS install_records (
  id TEXT PRIMARY KEY,
  package_id TEXT NOT NULL REFERENCES packages(id),
  skill_id TEXT NOT NULL REFERENCES skills(id),
  client_type TEXT NOT NULL,
  target_path TEXT NOT NULL,
  installed_path TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  installed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  uninstalled_at TEXT,
  status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS operation_logs (
  id TEXT PRIMARY KEY,
  action TEXT NOT NULL,
  client_type TEXT,
  package_id TEXT,
  skill_id TEXT,
  message TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS import_sources (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  path TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS harnesses (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  name TEXT NOT NULL,
  source_type TEXT,
  relative_path TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS harness_assets (
  harness_id TEXT NOT NULL REFERENCES harnesses(id) ON DELETE CASCADE,
  asset_id TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
  asset_type TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (harness_id, asset_id)
);"""

CLIENT_SEEDS = (
    ("codex", "Codex"),
    ("claude_code", "Claude Code"),
    ("opencode", "OpenCode"),
)


def connect(path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.executemany(
        "INSERT OR IGNORE INTO clients(type, name) VALUES (?, ?)",
        CLIENT_SEEDS,
    )
    conn.commit()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[None]:
    try:
        yield
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()

