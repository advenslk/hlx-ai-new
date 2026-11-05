"""
HELZERX AI Support - Customizable Ticket Panel Configuration Store
Persists custom panel title, description, colors, banner images, and footers.
Designed to match the exact HelzerX Support Center Container layout.
"""
from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
from bot.config import config, BASE_DIR

CONFIG_FILE = BASE_DIR / "panel_config.json"


@dataclass
class CustomPanelConfig:
    # Header & Title
    title: str = "🎧 HelzerX Support Center 🎧"
    top_image_url: str = "" # URL for top logo (e.g. 3D metallic HelzerX logo)
    
    # Intro Description
    description: str = (
        "Need assistance? Our support team is here to help.\n\n"
        "Create a ticket by selecting the appropriate category below. "
        "Please provide clear details so our team can assist you efficiently."
    )
    
    # Categories Section
    support_categories_title: str = "Support Categories"
    categories_list: str = (
        "• 👥 **General Support**\n"
        "• 📚 **Cloud & Hosting**\n"
        "• 🖥️ **Technical Issues**\n"
        "• 💳 **Billing & Payments**\n"
        "• 🚀 **Partnerships & Business**"
    )
    
    # Note Section
    note_title: str = "Please Note"
    note_text: str = "Submit one ticket per issue and keep all related communication within your ticket."
    
    # Bottom Banner & Branding
    bottom_banner_url: str = "" # URL for lower banner (e.g. HELZERX SUPPORT - YOUR TECH PARTNER)
    footer_line1: str = "HelzerX Technologies"
    footer_line2: str = "© 2026 HelzerX Technologies (Pvt) Ltd. All rights reserved."
    
    # Dropdown Component Placeholder
    select_placeholder: str = "Select a ticket category"
    
    # Container Side Color: #2B2D31 blends into Discord embed background to remove the side color line
    side_color_hex: str = "#2B2D31"

    @classmethod
    def load(cls) -> "CustomPanelConfig":
        """Loads configuration from panel_config.json if present, else defaults."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls(**data)
            except Exception:
                pass
        return cls()

    def save(self) -> None:
        """Saves current configuration to panel_config.json."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2)
        except Exception:
            pass

    @property
    def color_int(self) -> int:
        """Parses color_hex to integer RGB for discord.Color (default 0x2B2D31 for seamless container)."""
        try:
            clean = self.side_color_hex.lstrip("#")
            return int(clean, 16)
        except Exception:
            return 0x2B2D31


panel_config = CustomPanelConfig.load()
