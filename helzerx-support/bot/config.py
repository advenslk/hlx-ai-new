"""
HELZERX AI Support - Central Configuration Module
Handles environment variables, type coercion, defaults, and category specifications.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Dict, Any
from pathlib import Path

# Load .env file from root or local directory
BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        try:
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass


@dataclass(frozen=True)
class TicketCategoryDef:
    id: str
    name: str
    description: str
    emoji: str
    default_priority: str
    department: str


# Official HELZERX Ticket Categories (Aligned with Screenshot Template)
TICKET_CATEGORIES: Dict[str, TicketCategoryDef] = {
    "general": TicketCategoryDef(
        id="general",
        name="General Support",
        description="General questions about HELZERX services and accounts",
        emoji="👥",
        default_priority="NORMAL",
        department="Customer Service"
    ),
    "cloud_hosting": TicketCategoryDef(
        id="cloud_hosting",
        name="Cloud & Hosting",
        description="VPS, Dedicated servers, Minecraft & cloud infrastructure",
        emoji="📚",
        default_priority="HIGH",
        department="Infrastructure Operations"
    ),
    "technical": TicketCategoryDef(
        id="technical",
        name="Technical Issues",
        description="OS, networking, Docker, SSL, and general server problems",
        emoji="🖥️",
        default_priority="NORMAL",
        department="Technical Support"
    ),
    "billing": TicketCategoryDef(
        id="billing",
        name="Billing & Payments",
        description="Invoices, payment gateways, subscriptions, renewals, refunds",
        emoji="💳",
        default_priority="NORMAL",
        department="Billing & Finance"
    ),
    "partnership": TicketCategoryDef(
        id="partnership",
        name="Partnerships & Business",
        description="Affiliate programs, sponsorships, enterprise inquiries",
        emoji="🚀",
        default_priority="LOW",
        department="Management"
    ),
    "minecraft": TicketCategoryDef(
        id="minecraft",
        name="Minecraft Hosting",
        description="Paper/Purpur, Pterodactyl, plugin issues, crash reports, ports",
        emoji="⛏️",
        default_priority="NORMAL",
        department="Game Server Operations"
    ),
    "vps": TicketCategoryDef(
        id="vps",
        name="VPS Support",
        description="KVM VPS provisioning, reinstallation, kernel, network routing",
        emoji="🖥️",
        default_priority="HIGH",
        department="Infrastructure Team"
    ),
    "other": TicketCategoryDef(
        id="other",
        name="Other Inquiries",
        description="Uncategorized questions and custom requests",
        emoji="❓",
        default_priority="NORMAL",
        department="Customer Service"
    ),
}


class Config:
    """Runtime configuration container loaded from environment variables."""

    # Discord Credentials
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    DISCORD_GUILD_ID: int = int(os.getenv("DISCORD_GUILD_ID", "0"))
    TICKET_CATEGORY_ID: int = int(os.getenv("TICKET_CATEGORY_ID", "0"))
    TRANSCRIPT_CHANNEL_ID: int = int(os.getenv("TRANSCRIPT_CHANNEL_ID", "0"))
    STAFF_LOG_CHANNEL_ID: int = int(os.getenv("STAFF_LOG_CHANNEL_ID", "0"))

    # Roles
    _support_roles_raw = os.getenv("SUPPORT_ROLE_IDS", "")
    SUPPORT_ROLE_IDS: List[int] = [
        int(r.strip()) for r in _support_roles_raw.split(",") if r.strip().isdigit()
    ]
    _admin_roles_raw = os.getenv("ADMIN_ROLE_IDS", "")
    ADMIN_ROLE_IDS: List[int] = [
        int(r.strip()) for r in _admin_roles_raw.split(",") if r.strip().isdigit()
    ]

    # NVIDIA NIM AI Configuration
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")

    AI_MAX_CONTEXT_TOKENS: int = int(os.getenv("AI_MAX_CONTEXT_TOKENS", "8192"))
    AI_MAX_RESPONSE_TOKENS: int = int(os.getenv("AI_MAX_RESPONSE_TOKENS", "1024"))
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.3"))
    AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "45"))
    AI_MAX_RETRIES: int = int(os.getenv("AI_MAX_RETRIES", "3"))
    AI_AUTO_RESPONSE_ENABLED: bool = os.getenv("AI_AUTO_RESPONSE_ENABLED", "true").lower() in ("true", "1", "yes")

    # Database URLs
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///helzerx_support.db"
    )
    SYNC_DATABASE_URL: str = os.getenv(
        "SYNC_DATABASE_URL",
        "sqlite:///helzerx_support.db"
    )
    SQLITE_FALLBACK: bool = os.getenv("SQLITE_FALLBACK", "true").lower() in ("true", "1", "yes")

    # Security & Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "6"))
    PROMPT_INJECTION_FILTER_LEVEL: str = os.getenv("PROMPT_INJECTION_FILTER_LEVEL", "HIGH").upper()
    MASK_SENSITIVE_DATA: bool = os.getenv("MASK_SENSITIVE_DATA", "true").lower() in ("true", "1", "yes")

    # HELZERX Brand
    BRAND_NAME: str = os.getenv("BRAND_NAME", "HELZERX")
    BRAND_COLOR: int = 0x5865F2         # Blurple brand
    BRAND_SUCCESS: int = 0x10B981       # Emerald
    BRAND_WARNING: int = 0xF59E0B       # Amber
    BRAND_DANGER: int = 0xEF4444        # Red
    BRAND_DARK: int = 0x0F172A          # Deep Slate
    BRAND_FOOTER: str = os.getenv("BRAND_FOOTER", "HELZERX AI Support Engine • Enterprise Tier")
    BRAND_LOGO_URL: str = os.getenv("BRAND_LOGO_URL", "https://helzerx.com/assets/logo.png")

    @classmethod
    def is_support(cls, role_ids: List[int]) -> bool:
        """Check if any of the user's role IDs match support or admin roles."""
        all_staff = set(cls.SUPPORT_ROLE_IDS + cls.ADMIN_ROLE_IDS)
        return bool(all_staff.intersection(set(role_ids)))

    @classmethod
    def is_admin(cls, role_ids: List[int]) -> bool:
        """Check if any of the user's role IDs match admin roles."""
        return bool(set(cls.ADMIN_ROLE_IDS).intersection(set(role_ids)))


config = Config()
