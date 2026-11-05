"""
HELZERX AI Support - Confirm Close View
Provides confirmation buttons before archiving and closing a support ticket.
"""
from __future__ import annotations

import discord
from discord import ui


class ConfirmCloseView(ui.View):
    """Confirmation buttons for ticket closure."""

    def __init__(self, channel_id: int):
        super().__init__(timeout=60)
        self.channel_id = channel_id

    @ui.button(label="Confirm & Close", style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm_button(self, interaction: discord.Interaction, button: ui.Button):
        from bot.tickets.manager import ticket_manager

        await interaction.response.defer()
        self.stop()
        await ticket_manager.close_ticket(
            channel=interaction.channel,
            closed_by=interaction.user,
            reason="Closed by user confirmation"
        )

    @ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_button(self, interaction: discord.Interaction, button: ui.Button):
        self.stop()
        await interaction.message.delete()
