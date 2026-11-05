"""
HELZERX AI Support - Modern Discord Container / Components V2 Embeds
Provides clean container styling without side color lines, matching the official HelzerX layout.
"""
from __future__ import annotations

import discord
import datetime
from typing import Optional, List
from bot.config import config
from bot.panel_config import panel_config

# Discord dark theme background color (0x2B2D31) removes the left-side colored line
SEAMLESS_CONTAINER_COLOR = 0x2B2D31


def create_panel_embed(
    custom_title: Optional[str] = None,
    custom_desc: Optional[str] = None,
    banner_url: Optional[str] = None,
    top_image_url: Optional[str] = None,
    categories_text: Optional[str] = None,
    note_text: Optional[str] = None,
    footer_text: Optional[str] = None
) -> discord.Embed:
    """
    Creates the official HELZERX Customer Support Hub interactive panel embed.
    Formatted to match the user's HelzerX Support Center screenshot template.
    Uses seamless container color (0x2B2D31) to eliminate the vertical side color line.
    """
    title = custom_title or panel_config.title
    desc = custom_desc or panel_config.description
    cats = categories_text or panel_config.categories_list
    note = note_text or panel_config.note_text
    banner = banner_url or panel_config.bottom_banner_url
    top_logo = top_image_url or panel_config.top_image_url
    footer1 = panel_config.footer_line1
    footer2 = panel_config.footer_line2
    footer = footer_text or f"{footer1}\n{footer2}"

    # Build rich container description with markdown horizontal dividers
    description_blocks = [
        f"# {title}\n",
        desc.strip(),
        "\n---",
        f"__{panel_config.support_categories_title}__",
        cats.strip(),
        "\n---",
        f"ℹ️ **{panel_config.note_title}**",
        note.strip()
    ]

    embed = discord.Embed(
        description="\n\n".join(description_blocks),
        color=SEAMLESS_CONTAINER_COLOR,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

    # Top thumbnail logo (Chrome 3D HelzerX logo)
    if top_logo and top_logo.startswith("http"):
        embed.set_thumbnail(url=top_logo)

    # Bottom wide banner (HELZERX SUPPORT - YOUR TECH PARTNER)
    if banner and banner.startswith("http"):
        embed.set_image(url=banner)

    embed.set_footer(text=footer)
    return embed


def create_ticket_welcome_embed(
    ticket_code: str,
    creator: discord.Member | discord.User,
    category_name: str,
    priority: str,
    subject: Optional[str] = None,
    server_identifier: Optional[str] = None
) -> discord.Embed:
    """
    Creates the Container V2 ticket session card without side color line.
    """
    embed = discord.Embed(
        title=f"🎧 Ticket {ticket_code} • {category_name}",
        description=(
            f"Hello {creator.mention}, your private support channel is ready.\n"
            f"Our technical diagnostics session has started below. "
            f"You can also request human assistance at any time using the controls below."
        ),
        color=SEAMLESS_CONTAINER_COLOR,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

    # Metadata Container Block
    meta_lines = [
        f"**Reference:** `{ticket_code}`",
        f"**Category:** `{category_name}`",
        f"**Priority:** `{priority}`",
        f"**Customer:** {creator.mention}"
    ]
    if server_identifier:
        meta_lines.append(f"**Service / Node ID:** `{server_identifier}`")

    embed.add_field(
        name="📋 Session Attributes",
        value="\n".join(meta_lines),
        inline=False
    )

    if subject:
        embed.add_field(
            name="📌 Initial Issue Summary",
            value=f"> {subject}",
            inline=False
        )

    embed.add_field(
        name="⚙️ Interactive Controls",
        value="`[✋ Claim]` to assign staff • `[👤 Request Human]` to alert on-duty engineer • `[🔒 Close]` when resolved",
        inline=False
    )

    embed.set_footer(text=f"HelzerX Technologies • {ticket_code}")
    return embed


def create_escalation_embed(ticket_code: str, reason: str, priority: str = "HIGH") -> discord.Embed:
    """Container V2 embed when a ticket is escalated to human support."""
    embed = discord.Embed(
        title=f"🔔 Ticket {ticket_code} • Human Staff Summoned",
        description=(
            f"This ticket has been marked for **human engineer intervention**.\n"
            f"Automated diagnostics have been paused on this channel."
        ),
        color=SEAMLESS_CONTAINER_COLOR,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.add_field(name="Escalation Reason", value=f"```\n{reason}\n```", inline=False)
    embed.add_field(name="Priority Level", value=f"`{priority}`", inline=True)
    embed.set_footer(text="HelzerX Engineering Escalation Dispatched")
    return embed


def create_ticket_closed_embed(
    ticket_code: str,
    closed_by_name: str,
    reason: Optional[str] = None,
    total_messages: int = 0
) -> discord.Embed:
    """Container V2 embed displayed when a ticket is closed."""
    embed = discord.Embed(
        title=f"🔒 Ticket {ticket_code} Marked as Resolved",
        description="The support session has been concluded. An HTML transcript has been generated and archived.",
        color=SEAMLESS_CONTAINER_COLOR,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.add_field(name="Closed By", value=f"**{closed_by_name}**", inline=True)
    embed.add_field(name="Total Messages", value=f"`{total_messages}`", inline=True)
    if reason:
        embed.add_field(name="Resolution Summary", value=f"```\n{reason}\n```", inline=False)

    embed.set_footer(text="HelzerX Ticket Archived")
    return embed
