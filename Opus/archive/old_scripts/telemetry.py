"""
OPUS MAXIMUS - TELEMETRY & ANALYTICS SYSTEM
============================================
Tracks generation metrics, failures, resource usage, and performance.
Stores data in SQLite for analysis and visualization.

Usage:
    from telemetry import TelemetrySystem

    telemetry = TelemetrySystem()
    telemetry.log_section(subject, section_num, word_count, attempts, time_taken)
    telemetry.log_llm_call(prompt_tokens, completion_tokens, time_taken)

Author: Automated System for Orthodox Apologetics
Date: 2025-11-07
Version: GPU-NATIVE-V2
"""

import sqlite3
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import atexit

logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SectionMetric:
    """Metrics for a single section generation"""
    timestamp: str
    subject: str
    tier: str
    category: str
    section_num: int
    section_name: str
    word_count: int
    attempts: int
    time_taken: float
    vram_used_gb: float
    success: bool
    failures: str  # JSON list


@dataclass
class EntryMetric:
    """Metrics for a complete entry"""
    timestamp: str
    subject: str
    tier: str
    category: str
    total_word_count: int
    total_time: float
    section_count: int
    total_attempts: int
    expansion_attempts: int
    success: bool
    failures: str  # JSON list


@dataclass
class LLMCallMetric:
    """Metrics for a single LLM call"""
    timestamp: str
    subject: str
    purpose: str  # 'blueprint', 'section', 'correction', 'expansion'
    prompt_length: int
    response_length: int
    time_taken: float
    temperature: float
    max_tokens: int


@dataclass
class ValidationMetric:
    """Metrics for validation failures"""
    timestamp: str
    subject: str
    section_name: str
    failure_type: str  # 'format', 'style', 'length', 'uniqueness', etc.
    failure_message: str
    attempt_num: int


# ============================================================================
# TELEMETRY SYSTEM
# ============================================================================

