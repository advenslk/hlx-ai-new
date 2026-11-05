"""
HELZERX AI Support - Ticket Channel Control View
In-channel buttons for claiming, requesting human support, adding internal notes, and closing tickets.
"""
from __future__ import annotations

import discord
from discord import ui
from typing import Optional

from bot.config import config
from bot.security.permissions import is_staff_check
from bot.views.confirm_close_view import ConfirmCloseView


class InternalNoteModal(ui.Modal, title="Add Confidential Internal Note"):
    """Staff-only modal to attach a note invisible to the customer."""

    note_text = ui.TextInput(
        label="Internal Staff Note (Never visible to user)",
        style=discord.TextStyle.paragraph,
        placeholder="e.g. Node 4 is experiencing high I/O wait; migration scheduled...",
        required=True,
        max_length=1500
    )

    def __init__(self, ticket_code: str):
        super().__init__()
        self.ticket_code = ticket_code

    async def on_submit(self, interaction: discord.Interaction):
        from bot.staff.manager import staff_manager

        await staff_manager.add_note(
            channel_id=interaction.channel_id,
            staff_member=interaction.user,
            content=self.note_text.value
        )
        await interaction.response.send_message(
            "🔒 **Internal Note Saved**: This note is recorded in the database audit log and will not be displayed to the customer.",
            ephemeral=True
        )


class TicketControlView(ui.View):
    """Persistent control view placed in every active ticket channel."""

    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="Claim Ticket",
        style=discord.ButtonStyle.primary,
        custom_id="btn_ticket_claim",
        emoji="✋"
    )
    async def claim_button(self, interaction: discord.Interaction, button: ui.Button):
        if not is_staff_check(interaction):
            await interaction.response.send_message(
                "❌ **Staff Only**: Only authorized HELZERX Support Staff can claim tickets.",
                ephemeral=True
            )
            return

        from bot.staff.manager import staff_manager
        await staff_manager.claim_ticket(interaction.channel, interaction.user)
        button.disabled = True
        button.label = f"Claimed by {interaction.user.display_name[:15]}"
        button.style = discord.ButtonStyle.secondary
        await interaction.message.edit(view=self)
        await interaction.response.send_message(
            f"✅ **Ticket Claimed**: {interaction.user.mention} is now the primary assignee.",
            ephemeral=False
        )

    @ui.button(
        label="Request Human Staff",
        style=discord.ButtonStyle.secondary,
        custom_id="btn_ticket_request_human",
        emoji="👤"
    )
    async def request_human_button(self, interaction: discord.Interaction, button: ui.Button):
        from bot.tickets.manager import ticket_manager

        await ticket_manager.escalate_to_human(
            channel=interaction.channel,
            requested_by=interaction.user,
            reason="Customer clicked 'Request Human Staff' button"
        )
        await interaction.response.send_message(
            "🔔 **Escalation Dispatched**: An on-duty HELZERX engineer has been notified and will take over shortly.",
            ephemeral=False
        )

    @ui.button(
        label="Internal Note",
        style=discord.ButtonStyle.secondary,
        custom_id="btn_ticket_internal_note",
        emoji="📝"
    )
    async def internal_note_button(self, interaction: discord.Interaction, button: ui.Button):
        if not is_staff_check(interaction):
            await interaction.response.send_message(
                "❌ **Staff Only**: Internal notes are reserved exclusively for HELZERX staff.",
                ephemeral=True
            )
            return

        modal = InternalNoteModal(ticket_code=interaction.channel.name)
        await interaction.response.send_modal(modal)

    @ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="btn_ticket_close",
        emoji="🔒"
    )
    async def close_button(self, interaction: discord.Interaction, button: ui.Button):
        confirm_view = ConfirmCloseView(channel_id=interaction.channel_id)
        await interaction.response.send_message(
            "⚠️ **Confirm Closure**: Are you sure you want to mark this ticket as resolved and archive the channel?",
            view=confirm_view,
            ephemeral=False
        )
