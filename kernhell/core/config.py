import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

APP_NAME = "kernhell"
CONFIG_DIR = Path.home() / f".{APP_NAME}"
KEYS_FILE = CONFIG_DIR / "keys.json"
QUOTA_FILE = CONFIG_DIR / "quota.json"

SUPPORTED_PROVIDERS = ["google", "groq", "openrouter", "cloudflare", "nvidia"]


class QuotaTracker:
    """Persistent quota tracking across sessions"""
    
    def __init__(self):
        self.quota_file = QUOTA_FILE
        self.limits = {
            'google': 50,       # per day (free tier)
            'groq': 14400,      # per day (beta)
            'nvidia': 1000,     # per day (free credits)
            'openrouter': 200,  # per day (free tier)
            'cloudflare': 10000 # per day (workers free)
        }
        self.usage = self._load_usage()
        self._cleanup_old_dates()
    
    def _load_usage(self) -> Dict[str, Dict[str, int]]:
        """Load usage data from disk"""
        try:
            if self.quota_file.exists():
                with open(self.quota_file, 'r') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_usage(self):
        """Save usage data to disk"""
        try:
            with open(self.quota_file, 'w') as f:
                json.dump(self.usage, f, indent=4)
        except Exception:
            pass  # Fail silently if can't save
    
    def can_use(self, provider: str) -> bool:
        """Check if provider has quota remaining for today"""
        today = datetime.now().date().isoformat()
        used = self.usage.get(provider, {}).get(today, 0)
        limit = self.limits.get(provider, float('inf'))
        return used < limit
    
    def record_usage(self, provider: str):
        """Increment usage counter for today"""
        today = datetime.now().date().isoformat()
        if provider not in self.usage:
            self.usage[provider] = {}
        self.usage[provider][today] = self.usage[provider].get(today, 0) + 1
        self._save_usage()
    
    def get_usage(self, provider: str) -> int:
        """Get today's usage count for a provider"""
        today = datetime.now().date().isoformat()
        return self.usage.get(provider, {}).get(today, 0)
    
    def get_remaining(self, provider: str) -> int:
        """Get remaining quota for today"""
        limit = self.limits.get(provider, float('inf'))
        if limit == float('inf'):
            return 999999  # Unlimited
        used = self.get_usage(provider)
        return max(0, limit - used)
    
    def _cleanup_old_dates(self):
        """Remove usage data older than 7 days"""
        cutoff = (datetime.now().date() - timedelta(days=7)).isoformat()
        
        for provider in list(self.usage.keys()):
            for date in list(self.usage[provider].keys()):
                if date < cutoff:
                    del self.usage[provider][date]
        
        self._save_usage()


