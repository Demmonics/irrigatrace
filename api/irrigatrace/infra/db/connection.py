"""
SQLite database connection and schema initialization for IrrigaTrace.
Enforces WAL mode, foreign keys, and executes schema.sql + triggers.sql.
"""
from __future__ import annotations

import sqlite3
import os
from pathlib import Path
from typing import Optional


class Database:
    def __init__(self, db_path: str = "./irrigatrace.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def _init_db(self):
        sql_dir = Path(__file__).resolve().parent.parent.parent.parent / "sql"
        schema_path = sql_dir / "schema.sql"
        triggers_path = sql_dir / "triggers.sql"

        conn = self.get_connection()
        try:
            if schema_path.exists():
                with open(schema_path, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            if triggers_path.exists():
                with open(triggers_path, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            conn.commit()
        finally:
            conn.close()


_DEFAULT_DB: Optional[Database] = None


def get_db(db_path: Optional[str] = None) -> Database:
    global _DEFAULT_DB
    if db_path is not None:
        return Database(db_path)
    if _DEFAULT_DB is None:
        env_path = os.environ.get("DATABASE_URL", "./irrigatrace.db")
        if env_path.startswith("sqlite:///"):
            env_path = env_path[len("sqlite:///"):]
        _DEFAULT_DB = Database(env_path)
    return _DEFAULT_DB
