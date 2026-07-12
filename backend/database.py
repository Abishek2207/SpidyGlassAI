import sqlite3
import os
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="visionvoice.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    source TEXT,
                    content TEXT,
                    metadata TEXT
                )
            ''')
            conn.commit()

    def log_interaction(self, source: str, content: str, metadata: dict = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO history (timestamp, source, content, metadata) VALUES (?, ?, ?, ?)",
                (datetime.now().isoformat(), source, content, json.dumps(metadata) if metadata else "{}")
            )
            conn.commit()

    def get_recent_history(self, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT timestamp, source, content, metadata FROM history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [{"timestamp": r[0], "source": r[1], "content": r[2], "metadata": json.loads(r[3])} for r in reversed(rows)]

db_manager = DatabaseManager()
