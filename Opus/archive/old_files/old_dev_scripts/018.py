"""
FILE 18: TELEMETRY MONITORING
=============================
System health and event monitoring.
(Part of TIER 6 ADVANCED FEATURES)
File 18 of 20: Telemetry Monitor
"""
import logging
import sqlite3
import json
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# MODULE 18: TELEMETRY MONITORING
# (Extracted from 010.py)
# ============================================================================
class TelemetryMonitor:
    """System health and event monitoring."""
    def __init__(self, db_path: str = "telemetry.db"):
        self.db_path = db_path
        try:
            self._init_db()
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize telemetry database at {db_path}: {e}")

    def _init_db(self):
        """Initialize the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS events 
                            (id INTEGER PRIMARY KEY, timestamp TEXT, event_type TEXT, metadata TEXT, level TEXT)''')

    def log_event(self, event_type: str, metadata: Dict = None, level: str = "INFO"):
        """Log a system event to the telemetry database."""
        timestamp = datetime.now().isoformat()
        metadata_str = json.dumps(metadata) if metadata else "{}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO events (timestamp, event_type, metadata, level) VALUES (?, ?, ?, ?)",
                             (timestamp, event_type, metadata_str, level))
        except sqlite3.Error as e:
            logger.error(f"Failed to write to telemetry database: {e}")
            
        if level in ["ERROR", "WARNING", "CRITICAL"]:
             logger.log(logging.ERROR if level in ["ERROR", "CRITICAL"] else logging.WARNING, 
                        f"TELEMETRY EVENT ({level}): {event_type} - {metadata_str}")

    def get_health_status(self) -> Dict:
        """Get the current system health status based on recent errors."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                recent_errors = conn.execute(
                    "SELECT COUNT(*) FROM events WHERE level='ERROR' AND timestamp > datetime('now', '-1 hour')"
                ).fetchone()[0]
            
            return {"status": "HEALTHY" if recent_errors == 0 else "DEGRADED", "recent_errors": recent_errors}
        except sqlite3.Error as e:
            logger.error(f"Failed to query telemetry database: {e}")
            return {"status": "UNKNOWN", "recent_errors": -1}

# Global instance
telemetry = TelemetryMonitor()