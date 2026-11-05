"""
HELZERX AI Support - Ticket Creation Modal
Presents a clean, structured modal asking for issue subject, description, and server identifier.
"""
from __future__ import annotations

import discord
from discord import ui
from typing import Optional

from bot.utils.logger import logger


class TicketCreateModal(ui.Modal):
    """Interactive modal prompting customer for issue details."""

    def __init__(self, category_id: str, category_name: str):
        super().__init__(title=f"Create Ticket • {category_name[:25]}")
        self.category_id = category_id
        self.category_name = category_name

        self.subject_input = ui.TextInput(
            label="Brief Summary of the Issue",
            placeholder="e.g. Server crashed after updating Paper jar",
            required=True,
            max_length=150
        )
        self.add_item(self.subject_input)

        self.description_input = ui.TextInput(
            label="Detailed Description & Steps to Reproduce",
            placeholder="Provide error logs, what changed, or specific symptoms...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )
        self.add_item(self.description_input)

        self.server_input = ui.TextInput(
            label="Server ID, Node, or IP (Optional)",
            placeholder="e.g. node-04 / srv-88321 or play.example.com",
            required=False,
            max_length=100
        )
        self.add_item(self.server_input)

    async def on_submit(self, interaction: discord.Interaction):
        # Defer interaction to give the bot time to create private channel and run AI triage
        await interaction.response.defer(ephemeral=True, thinking=True)

        from bot.tickets.manager import ticket_manager

        try:
            channel, ticket_code = await ticket_manager.create_ticket_channel(
                guild=interaction.guild,
                user=interaction.user,
                category_id=self.category_id,
                subject=self.subject_input.value,
                description=self.description_input.value,
                server_identifier=self.server_input.value or None
            )

            await interaction.followup.send(
                f"✅ **Ticket Created**: Your private support channel has been provisioned: {channel.mention} (`{ticket_code}`).",
                ephemeral=True
            )
        except ValueError as val_err:
            await interaction.followup.send(f"⚠️ {str(val_err)}", ephemeral=True)
        except Exception as e:
            logger.error(f"Error creating ticket for user {interaction.user.id}: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ An unexpected error occurred while creating your ticket. Please notify an administrator.",
                ephemeral=True
            )
