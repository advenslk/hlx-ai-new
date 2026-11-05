"""
HELZERX AI Support - Ticket Panel Configuration Store
Matches the exact Ticket Panel and Container Builder control layout.
"""
from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from bot.config import config, BASE_DIR

CONFIG_FILE = BASE_DIR / "panel_config.json"


@dataclass
class CustomPanelConfig:
    # Header & Title
    title: str = "🎧 HelzerX Support Center 🎧"
    top_image_url: str = "/assets/helzerx-logo-3d.png"
    
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
    active_category_ids: List[str] = field(default_factory=lambda: [
        "general", "cloud_hosting", "technical", "billing", "partnership"
    ])
    
    # Note Section
    note_title: str = "Please Note"
    note_text: str = "Submit one ticket per issue and keep all related communication within your ticket."
    
    # Bottom Banner & Branding
    bottom_banner_url: str = "/assets/helzerx-banner.png"
    footer_line1: str = "HelzerX Technologies"
    footer_line2: str = "© 2026 HelzerX Technologies (Pvt) Ltd. All rights reserved."
    
    # Dropdown Component Placeholder
    select_placeholder: str = "Select a ticket category"
    
    # Panel Status & Logistics
    is_active: bool = True
    target_channel_id: Optional[int] = None
    logs_channel_id: Optional[int] = None
    
    # Container Accent Color ('none' or hex, default 0x2B2D31 for seamless container without side lines)
    side_color_hex: str = "#2B2D31"
    accent_color_label: str = "none"

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

    @property
    def status_display(self) -> str:
        return "Active" if self.is_active else "Disabled"

    @property
    def categories_display(self) -> str:
        total = 5
        active = len(self.active_category_ids)
        return f"{active}/{total} active"


panel_config = CustomPanelConfig.load()
