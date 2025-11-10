"""
OPUS MAXIMUS - Multi-Tier Caching System
==========================================
Three-tier caching optimized for 32GB RAM:
- L1: Hot cache (RAM, 5000 entries)
- L2: Warm cache (RAM, 50000 entries)
- L3: Cold cache (Disk, compressed, unlimited)
"""

import json
import zlib
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from collections import OrderedDict
from dataclasses import dataclass
import time

from .error_handling import ResourceError

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class CacheEntry:
    """Single cache entry"""
    key: str
    value: Any
    timestamp: float
    size_bytes: int
    hit_count: int = 0


# ============================================================================
# LRU CACHE (for L1 and L2)
# ============================================================================

class LRUCache:
    """
    Least Recently Used (LRU) cache implementation.

    Features:
    - Fixed size limit
    - Automatic eviction of least recently used
    - Hit/miss tracking
    """

    def __init__(self, max_size: int, name: str = "cache"):
        """
        Initialize LRU cache.

        Args:
            max_size: Maximum number of entries
            name: Cache name (for logging)
        """
        self.max_size = max_size
        self.name = name
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0

        logger.debug(f"Initialized {name} with max_size={max_size}")

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry = self.cache[key]
            entry.hit_count += 1
            self.hits += 1

            logger.debug(f"{self.name} HIT: {key[:50]}")
            return entry.value
        else:
            self.misses += 1
            logger.debug(f"{self.name} MISS: {key[:50]}")
            return None

    def put(self, key: str, value: Any, size_bytes: Optional[int] = None):
        """
        Put value in cache.

        Args:
            key: Cache key
            value: Value to cache
            size_bytes: Optional size hint
        """
        # Estimate size if not provided
        if size_bytes is None:
            size_bytes = len(str(value))

        # Remove if already exists
        if key in self.cache:
            del self.cache[key]
        # Evict oldest if at capacity
        elif len(self.cache) >= self.max_size:
            evicted_key, evicted_entry = self.cache.popitem(last=False)
            logger.debug(f"{self.name} evicted: {evicted_key[:50]}")

        # Add new entry
        entry = CacheEntry(
            key=key,
            value=value,
            timestamp=time.time(),
            size_bytes=size_bytes
        )
        self.cache[key] = entry

        logger.debug(f"{self.name} PUT: {key[:50]} ({size_bytes} bytes)")

    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info(f"{self.name} cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0

        return {
            'name': self.name,
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'total_bytes': sum(e.size_bytes for e in self.cache.values())
        }


# ============================================================================
# DISK CACHE (for L3)
# ============================================================================

class DiskCache:
    """
    Compressed disk cache for long-term storage.

    Features:
    - zlib compression
    - Unlimited size
    - Persistent across sessions
    """

    def __init__(self, cache_dir: Path, compress: bool = True):
        """
        Initialize disk cache.

        Args:
            cache_dir: Directory to store cache files
            compress: Whether to compress cached data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.compress = compress
        self.hits = 0
        self.misses = 0

        logger.debug(f"Initialized disk cache: {cache_dir} (compress={compress})")

    def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache"""
        cache_file = self._get_cache_file(key)

        if not cache_file.exists():
            self.misses += 1
            return None

        try:
            with open(cache_file, 'rb') as f:
                data = f.read()

            # Decompress if needed
            if self.compress:
                data = zlib.decompress(data)

            value = json.loads(data.decode('utf-8'))
            self.hits += 1

            logger.debug(f"Disk cache HIT: {key[:50]}")
            return value

        except Exception as e:
            logger.warning(f"Failed to read from disk cache: {e}")
            self.misses += 1
            return None

    def put(self, key: str, value: Any):
        """Put value in disk cache"""
        cache_file = self._get_cache_file(key)

        try:
            # Serialize to JSON
            data = json.dumps(value, ensure_ascii=False).encode('utf-8')

            # Compress if enabled
            if self.compress:
                data = zlib.compress(data, level=6)

            # Write to disk
            with open(cache_file, 'wb') as f:
                f.write(data)

            logger.debug(f"Disk cache PUT: {key[:50]} ({len(data)} bytes)")

        except Exception as e:
            logger.error(f"Failed to write to disk cache: {e}")
            raise ResourceError(f"Disk cache write failed: {e}")

    def clear(self):
        """Clear all disk cache files"""
        count = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
            count += 1

        logger.info(f"Disk cache cleared ({count} files deleted)")
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get disk cache statistics"""
        files = list(self.cache_dir.glob("*.cache"))
        total_bytes = sum(f.stat().st_size for f in files)
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0

        return {
            'name': 'L3 (Disk)',
            'size': len(files),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'total_bytes': total_bytes
        }

    def _get_cache_file(self, key: str) -> Path:
        """Generate cache file path from key"""
        key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"


# ============================================================================
# MULTI-TIER CACHE
# ============================================================================

class MultiTierCache:
    """
    Three-tier cache system.

    Cache hierarchy:
    1. L1 (Hot): Small, fast RAM cache for frequent access
    2. L2 (Warm): Larger RAM cache for recent access
    3. L3 (Cold): Unlimited disk cache for all data

    On cache miss:
    - Check L1 → L2 → L3 → Return None
    - When found, promote to higher tier

    On cache put:
    - Write to L1, L2, and L3 simultaneously
    """

    def __init__(
        self,
        l1_size: int = 5000,
        l2_size: int = 50000,
        cache_dir: Path = Path(".cache"),
        enable_l3: bool = True
    ):
        """
        Initialize multi-tier cache.

        Args:
            l1_size: L1 cache size (hot)
            l2_size: L2 cache size (warm)
            cache_dir: Directory for L3 disk cache
            enable_l3: Whether to enable disk cache
        """
        self.l1 = LRUCache(l1_size, name="L1 (Hot)")
        self.l2 = LRUCache(l2_size, name="L2 (Warm)")

        if enable_l3:
            self.l3 = DiskCache(cache_dir, compress=True)
        else:
            self.l3 = None

        logger.info(
            f"Multi-tier cache initialized: "
            f"L1={l1_size}, L2={l2_size}, L3={'enabled' if enable_l3 else 'disabled'}"
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Checks L1 → L2 → L3 in order.
        Promotes found values to higher tiers.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        # Try L1
        value = self.l1.get(key)
        if value is not None:
            return value

        # Try L2
        value = self.l2.get(key)
        if value is not None:
            # Promote to L1
            self.l1.put(key, value)
            return value

        # Try L3
        if self.l3:
            value = self.l3.get(key)
            if value is not None:
                # Promote to L1 and L2
                self.l1.put(key, value)
                self.l2.put(key, value)
                return value

        return None

    def put(self, key: str, value: Any):
        """
        Put value in all cache tiers.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Write to all tiers
        self.l1.put(key, value)
        self.l2.put(key, value)

        if self.l3:
            self.l3.put(key, value)

    def clear(self):
        """Clear all cache tiers"""
        self.l1.clear()
        self.l2.clear()
        if self.l3:
            self.l3.clear()
        logger.info("All cache tiers cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all cache tiers"""
        stats = {
            'l1': self.l1.get_stats(),
            'l2': self.l2.get_stats(),
        }

        if self.l3:
            stats['l3'] = self.l3.get_stats()

        # Overall stats
        total_hits = stats['l1']['hits'] + stats['l2']['hits']
        total_misses = stats['l1']['misses'] + stats['l2']['misses']

        if self.l3:
            total_hits += stats['l3']['hits']
            total_misses += stats['l3']['misses']

        total_requests = total_hits + total_misses
        overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0

        stats['overall'] = {
            'total_hits': total_hits,
            'total_misses': total_misses,
            'hit_rate': overall_hit_rate
        }

        return stats

    def print_stats(self):
        """Print cache statistics (pretty format)"""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("CACHE STATISTICS")
        print("="*60)

        for tier in ['l1', 'l2', 'l3']:
            if tier not in stats:
                continue

            tier_stats = stats[tier]
            print(f"\n{tier_stats['name']}:")
            print(f"  Entries: {tier_stats['size']}")
            if 'max_size' in tier_stats:
                print(f"  Max: {tier_stats['max_size']}")
            print(f"  Hits: {tier_stats['hits']}")
            print(f"  Misses: {tier_stats['misses']}")
            print(f"  Hit Rate: {tier_stats['hit_rate']:.2%}")
            print(f"  Size: {tier_stats['total_bytes'] / 1024 / 1024:.2f} MB")

        print(f"\nOverall Hit Rate: {stats['overall']['hit_rate']:.2%}")
        print("="*60 + "\n")


# ============================================================================
# CACHE KEY GENERATORS
# ============================================================================

def make_cache_key(prefix: str, **kwargs) -> str:
    """
    Generate cache key from parameters.

    Args:
        prefix: Key prefix (e.g., "blueprint", "section")
        **kwargs: Key-value pairs to include

    Returns:
        Cache key string

    Example:
        key = make_cache_key("section", subject="Theosis", section="strategic_role")
    """
    parts = [prefix]
    for k, v in sorted(kwargs.items()):
        parts.append(f"{k}={v}")

    return "|".join(parts)


def hash_prompt(prompt: str) -> str:
    """
    Generate hash of prompt for caching.

    Args:
        prompt: Prompt text

    Returns:
        SHA256 hash (first 16 chars)
    """
    return hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16]
