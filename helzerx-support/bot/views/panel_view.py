"""
HELZERX AI Support - Ticket Panel View
Provides the category selection dropdown that launches the ticket modal.
"""
from __future__ import annotations

import discord
from discord import ui
from typing import Optional

from bot.config import config, TICKET_CATEGORIES
from bot.views.ticket_modal import TicketCreateModal


from bot.panel_config import panel_config


class CategorySelect(ui.Select):
    """Category dropdown menu for selecting support category."""

    def __init__(self, placeholder: Optional[str] = None):
        # 5 primary screenshot categories
        primary_ids = ["general", "cloud_hosting", "technical", "billing", "partnership"]
        options = [
            discord.SelectOption(
                label=TICKET_CATEGORIES[cat_id].name,
                value=cat_id,
                description=TICKET_CATEGORIES[cat_id].description[:100],
                emoji=TICKET_CATEGORIES[cat_id].emoji
            )
            for cat_id in primary_ids
            if cat_id in TICKET_CATEGORIES
        ]

        super().__init__(
            placeholder=placeholder or panel_config.select_placeholder or "Select a ticket category",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="helzerx_ticket_category_select"
        )

    async def callback(self, interaction: discord.Interaction):
        selected_category_id = self.values[0]
        cat_def = TICKET_CATEGORIES.get(selected_category_id)
        if not cat_def:
            await interaction.response.send_message("Invalid category selection.", ephemeral=True)
            return

        # Open ticket modal
        modal = TicketCreateModal(category_id=selected_category_id, category_name=cat_def.name)
        await interaction.response.send_modal(modal)


class TicketPanelView(ui.View):
    """Persistent View displayed on the main support ticket channel."""

    def __init__(self):
        super().__init__(timeout=None) # Persistent view
        self.add_item(CategorySelect())
