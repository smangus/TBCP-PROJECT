# agents/ip_agent/utils/cache_manager.py

import os
import json
import pickle
import hashlib
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

class CacheManager:
    """
    Manages caching of data to reduce API calls and improve performance.
    """
    
    def __init__(self, cache_dir: str, default_ttl: int = 86400):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store the cache files
            default_ttl: Default time-to-live in seconds (24 hours)
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            ttl: Time-to-live in seconds (optional, uses default if not specified)
            
        Returns:
            The cached value or None if not found or expired
        """
        if ttl is None:
            ttl = self.default_ttl
            
        cache_file = self._get_cache_file_path(key)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                metadata = pickle.load(f)
                data = pickle.load(f)
                
            # Check if cache is expired
            created_at = metadata.get('created_at', datetime.min)
            if (datetime.now() - created_at).total_seconds() > ttl:
                return None
                
            return data
        except Exception as e:
            print(f"Error retrieving from cache: {e}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_file = self._get_cache_file_path(key)
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            
            # Create metadata
            metadata = {
                'created_at': datetime.now(),
                'key': key
            }
            
            # Write to cache file
            with open(cache_file, 'wb') as f:
                pickle.dump(metadata, f)
                pickle.dump(value, f)
                
            return True
        except Exception as e:
            print(f"Error writing to cache: {e}")
            return False
    
    def invalidate(self, key: str) -> bool:
        """
        Remove a key from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        cache_file = self._get_cache_file_path(key)
        
        if not os.path.exists(cache_file):
            return True
            
        try:
            os.remove(cache_file)
            return True
        except Exception as e:
            print(f"Error invalidating cache: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        Clear the entire cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
    
    def _get_cache_file_path(self, key: str) -> str:
        """
        Convert a cache key to a file path.
        
        Args:
            key: Cache key
            
        Returns:
            File path for the cache key
        """
        # Create a hash of the key for the filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")
