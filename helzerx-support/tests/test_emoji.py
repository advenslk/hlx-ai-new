"""
Unit tests for HELZERX EmojiLoader (bot/emoji.py).
Verifies defaults, emojis.json overrides, env overrides, category lookups,
guild emoji auto-loading, and runtime set/reload.
"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from bot.emoji import EmojiLoader, DEFAULT_EMOJIS


class TestEmojiLoader(unittest.TestCase):
    def test_defaults_loaded(self):
        """Verify all default emoji keys load cleanly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = EmojiLoader(file_path=Path(tmpdir) / "missing.json")
            self.assertEqual(loader.success, DEFAULT_EMOJIS["success"])
            self.assertEqual(loader["claim"], DEFAULT_EMOJIS["claim"])
            self.assertEqual(loader.category("general"), DEFAULT_EMOJIS["cat_general"])

    def test_json_override_and_reload(self):
        """Verify custom Discord emojis & Unicode overrides in emojis.json work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "emojis.json"
            json_path.write_text(
                json.dumps({
                    "_comment": "ignore me",
                    "success": "<:hzx_ok:123456789012345678>",
                    "cat_general": "🔥"
                }),
                encoding="utf-8"
            )
            loader = EmojiLoader(file_path=json_path)
            self.assertEqual(loader.success, "<:hzx_ok:123456789012345678>")
            self.assertEqual(loader.category("general"), "🔥")
            # Unmodified keys still fall back to defaults
            self.assertEqual(loader.lock, DEFAULT_EMOJIS["lock"])

            # Runtime set + save + reload
            loader.set("claim", "<a:wave:999888777666555444>", save=True)
            reloaded = EmojiLoader(file_path=json_path)
            self.assertEqual(reloaded.claim, "<a:wave:999888777666555444>")

    def test_env_override(self):
        """Verify EMOJI_<KEY> environment variables override JSON/defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["EMOJI_URGENT"] = "💥"
            try:
                loader = EmojiLoader(file_path=Path(tmpdir) / "missing.json")
                self.assertEqual(loader.urgent, "💥")
            finally:
                os.environ.pop("EMOJI_URGENT", None)

    def test_guild_auto_sync(self):
        """Verify load_from_guild matches hzx_<key> custom server emojis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = EmojiLoader(file_path=Path(tmpdir) / "missing.json")

            class FakeEmoji:
                def __init__(self, name, formatted):
                    self.name = name
                    self._formatted = formatted
                def __str__(self):
                    return self._formatted

            fake_guild = SimpleNamespace(emojis=[
                FakeEmoji("hzx_claim", "<:hzx_claim:111222333444555666>"),
                FakeEmoji("unrelated_emoji", "<:unrelated:999>"),
            ])
            matched = loader.load_from_guild(fake_guild)
            self.assertEqual(matched, 1)
            self.assertEqual(loader.claim, "<:hzx_claim:111222333444555666>")
