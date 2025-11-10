"""
FILE 20: ERROR RECOVERY
=======================
Aggressive error handling and automatic recovery system.
Optimized for fast hardware (DDR5/NVMe) with rapid retry cycles.
File 20 of 20: Error Recovery
Optimized for: Fast Recovery Cycles (Edit 22)
"""
import logging
import time
from typing import Dict, Optional, Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorRecovery:
    """
    Aggressive error handling and recovery for fast hardware.
    Implements exponential backoff with tight caps for rapid retries
    on high-performance systems.
    """
    def __init__(self):
        self.recovery_log: list[Dict] = []
        # Edit 22: Aggressive settings for modern hardware (DDR5/NVMe)
        # These settings assume fast I/O and CPU, allowing for more frequent
        # retries without causing massive system hangs.
        self.max_retries = 5        # Increased attempts before giving up
        self.backoff_factor = 1.5   # Tighter backoff for faster retry cycles
        self.max_wait_time = 5.0    # Cap wait time at 5s (don't wait minutes on fast hardware)

    def execute_with_recovery(self, func: Callable, args: tuple = (), kwargs: Dict = None, 
                              strategy: str = "retry") -> Optional[Any]:
        """
        Execute any function with automatic aggressive recovery.
        Strategies:
          - 'retry': Attempt up to max_retries, then return None on failure.
          - 'raise': Attempt up to max_retries, then raise the last exception.
        """
        if kwargs is None: kwargs = {}
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                # Log the failure
                logger.warning(f"Operation {func.__name__} failed (Attempt {attempt+1}/{self.max_retries+1}). Error: {e}")
                
                if attempt < self.max_retries:
                    # Calculate wait time with exponential backoff, capped at max_wait_time
                    wait_time = min(self.backoff_factor ** attempt, self.max_wait_time)
                    logger.info(f"Retrying {func.__name__} in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    # Final failure after all retries
                    logger.error(f"Operation {func.__name__} failed permanently after {self.max_retries+1} attempts.")
                    self._log_failure(func.__name__, str(e))
                    
                    if strategy == "raise":
                        raise last_exception
                    return None

    def _log_failure(self, operation: str, error_msg: str):
        """Log permanent failure to internal history."""
        self.recovery_log.append({
            "operation": operation,
            "success": False,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        })

    def get_recovery_stats(self) -> Dict:
        """Get statistics on error recoveries."""
        total_failures = len(self.recovery_log)
        return {
            "total_permanent_failures": total_failures,
            "last_failure": self.recovery_log[-1] if self.recovery_log else None
        }

# Global instance
error_recovery = ErrorRecovery()