class ConfigManager:
    """
    Multi-Provider API Key Manager.
    Stores keys per provider: {"google": [...], "groq": [...], ...}
    Handles rotation within a provider and failover across providers.
    """
    def __init__(self):
        self._ensure_config_dir()
        self.provider_keys: Dict[str, List[str]] = self._load_keys()
        self.current_provider: str = self._detect_default_provider()
        self.current_key_index: int = 0
        self.quota_tracker = QuotaTracker()  # NEW: Quota tracking

    def _ensure_config_dir(self):
        if not CONFIG_DIR.exists():
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not KEYS_FILE.exists():
            self._save_keys({p: [] for p in SUPPORTED_PROVIDERS})

    def _load_keys(self) -> Dict[str, List[str]]:
        try:
            with open(KEYS_FILE, "r") as f:
                data = json.load(f)

            # Migration: old format was {"api_keys": [...]}
            if "api_keys" in data and isinstance(data["api_keys"], list):
                migrated = {p: [] for p in SUPPORTED_PROVIDERS}
                migrated["google"] = data["api_keys"]
                self._save_keys(migrated)
                return migrated

            # Ensure all providers exist
            for p in SUPPORTED_PROVIDERS:
                if p not in data:
                    data[p] = []
            return data

        except (json.JSONDecodeError, FileNotFoundError):
            return {p: [] for p in SUPPORTED_PROVIDERS}

    def _save_keys(self, keys: Dict[str, List[str]]):
        with open(KEYS_FILE, "w") as f:
            json.dump(keys, f, indent=4)

    def _detect_default_provider(self) -> str:
        """Returns first provider that has keys, or 'google' as default."""
        for p in SUPPORTED_PROVIDERS:
            if self.provider_keys.get(p):
                return p
        return "google"

    # --- Key Management ---

    def add_key(self, key: str, provider: str = "google") -> Tuple[bool, str]:
        provider = provider.lower()
        if provider not in SUPPORTED_PROVIDERS:
            return False, f"Unknown provider '{provider}'. Supported: {', '.join(SUPPORTED_PROVIDERS)}"
        if key in self.provider_keys.get(provider, []):
            return False, f"Key already exists for {provider}."

        self.provider_keys.setdefault(provider, []).append(key)
        self._save_keys(self.provider_keys)
        return True, f"Key added to [{provider}] pool."

    def remove_key(self, key: str, provider: str = None) -> Tuple[bool, str]:
        """Removes a key. If provider not specified, searches all providers."""
        if provider:
            provider = provider.lower()
            if key in self.provider_keys.get(provider, []):
                self.provider_keys[provider].remove(key)
                self._save_keys(self.provider_keys)
                return True, f"Key removed from [{provider}]."
            return False, f"Key not found in [{provider}]."

        # Search all providers
        for p in SUPPORTED_PROVIDERS:
            if key in self.provider_keys.get(p, []):
                self.provider_keys[p].remove(key)
                self._save_keys(self.provider_keys)
                return True, f"Key removed from [{p}]."
        return False, "Key not found in any provider."

    def prune_key(self, key: str, provider: str) -> Tuple[bool, str]:
        """Removes a specific dead key from a provider."""
        return self.remove_key(key, provider)

    # --- Key Rotation ---

    def get_active_key(self) -> Optional[str]:
        keys = self.provider_keys.get(self.current_provider, [])
        if not keys:
            return None
        return keys[self.current_key_index % len(keys)]

    def rotate_key(self) -> Optional[str]:
        """Rotates to next key in current provider."""
        keys = self.provider_keys.get(self.current_provider, [])
        if not keys:
            return None
        self.current_key_index = (self.current_key_index + 1) % len(keys)
        return self.get_active_key()

    def switch_provider(self) -> Optional[str]:
        """Switches to the next provider that has keys. Returns new provider name or None."""
        current_idx = SUPPORTED_PROVIDERS.index(self.current_provider)
        for i in range(1, len(SUPPORTED_PROVIDERS)):
            next_provider = SUPPORTED_PROVIDERS[(current_idx + i) % len(SUPPORTED_PROVIDERS)]
            if self.provider_keys.get(next_provider):
                self.current_provider = next_provider
                self.current_key_index = 0
                return next_provider
        return None

    def get_key_count(self, provider: str = None) -> int:
        if provider:
            return len(self.provider_keys.get(provider, []))
        return sum(len(v) for v in self.provider_keys.values())

    def get_all_providers_with_keys(self) -> Dict[str, List[str]]:
        return {p: keys for p, keys in self.provider_keys.items() if keys}
    
    # --- NEW: Quota Management Integration ---
    
    def can_use_provider(self, provider: str) -> bool:
        """Check if provider has both keys AND quota remaining"""
        has_keys = bool(self.provider_keys.get(provider))
        has_quota = self.quota_tracker.can_use(provider)
        return has_keys and has_quota
    
    def record_api_call(self, provider: str):
        """Record that an API call was made"""
        self.quota_tracker.record_usage(provider)
    
    def get_quota_status(self, provider: str) -> Dict[str, int]:
        """Get quota status for a provider"""
        return {
            'used': self.quota_tracker.get_usage(provider),
            'remaining': self.quota_tracker.get_remaining(provider),
            'limit': self.quota_tracker.limits.get(provider, 0)
        }

# Global Instance
config = ConfigManager()