class TelemetrySystem:
    """
    Comprehensive telemetry and analytics system
    """

    def __init__(self, db_path: str = 'telemetry.db'):
        """
        Initialize telemetry system

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.cursor = self.conn.cursor()

        self._create_tables()

        # Register cleanup
        atexit.register(self.close)

        logger.info(f"TelemetrySystem initialized (DB: {self.db_path})")

    def _create_tables(self):
        """Create database tables if they don't exist"""

        # Sections table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                subject TEXT NOT NULL,
                tier TEXT,
                category TEXT,
                section_num INTEGER,
                section_name TEXT,
                word_count INTEGER,
                attempts INTEGER,
                time_taken REAL,
                vram_used_gb REAL,
                success BOOLEAN,
                failures TEXT
            )
        """)

        # Entries table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                subject TEXT NOT NULL,
                tier TEXT,
                category TEXT,
                total_word_count INTEGER,
                total_time REAL,
                section_count INTEGER,
                total_attempts INTEGER,
                expansion_attempts INTEGER,
                success BOOLEAN,
                failures TEXT
            )
        """)

        # LLM calls table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                subject TEXT,
                purpose TEXT,
                prompt_length INTEGER,
                response_length INTEGER,
                time_taken REAL,
                temperature REAL,
                max_tokens INTEGER
            )
        """)

        # Validation failures table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_failures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                subject TEXT,
                section_name TEXT,
                failure_type TEXT,
                failure_message TEXT,
                attempt_num INTEGER
            )
        """)

        # Resource snapshots table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                vram_total_gb REAL,
                vram_used_gb REAL,
                vram_free_gb REAL,
                ram_total_gb REAL,
                ram_used_gb REAL,
                ram_free_gb REAL,
                cpu_percent REAL
            )
        """)

        self.conn.commit()

        # Create indexes for faster queries
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sections_subject ON sections(subject)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sections_timestamp ON sections(timestamp)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entries_subject ON entries(subject)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_validation_failures_type
            ON validation_failures(failure_type)
        """)

        self.conn.commit()

    # ========================================================================
    # LOGGING METHODS
    # ========================================================================

    def log_section(self, subject: str, tier: str, category: str,
                   section_num: int, section_name: str, word_count: int,
                   attempts: int, time_taken: float, vram_used_gb: float,
                   success: bool, failures: List[str] = None):
        """Log section generation metrics"""
        try:
            self.cursor.execute("""
                INSERT INTO sections
                (timestamp, subject, tier, category, section_num, section_name,
                 word_count, attempts, time_taken, vram_used_gb, success, failures)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                subject,
                tier,
                category,
                section_num,
                section_name,
                word_count,
                attempts,
                time_taken,
                vram_used_gb,
                success,
                json.dumps(failures if failures else [])
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log section metrics: {e}")

    def log_entry(self, subject: str, tier: str, category: str,
                 total_word_count: int, total_time: float, section_count: int,
                 total_attempts: int, expansion_attempts: int, success: bool,
                 failures: List[str] = None):
        """Log complete entry metrics"""
        try:
            self.cursor.execute("""
                INSERT INTO entries
                (timestamp, subject, tier, category, total_word_count, total_time,
                 section_count, total_attempts, expansion_attempts, success, failures)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                subject,
                tier,
                category,
                total_word_count,
                total_time,
                section_count,
                total_attempts,
                expansion_attempts,
                success,
                json.dumps(failures if failures else [])
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log entry metrics: {e}")

    def log_llm_call(self, subject: str, purpose: str, prompt_length: int,
                    response_length: int, time_taken: float, temperature: float,
                    max_tokens: int):
        """Log LLM call metrics"""
        try:
            self.cursor.execute("""
                INSERT INTO llm_calls
                (timestamp, subject, purpose, prompt_length, response_length,
                 time_taken, temperature, max_tokens)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                subject,
                purpose,
                prompt_length,
                response_length,
                time_taken,
                temperature,
                max_tokens
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log LLM call: {e}")

    def log_validation_failure(self, subject: str, section_name: str,
                               failure_type: str, failure_message: str,
                               attempt_num: int):
        """Log validation failure"""
        try:
            self.cursor.execute("""
                INSERT INTO validation_failures
                (timestamp, subject, section_name, failure_type, failure_message, attempt_num)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                subject,
                section_name,
                failure_type,
                failure_message,
                attempt_num
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log validation failure: {e}")

    def log_resource_snapshot(self, vram_total: float, vram_used: float,
                             vram_free: float, ram_total: float, ram_used: float,
                             ram_free: float, cpu_percent: float):
        """Log resource snapshot"""
        try:
            self.cursor.execute("""
                INSERT INTO resource_snapshots
                (timestamp, vram_total_gb, vram_used_gb, vram_free_gb,
                 ram_total_gb, ram_used_gb, ram_free_gb, cpu_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                vram_total,
                vram_used,
                vram_free,
                ram_total,
                ram_used,
                ram_free,
                cpu_percent
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log resource snapshot: {e}")

    # ========================================================================
    # ANALYTICS METHODS
    # ========================================================================

    def get_failure_patterns(self, limit: int = 10) -> List[Dict]:
        """Get most common failure patterns"""
        try:
            self.cursor.execute("""
                SELECT failure_type, COUNT(*) as count,
                       AVG(attempt_num) as avg_attempts
                FROM validation_failures
                GROUP BY failure_type
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))

            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'failure_type': row[0],
                    'count': row[1],
                    'avg_attempts': row[2]
                })
            return results
        except Exception as e:
            logger.error(f"Failed to get failure patterns: {e}")
            return []

    def get_section_stats(self, section_num: int) -> Dict:
        """Get statistics for a specific section"""
        try:
            self.cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    AVG(word_count) as avg_words,
                    AVG(attempts) as avg_attempts,
                    AVG(time_taken) as avg_time,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
                FROM sections
                WHERE section_num = ?
            """, (section_num,))

            row = self.cursor.fetchone()
            return {
                'section_num': section_num,
                'total_generated': row[0],
                'avg_word_count': row[1],
                'avg_attempts': row[2],
                'avg_time_seconds': row[3],
                'success_count': row[4],
                'success_rate': (row[4] / row[0] * 100) if row[0] > 0 else 0
            }
        except Exception as e:
            logger.error(f"Failed to get section stats: {e}")
            return {}

    def get_recent_entries(self, limit: int = 10) -> List[Dict]:
        """Get recent entries"""
        try:
            self.cursor.execute("""
                SELECT subject, tier, category, total_word_count, total_time,
                       success, timestamp
                FROM entries
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'subject': row[0],
                    'tier': row[1],
                    'category': row[2],
                    'word_count': row[3],
                    'time_minutes': row[4] / 60,
                    'success': bool(row[5]),
                    'timestamp': row[6]
                })
            return results
        except Exception as e:
            logger.error(f"Failed to get recent entries: {e}")
            return []

    def get_performance_summary(self) -> Dict:
        """Get overall performance summary"""
        try:
            # Entry stats
            self.cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    AVG(total_time) as avg_time,
                    AVG(total_word_count) as avg_words
                FROM entries
            """)
            entry_row = self.cursor.fetchone()

            # Section stats
            self.cursor.execute("""
                SELECT
                    AVG(attempts) as avg_attempts,
                    AVG(time_taken) as avg_time
                FROM sections
            """)
            section_row = self.cursor.fetchone()

            # LLM stats
            self.cursor.execute("""
                SELECT
                    COUNT(*) as total_calls,
                    AVG(time_taken) as avg_time,
                    SUM(time_taken) as total_time
                FROM llm_calls
            """)
            llm_row = self.cursor.fetchone()

            return {
                'entries': {
                    'total': entry_row[0],
                    'successful': entry_row[1],
                    'success_rate': (entry_row[1] / entry_row[0] * 100) if entry_row[0] > 0 else 0,
                    'avg_time_minutes': entry_row[2] / 60 if entry_row[2] else 0,
                    'avg_word_count': entry_row[3]
                },
                'sections': {
                    'avg_attempts': section_row[0],
                    'avg_time_seconds': section_row[1]
                },
                'llm': {
                    'total_calls': llm_row[0],
                    'avg_time_seconds': llm_row[1],
                    'total_time_minutes': llm_row[2] / 60 if llm_row[2] else 0
                }
            }
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {}

    def get_vram_usage_over_time(self, limit: int = 100) -> List[Dict]:
        """Get VRAM usage history"""
        try:
            self.cursor.execute("""
                SELECT timestamp, vram_used_gb, vram_free_gb
                FROM resource_snapshots
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'timestamp': row[0],
                    'vram_used_gb': row[1],
                    'vram_free_gb': row[2]
                })
            return list(reversed(results))  # Oldest first
        except Exception as e:
            logger.error(f"Failed to get VRAM usage: {e}")
            return []

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def clear_old_data(self, days: int = 30):
        """Clear telemetry data older than specified days"""
        try:
            cutoff = datetime.now().isoformat()
            # This is a simplification - proper implementation would parse timestamps
            logger.info(f"Clearing data older than {days} days")

            for table in ['sections', 'entries', 'llm_calls', 'validation_failures', 'resource_snapshots']:
                self.cursor.execute(f"""
                    DELETE FROM {table}
                    WHERE datetime(timestamp) < datetime('now', '-{days} days')
                """)

            self.conn.commit()
            logger.info("Old telemetry data cleared")
        except Exception as e:
            logger.error(f"Failed to clear old data: {e}")

    def export_to_json(self, output_path: str):
        """Export all telemetry data to JSON"""
        try:
            data = {
                'entries': self.get_recent_entries(limit=1000),
                'failure_patterns': self.get_failure_patterns(limit=50),
                'performance_summary': self.get_performance_summary(),
                'section_stats': [self.get_section_stats(i) for i in range(6)]
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Telemetry data exported to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export data: {e}")

    def close(self):
        """Close database connection"""
        try:
            self.conn.close()
            logger.info("TelemetrySystem closed")
        except Exception as e:
            logger.error(f"Error closing telemetry: {e}")


# ============================================================================
# CLI TESTING
# ============================================================================

if __name__ == "__main__":
    """Test telemetry system"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print("=" * 80)
    print("OPUS MAXIMUS - TELEMETRY SYSTEM TEST")
    print("=" * 80)

    telemetry = TelemetrySystem(db_path='test_telemetry.db')

    # Log some test data
    print("\nLogging test data...")
    telemetry.log_section(
        subject="Darwin",
        tier="S",
        category="Science",
        section_num=0,
        section_name="I. Strategic Role",
        word_count=1850,
        attempts=2,
        time_taken=45.3,
        vram_used_gb=12.5,
        success=True,
        failures=[]
    )

    telemetry.log_validation_failure(
        subject="Darwin",
        section_name="I. Strategic Role",
        failure_type="format",
        failure_message="Missing 4-space indent",
        attempt_num=1
    )

    telemetry.log_llm_call(
        subject="Darwin",
        purpose="section",
        prompt_length=2500,
        response_length=9500,
        time_taken=8.3,
        temperature=0.9,
        max_tokens=10000
    )

    # Get stats
    print("\n" + "=" * 80)
    print("ANALYTICS")
    print("=" * 80)

    section_stats = telemetry.get_section_stats(0)
    print(f"\nSection 0 Stats:")
    print(f"  Total Generated: {section_stats.get('total_generated', 0)}")
    print(f"  Avg Word Count: {section_stats.get('avg_word_count', 0):.1f}")
    print(f"  Avg Attempts: {section_stats.get('avg_attempts', 0):.2f}")
    print(f"  Success Rate: {section_stats.get('success_rate', 0):.1f}%")

    failure_patterns = telemetry.get_failure_patterns()
    if failure_patterns:
        print(f"\nTop Failure Patterns:")
        for pattern in failure_patterns:
            print(f"  {pattern['failure_type']}: {pattern['count']} occurrences")

    telemetry.close()

    print("\n" + "=" * 80)
    print("Test completed. Database: test_telemetry.db")
    print("=" * 80)
