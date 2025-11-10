"""
FILE 19: CACHING SYSTEM
=======================
Multi-level caching system optimized for high-RAM (32GB+) environments.
Implements L1 (Fast RAM), L2 (Secondary RAM), and L3 (Disk) caching tiers.
File 19 of 20: Caching System
Optimized for: 32GB RAM Scaling (Edit 21)
"""
import logging
import pickle
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class CachingSystem:
    """
    Multi-level caching system optimized for 32GB RAM.
    L1: Ultra-fast, small, most recently used items.
    L2: Larger RAM cache for working set.
    L3: Disk-based persistent cache for large objects/long-term storage.
    """
    def __init__(self, cache_dir: Path = Path(".cache")):
        self.cache_dir = cache_dir
        self.l1_cache: Dict[str, Any] = {} # Fast RAM cache
        self.l2_cache: Dict[str, Any] = {} # Secondary RAM cache
        self.l3_path = cache_dir / "l3"    # Disk cache
        self.l3_path.mkdir(parents=True, exist_ok=True)
        
        # Edit 21: Scale cache sizes for 32GB RAM target
        # These values are significantly higher than standard 16GB configurations
        self.l1_max_size = 5000   # Increased 5x for immediate hot objects
        self.l2_max_size = 50000  # Increased 5x for active working set
        
        self.hit_count = 0
        self.miss_count = 0
        self.total_requests = 0

    def get(self, key: str) -> Optional[Any]:
        """Get item from tiered cache."""
        self.total_requests += 1
        
        # Level 1: Fast RAM
        if key in self.l1_cache:
            self.hit_count += 1
            # Move to front (simple LRU via re-insertion in Python 3.7+)
            val = self.l1_cache.pop(key)
            self.l1_cache[key] = val
            return val
            
        # Level 2: Secondary RAM
        if key in self.l2_cache:
            self.hit_count += 1
            # Promote to L1
            val = self.l2_cache.pop(key)
            self._set_l1(key, val)
            return val
            
        # Level 3: Disk
        val = self._get_l3(key)
        if val is not None:
            self.hit_count += 1
            # Promote to L2 on disk read (don't clog L1 with cold storage items yet)
            self._set_l2(key, val)
            return val

        self.miss_count += 1
        return None

    def set(self, key: str, value: Any, level: int = 1):
        """Set value in specific cache tier (defaults to L1)."""
        if level == 1:
            self._set_l1(key, value)
        elif level == 2:
            self._set_l2(key, value)
        elif level >= 3:
            self._set_l3(key, value)

    def _set_l1(self, key: str, value: Any):
        """Internal set for L1 with eviction to L2."""
        if key in self.l1_cache:
             del self.l1_cache[key]
        elif len(self.l1_cache) >= self.l1_max_size:
            # Evict least recently used (first item) to L2
            oldest_key = next(iter(self.l1_cache))
            oldest_val = self.l1_cache.pop(oldest_key)
            self._set_l2(oldest_key, oldest_val)
            
        self.l1_cache[key] = value

    def _set_l2(self, key: str, value: Any):
        """Internal set for L2 with pure eviction."""
        if key in self.l2_cache:
            del self.l2_cache[key]
        elif len(self.l2_cache) >= self.l2_max_size:
             # Evict least recently used (first item) completely
             # Optional: could demote to L3 here if persistence is critical
             self.l2_cache.pop(next(iter(self.l2_cache)))
             
        self.l2_cache[key] = value

    def _get_l3(self, key: str) -> Optional[Any]:
        """Internal get from L3 disk cache."""
        cache_file = self.l3_path / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"L3 cache read failed for {key}: {e}")
                return None
        return None

    def _set_l3(self, key: str, value: Any):
        """Internal set for L3 disk cache."""
        try:
            with open(self.l3_path / f"{key}.pkl", 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            logger.error(f"L3 cache write failed for {key}: {e}")

    def clear_ram_caches(self):
        """Emergency clear of RAM caches if VRAM/RAM pressure is high."""
        logger.info(f"Clearing RAM caches. Freed L1: {len(self.l1_cache)}, L2: {len(self.l2_cache)} items.")
        self.l1_cache.clear()
        self.l2_cache.clear()

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        hit_rate = (self.hit_count / self.total_requests) * 100 if self.total_requests > 0 else 0
        return {
            "l1_size": len(self.l1_cache),
            "l2_size": len(self.l2_cache),
            "requests": self.total_requests,
            "hits": self.hit_count,
            "misses": self.miss_count,
            "hit_rate": f"{hit_rate:.1f}%"
        }

# Global instance
caching_system = CachingSystem()