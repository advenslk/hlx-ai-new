"""
HELZERX AI Support - Global Error Handler
Captures unhandled Discord interaction and event errors with detailed logging.
"""
from __future__ import annotations

import discord
from discord import app_commands
from bot.utils.logger import logger


async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    """Handles exceptions raised during slash command execution."""
    if isinstance(error, app_commands.CheckFailure):
        # Already handled by check predicates
        return
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"⏳ **Cooldown**: Please wait `{error.retry_after:.1f}` seconds before reusing this command.",
            ephemeral=True
        )
    else:
        logger.error(f"Command Error in /{interaction.command.name if interaction.command else 'unknown'}: {error}", exc_info=True)
        msg = "❌ An unexpected internal error occurred while executing this command."
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
