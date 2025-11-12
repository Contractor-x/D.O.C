"""
Cache manager for API responses and computed data.
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta
import os


class CacheManager:
    """Manages caching of API responses and computed data."""

    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key from input."""
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get full path for cache file."""
        return self.cache_dir / f"{cache_key}.cache"

    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """
        Store data in cache.

        Args:
            key: Cache key
            data: Data to cache
            ttl: Time-to-live in seconds
        """
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)

        cache_data = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'ttl': ttl or self.default_ttl
        }

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception:
            # If pickle fails, try JSON for simple data types
            try:
                cache_data['data'] = json.dumps(data, default=str)
                cache_data['format'] = 'json'
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, default=str)
            except Exception:
                pass  # Silently fail if caching is not possible

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve data from cache.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
        except Exception:
            # Try loading as JSON
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                if cache_data.get('format') == 'json':
                    cache_data['data'] = json.loads(cache_data['data'])
            except Exception:
                return None

        # Check if cache is expired
        timestamp = datetime.fromisoformat(cache_data['timestamp'])
        ttl = cache_data['ttl']

        if datetime.now() - timestamp > timedelta(seconds=ttl):
            # Cache expired, remove file
            cache_path.unlink(missing_ok=True)
            return None

        return cache_data['data']

    def delete(self, key: str) -> bool:
        """
        Delete cached data.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)

        if cache_path.exists():
            cache_path.unlink()
            return True
        return False

    def clear(self) -> int:
        """
        Clear all cached data.

        Returns:
            Number of files deleted
        """
        deleted_count = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
            deleted_count += 1
        return deleted_count

    def cleanup_expired(self) -> int:
        """
        Remove expired cache files.

        Returns:
            Number of files removed
        """
        removed_count = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)

                timestamp = datetime.fromisoformat(cache_data['timestamp'])
                ttl = cache_data['ttl']

                if datetime.now() - timestamp > timedelta(seconds=ttl):
                    cache_file.unlink()
                    removed_count += 1
            except Exception:
                # If we can't read the file, remove it
                cache_file.unlink()
                removed_count += 1

        return removed_count

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the cache.

        Returns:
            Cache statistics
        """
        total_files = len(list(self.cache_dir.glob("*.cache")))
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.cache"))

        return {
            'cache_dir': str(self.cache_dir),
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }


class MemoryCache:
    """In-memory cache for frequently accessed data."""

    def __init__(self, max_size: int = 1000):
        """
        Initialize memory cache.

        Args:
            max_size: Maximum number of items to cache
        """
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}

    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """
        Store data in memory cache.

        Args:
            key: Cache key
            data: Data to cache
            ttl: Time-to-live in seconds
        """
        if len(self.cache) >= self.max_size:
            # Remove least recently used item
            lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
            del self.cache[lru_key]
            del self.access_times[lru_key]

        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now(),
            'ttl': ttl
        }
        self.access_times[key] = datetime.now()

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve data from memory cache.

        Args:
            key: Cache key

        Returns:
            Cached data or None
        """
        if key not in self.cache:
            return None

        cache_item = self.cache[key]
        timestamp = cache_item['timestamp']
        ttl = cache_item.get('ttl')

        # Check TTL
        if ttl and datetime.now() - timestamp > timedelta(seconds=ttl):
            del self.cache[key]
            del self.access_times[key]
            return None

        # Update access time
        self.access_times[key] = datetime.now()
        return cache_item['data']

    def clear(self) -> int:
        """
        Clear memory cache.

        Returns:
            Number of items cleared
        """
        count = len(self.cache)
        self.cache.clear()
        self.access_times.clear()
        return count
