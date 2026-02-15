import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

APP_NAME = "kernhell"
CONFIG_DIR = Path.home() / f".{APP_NAME}"
KEYS_FILE = CONFIG_DIR / "keys.json"

SUPPORTED_PROVIDERS = ["google", "groq", "openrouter", "cloudflare", "nvidia"]

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

# Global Instance
config = ConfigManager()
