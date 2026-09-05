import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "marginguard.db"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            item_count INTEGER NOT NULL,
            opportunity_value REAL NOT NULL,
            payload TEXT NOT NULL
        )
        """)


def save_scan(results: list[dict]) -> int:
    opportunity = round(sum(max(float(r.get("opportunity", 0)), 0) for r in results), 2)
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute(
            "INSERT INTO scans(item_count, opportunity_value, payload) VALUES (?, ?, ?)",
            (len(results), opportunity, json.dumps(results)),
        )
        return int(cur.lastrowid)


def recent_scans(limit: int = 8) -> list[dict]:
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT id, created_at, item_count, opportunity_value FROM scans ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
