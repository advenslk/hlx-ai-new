"""
HELZERX AI Support - Centralized Emoji Registry & Dynamic Emoji Loader
Allows customizing all bot emojis (Unicode or Discord custom `<:name:id>` / `<a:name:id>`)
via `emojis.json`, environment variables (`EMOJI_<KEY>`), guild auto-sync (`hzx_<key>`),
or editing `DEFAULT_EMOJIS` directly.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_EMOJIS_FILE = BASE_DIR / "emojis.json"

# ==============================================================================
# DEFAULT EMOJI MAP — Change any value here or override in emojis.json!
# Supports both standard Unicode emojis ("✅") and Discord custom emojis
# ("<:custom_name:123456789012345678>" or "<a:animated_name:123456789012345678>").
# ==============================================================================
DEFAULT_EMOJIS: Dict[str, str] = {
    # Status & Feedback
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "loading": "⏳",
    "urgent": "🚨",
    "security": "🛡️",
    "sync": "⚡",
    "reset": "🔄",
    "search": "🔍",

    # Panel & Ticket Controls
    "headset": "🎧",
    "panel": "📚",
    "claim": "✋",
    "human": "👤",
    "note": "📝",
    "lock": "🔒",
    "unlock": "🔓",
    "bell": "🔔",
    "transcript": "📄",
    "clipboard": "📋",
    "pin": "📌",
    "settings": "⚙️",
    "ai": "🤖",
    "trash": "🗑️",
    "back": "⬅️",

    # Ticket Categories
    "cat_general": "👥",
    "cat_cloud_hosting": "📚",
    "cat_technical": "🖥️",
    "cat_billing": "💳",
    "cat_partnership": "🚀",
    "cat_minecraft": "⛏️",
    "cat_vps": "🖥️",
    "cat_other": "❓",
}


class EmojiLoader:
    """Loads, resolves, and hot-reloads Unicode & Discord custom emojis."""

    def __init__(self, file_path: Optional[Path] = None, defaults: Optional[Dict[str, str]] = None):
        self.file_path: Path = Path(file_path) if file_path else DEFAULT_EMOJIS_FILE
        self._defaults: Dict[str, str] = dict(defaults or DEFAULT_EMOJIS)
        self._emojis: Dict[str, str] = {}
        self.reload()

    def reload(self) -> Dict[str, str]:
        """Reload emojis from defaults -> emojis.json -> environment variables."""
        merged: Dict[str, str] = dict(self._defaults)

        # 1. Merge overrides from emojis.json if present
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                if isinstance(raw, dict):
                    for key, val in raw.items():
                        if key.startswith("_"):
                            continue
                        if isinstance(val, str) and val.strip():
                            merged[key] = val.strip()
            except Exception:
                pass

        # 2. Merge optional environment variable overrides (e.g. EMOJI_SUCCESS, EMOJI_CLAIM)
        for key in list(merged.keys()):
            env_val = os.getenv(f"EMOJI_{key.upper()}")
            if env_val and env_val.strip():
                merged[key] = env_val.strip()

        # Also pick up any extra EMOJI_* env vars for custom user-added keys
        for env_key, env_val in os.environ.items():
            if env_key.startswith("EMOJI_") and env_val and env_val.strip():
                normalized = env_key[len("EMOJI_"):].lower()
                if normalized not in ("auto_sync_guild", "guild_prefix"):
                    merged[normalized] = env_val.strip()

        self._emojis = merged
        return dict(self._emojis)

    def save(self) -> bool:
        """Persist current emoji map to emojis.json."""
        try:
            payload: Dict[str, Any] = {
                "_comment": (
                    "Customize any emoji below with Unicode (e.g. '🔥') or Discord custom emojis "
                    "(e.g. '<:name:123456789012345678>' or '<a:name:123456789012345678>'). "
                    "Use /emojis-reload or /emoji-set in Discord to update without restarting."
                )
            }
            payload.update(self._emojis)
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def get(self, key: str, default: Optional[str] = None) -> str:
        """Fetch an emoji by key with optional fallback."""
        if key in self._emojis:
            return self._emojis[key]
        if key in self._defaults:
            return self._defaults[key]
        return default if default is not None else ""

    def set(self, key: str, value: str, save: bool = True) -> str:
        """Set or override an emoji key and optionally save to emojis.json."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Emoji value cannot be empty.")
        self._emojis[key] = cleaned
        if save:
            self.save()
        return cleaned

    def category(self, category_id: str, fallback: str = "🎫") -> str:
        """Convenience lookup for ticket category emojis (`cat_<category_id>`)."""
        return self.get(f"cat_{category_id}", fallback)

    def as_partial(self, key: str, default: Optional[str] = None) -> Any:
        """
        Converts an emoji entry into a `discord.PartialEmoji` for Buttons/Selects when discord.py
        is available, or returns the raw string as fallback.
        """
        raw = self.get(key, default)
        if not raw:
            return None
        try:
            import discord
            return discord.PartialEmoji.from_str(raw)
        except Exception:
            return raw

    def load_from_guild(self, guild: Any, prefix: str = "hzx_") -> int:
        """
        Auto-loads custom Discord server emojis matching `<prefix><key>` (e.g. `hzx_claim`, `hzx_success`).
        Returns the number of emoji keys matched and loaded from the guild.
        """
        if not guild or not hasattr(guild, "emojis"):
            return 0
        matched = 0
        prefix_lower = prefix.lower()
        for guild_emoji in getattr(guild, "emojis", []):
            name_lower = getattr(guild_emoji, "name", "").lower()
            if prefix_lower and not name_lower.startswith(prefix_lower):
                continue
            key = name_lower[len(prefix_lower):] if prefix_lower else name_lower
            if key in self._emojis or key in self._defaults:
                self._emojis[key] = str(guild_emoji)
                matched += 1
        return matched

    def all(self) -> Dict[str, str]:
        """Return a copy of all loaded emojis."""
        return dict(self._emojis)

    def keys(self):
        return self._emojis.keys()

    def __getitem__(self, key: str) -> str:
        return self.get(key)

    def __getattr__(self, name: str) -> str:
        if name.startswith("_"):
            raise AttributeError(name)
        if name in self._emojis:
            return self._emojis[name]
        if name in self._defaults:
            return self._defaults[name]
        raise AttributeError(f"Emoji key '{name}' not found in EmojiLoader.")


# Global singleton emoji loader instance
emojis = EmojiLoader()


def get_emoji(key: str, default: str = "") -> str:
    """Module-level helper to fetch an emoji by key."""
    return emojis.get(key, default)
