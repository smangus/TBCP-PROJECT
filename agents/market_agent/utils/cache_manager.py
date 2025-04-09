# agents/market_agent/utils/cache_manager.py

import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pickle

class CacheManager:
    """
    Manages caching of market data to reduce API calls and speed up responses.
    Handles expiration of cached data based on configurable TTL (time to live).
    """
    
    def __init__(self, cache_dir: str, default_ttl: int = 86400):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir (str): Directory to store cache files
            default_ttl (int): Default TTL in seconds (1 day default)
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        os.makedirs(cache_dir, exist_ok=True)
        
        # In-memory cache for faster repeated access
        self.memory_cache = {}
    
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """
        Get cached data if available and not expired.
        
        Args:
            key (str): Cache key
            ttl (Optional[int]): Override default TTL
            
        Returns:
            Optional[Any]: Cached data or None if not found/expired
        """
        # Check memory cache first
        if key in self.memory_cache:
            data, timestamp = self.memory_cache[key]
            if not self._is_expired(timestamp, ttl or self.default_ttl):
                return data
        
        # Check disk cache
        cache_path = os.path.join(self.cache_dir, f"{key}.json")
        pickle_path = os.path.join(self.cache_dir, f"{key}.pickle")
        
        # Try JSON format first (for simpler data)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                    
                timestamp = cache_data.get("_timestamp", 0)
                if not self._is_expired(timestamp, ttl or self.default_ttl):
                    data = cache_data.get("data")
                    # Update memory cache
                    self.memory_cache[key] = (data, timestamp)
                    return data
            except Exception as e:
                print(f"Error reading JSON cache for {key}: {e}")
        
        # Then try pickle format (for complex data)
        if os.path.exists(pickle_path):
            try:
                with open(pickle_path, 'rb') as f:
                    cache_data = pickle.load(f)
                    
                timestamp = cache_data.get("_timestamp", 0)
                if not self._is_expired(timestamp, ttl or self.default_ttl):
                    data = cache_data.get("data")
                    # Update memory cache
                    self.memory_cache[key] = (data, timestamp)
                    return data
            except Exception as e:
                print(f"Error reading pickle cache for {key}: {e}")
        
        return None
    
    def set(self, key: str, data: Any, use_pickle: bool = False) -> None:
        """
        Cache data.
        
        Args:
            key (str): Cache key
            data (Any): Data to cache
            use_pickle (bool): Whether to use pickle format instead of JSON
        """
        timestamp = int(time.time())
        
        # Update memory cache
        self.memory_cache[key] = (data, timestamp)
        
        # Prepare cache data
        cache_data = {
            "data": data,
            "_timestamp": timestamp
        }
        
        # Write to disk
        if use_pickle:
            cache_path = os.path.join(self.cache_dir, f"{key}.pickle")
            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump(cache_data, f)
            except Exception as e:
                print(f"Error writing pickle cache for {key}: {e}")
        else:
            cache_path = os.path.join(self.cache_dir, f"{key}.json")
            try:
                with open(cache_path, 'w') as f:
                    json.dump(cache_data, f, indent=2)
            except Exception as e:
                print(f"Error writing JSON cache for {key}: {e}")
    
    def invalidate(self, key: str) -> None:
        """
        Invalidate a specific cache entry.
        
        Args:
            key (str): Cache key to invalidate
        """
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Remove from disk cache
        cache_path = os.path.join(self.cache_dir, f"{key}.json")
        pickle_path = os.path.join(self.cache_dir, f"{key}.pickle")
        
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
            except Exception as e:
                print(f"Error removing JSON cache for {key}: {e}")
        
        if os.path.exists(pickle_path):
            try:
                os.remove(pickle_path)
            except Exception as e:
                print(f"Error removing pickle cache for {key}: {e}")
    
    def clear_all(self) -> None:
        """Clear all cached data."""
        # Clear memory cache
        self.memory_cache.clear()
        
        # Clear disk cache
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json') or filename.endswith('.pickle'):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                except Exception as e:
                    print(f"Error removing cache file {filename}: {e}")
    
    def _is_expired(self, timestamp: int, ttl: int) -> bool:
        """
        Check if a cached item has expired.
        
        Args:
            timestamp (int): Unix timestamp of when the item was cached
            ttl (int): TTL in seconds
            
        Returns:
            bool: True if expired, False otherwise
        """
        current_time = int(time.time())
        return current_time - timestamp > ttl
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the cache.
        
        Returns:
            Dict with cache statistics
        """
        json_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
        pickle_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pickle')]
        
        cache_size = 0
        for filename in json_files + pickle_files:
            try:
                cache_size += os.path.getsize(os.path.join(self.cache_dir, filename))
            except Exception:
                pass
        
        return {
            "memory_cache_entries": len(self.memory_cache),
            "disk_cache_entries": len(json_files) + len(pickle_files),
            "json_cache_entries": len(json_files),
            "pickle_cache_entries": len(pickle_files),
            "total_cache_size_bytes": cache_size,
            "total_cache_size_mb": round(cache_size / (1024 * 1024), 2)
        }
