import sqlite3
import json
import uuid
import os
from datetime import datetime

class StateManager:
    """
    Pengelola state persistent untuk Snowline.
    Ini yang membuat Snowline menjadi "OS" bukan hanya script.
    """
    
    def __init__(self, db_path: str = "./.snowline/state.db"):
        self.db_path = db_path
        
        # Ensure parent directory exists
        db_dir = os.path.dirname(os.path.abspath(db_path))
        os.makedirs(db_dir, exist_ok=True)
        
        self.db = sqlite3.connect(db_path)
        self.current_execution_id = None
        self._init_schema()
    
    def _init_schema(self):
        """Setup database schema"""
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS executions (
                id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                tool_name TEXT,
                agent_id TEXT,
                request_params JSON
            );
            
            CREATE TABLE IF NOT EXISTS artifacts (
                id TEXT PRIMARY KEY,
                execution_id TEXT,
                artifact_type TEXT,
                data JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(execution_id) REFERENCES executions(id)
            );
            
            CREATE TABLE IF NOT EXISTS agent_memory (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                memory_type TEXT,
                content JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ttl_seconds INTEGER
            );
        """)
        self.db.commit()
    
    def start_execution(self, exec_id: str, tool_name: str, agent_id: str = None):
        """Tandai eksekusi dimulai"""
        self.current_execution_id = exec_id
        self.db.execute(
            """INSERT INTO executions (id, status, tool_name, agent_id, request_params)
               VALUES (?, ?, ?, ?, ?)""",
            (exec_id, "started", tool_name, agent_id, "{}")
        )
        self.db.commit()
    
    def save_artifact(self, artifact_type: str, data: dict) -> str:
        """
        Simpan hasil eksekusi (backup, preview, dll).
        Ini yang memungkinkan rollback bekerja.
        """
        artifact_id = str(uuid.uuid4())
        self.db.execute(
            """INSERT INTO artifacts (id, execution_id, artifact_type, data)
               VALUES (?, ?, ?, ?)""",
            (artifact_id, self.current_execution_id, artifact_type, json.dumps(data))
        )
        self.db.commit()
        return artifact_id
    
    def get_artifact(self, artifact_id: str) -> dict:
        """Ambil artifact dari eksekusi sebelumnya"""
        result = self.db.execute(
            "SELECT data FROM artifacts WHERE id = ?",
            (artifact_id,)
        ).fetchone()
        return json.loads(result[0]) if result else None
    
    def memorize(self, agent_id: str, memory_type: str, content: dict, ttl_seconds: int = 3600):
        """Simpan ke agent memory (dengan auto-expire)"""
        memory_id = str(uuid.uuid4())
        self.db.execute(
            """INSERT INTO agent_memory (id, agent_id, memory_type, content, ttl_seconds)
               VALUES (?, ?, ?, ?, ?)""",
            (memory_id, agent_id, memory_type, json.dumps(content), ttl_seconds)
        )
        self.db.commit()
    
    def recall(self, agent_id: str, memory_type: str, limit: int = 5) -> list:
        """Ambil memory dari history"""
        results = self.db.execute(
            """SELECT content FROM agent_memory 
               WHERE agent_id = ? AND memory_type = ?
               ORDER BY created_at DESC LIMIT ?""",
            (agent_id, memory_type, limit)
        ).fetchall()
        return [json.loads(r[0]) for r in results]
