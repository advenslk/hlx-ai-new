"""
HELZERX AI Support - Discord Permission Decorators & Checkers
Strict role-based access control with robust Member resolution and error handling.
"""
from __future__ import annotations

import discord
from discord import app_commands
from typing import Callable, Any
from bot.config import config


def is_staff_check(interaction: discord.Interaction) -> bool:
    """Returns True if the interaction user is Server Owner, Administrator, or has a staff role."""
    if not interaction.guild:
        return False

    member = interaction.user if isinstance(interaction.user, discord.Member) else interaction.guild.get_member(interaction.user.id)
    if not member:
        return False

    # Server owner is always staff
    if member.id == interaction.guild.owner_id:
        return True

    # Administrators or Guild Managers are staff
    perms = getattr(member, "guild_permissions", None)
    if perms and (perms.administrator or perms.manage_guild or perms.manage_channels):
        return True

    # Check configured support roles
    user_roles = [r.id for r in getattr(member, "roles", [])]
    return config.is_support(user_roles)


def is_admin_check(interaction: discord.Interaction) -> bool:
    """Returns True if the interaction user is Server Owner, Administrator, or has an admin role."""
    if not interaction.guild:
        return False

    member = interaction.user if isinstance(interaction.user, discord.Member) else interaction.guild.get_member(interaction.user.id)
    if not member:
        return False

    # Server owner is always admin
    if member.id == interaction.guild.owner_id:
        return True

    perms = getattr(member, "guild_permissions", None)
    if perms and perms.administrator:
        return True

    user_roles = [r.id for r in getattr(member, "roles", [])]
    return config.is_admin(user_roles)


def require_staff():
    """Slash command decorator requiring Support Staff or Admin role."""
    async def predicate(interaction: discord.Interaction) -> bool:
        if not is_staff_check(interaction):
            msg = "❌ **Access Denied**: You require an authorized HELZERX Support Staff role or Administrator permissions to execute this command."
            if not interaction.response.is_done():
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                await interaction.followup.send(msg, ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)


def require_admin():
    """Slash command decorator requiring HELZERX Admin role."""
    async def predicate(interaction: discord.Interaction) -> bool:
        if not is_admin_check(interaction):
            msg = "❌ **Access Denied**: You require an authorized HELZERX Administrator role to execute this command."
            if not interaction.response.is_done():
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                await interaction.followup.send(msg, ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)
