"""
HELZERX AI Support - Exact Ticket Panel Setup & Container Builder
Replicates the exact Discord Ticket Panel control dashboard and container builder from user screenshots.
Supports *panel, !panel, !panel-setup, /panel, and /panel-setup.
"""
from __future__ import annotations

import discord
from discord import app_commands, ui
from discord.ext import commands
from typing import Optional, List

from bot.config import config, TICKET_CATEGORIES
from bot.panel_config import panel_config, CustomPanelConfig
from bot.security.permissions import require_admin
from bot.embeds.ticket_embeds import create_panel_embed, SEAMLESS_CONTAINER_COLOR
from bot.views.panel_view import TicketPanelView
from bot.utils.logger import logger


# ==========================================
# INTERACTIVE MODALS FOR TICKET PANEL
# ==========================================

class EditNameModal(ui.Modal, title="Edit Ticket Panel Name"):
    name_input = ui.TextInput(
        label="Panel Title / Name",
        placeholder="e.g. 🎧 HelzerX Support Center 🎧",
        default=panel_config.title[:100],
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        panel_config.title = self.name_input.value.strip()
        panel_config.save()
        embed = build_ticket_panel_control_embed()
        view = TicketPanelControlView()
        await interaction.response.edit_message(embed=embed, view=view)


class EditMessageModal(ui.Modal, title="Edit Panel Message"):
    intro_input = ui.TextInput(
        label="Introduction / Subtitle",
        style=discord.TextStyle.paragraph,
        placeholder="Need assistance? Our support team is here to help...",
        default=panel_config.description[:1000],
        required=True,
        max_length=1500
    )
    note_input = ui.TextInput(
        label="Please Note Callout",
        style=discord.TextStyle.paragraph,
        placeholder="Submit one ticket per issue and keep all related communication within your ticket.",
        default=panel_config.note_text[:400],
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        panel_config.description = self.intro_input.value.strip()
        panel_config.note_text = self.note_input.value.strip()
        panel_config.save()
        embed = build_ticket_panel_control_embed()
        view = TicketPanelControlView()
        await interaction.response.edit_message(embed=embed, view=view)


class EditPlaceholderModal(ui.Modal, title="Edit Dropdown Placeholder"):
    placeholder_input = ui.TextInput(
        label="Dropdown Placeholder",
        placeholder="e.g. Select a ticket category",
        default=panel_config.select_placeholder[:100],
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        panel_config.select_placeholder = self.placeholder_input.value.strip() or "Select a ticket category"
        panel_config.save()
        embed = build_ticket_panel_control_embed()
        view = TicketPanelControlView()
        await interaction.response.edit_message(embed=embed, view=view)


class ConfigureLogsModal(ui.Modal, title="Configure Ticket Logs Channel"):
    channel_input = ui.TextInput(
        label="Transcript / Logs Channel ID or Mention",
        placeholder="e.g. 123456789012345678 or #support-logs",
        default=str(panel_config.logs_channel_id or "") if panel_config.logs_channel_id else "",
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        raw = self.channel_input.value.strip().replace("<#", "").replace(">", "")
        if raw.isdigit():
            panel_config.logs_channel_id = int(raw)
            panel_config.save()
            embed = build_ticket_panel_control_embed()
            view = TicketPanelControlView()
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.send_message("❌ Invalid channel ID. Please provide a numeric ID or mention.", ephemeral=True)


class ManageCategoriesSelect(ui.Select):
    """Multi-select menu for enabling or disabling ticket categories."""

    def __init__(self):
        primary_categories = [
            ("general", "General Support", "👥"),
            ("cloud_hosting", "Cloud & Hosting", "📚"),
            ("technical", "Technical Issues", "🖥️"),
            ("billing", "Billing & Payments", "💳"),
            ("partnership", "Partnerships & Business", "🚀")
        ]
        options = [
            discord.SelectOption(
                label=name,
                value=cat_id,
                emoji=emoji,
                default=cat_id in panel_config.active_category_ids
            )
            for cat_id, name, emoji in primary_categories
        ]
        super().__init__(
            placeholder="Select active ticket categories...",
            min_values=1,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        panel_config.active_category_ids = self.values
        panel_config.save()
        embed = build_ticket_panel_control_embed()
        view = TicketPanelControlView()
        await interaction.response.edit_message(embed=embed, view=view)


class ManageCategoriesView(ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(ManageCategoriesSelect())

    @ui.button(label="Back to Panel Control", style=discord.ButtonStyle.secondary, emoji="⬅️")
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        embed = build_ticket_panel_control_embed()
        view = TicketPanelControlView()
        await interaction.response.edit_message(embed=embed, view=view)


class DeleteConfirmView(ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @ui.button(label="Confirm Reset / Delete", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirm_delete(self, interaction: discord.Interaction, button: ui.Button):
        global panel_config
        panel_config = CustomPanelConfig()
        panel_config.save()
        embed = build_ticket_panel_control_embed()
        view = TicketPanelControlView()
        await interaction.response.edit_message(content="✅ **Ticket Panel Reset to Factory Defaults!**", embed=embed, view=view)

    @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_delete(self, interaction: discord.Interaction, button: ui.Button):
        embed = build_ticket_panel_control_embed()
        view = TicketPanelControlView()
        await interaction.response.edit_message(content=None, embed=embed, view=view)


# ==========================================
# EXACT TICKET PANEL CONTROL VIEW (SCREENSHOT 2)
# ==========================================

def build_ticket_panel_control_embed() -> discord.Embed:
    """
    Builds the exact dashboard embed matching the user's screenshot:
    📚 Ticket Panel
    Status: Active
    Categories: 5/5 active
    """
    embed = discord.Embed(
        title="📚 Ticket Panel",
        description=(
            f"**Status:** {panel_config.status_display}\n"
            f"**Categories:** {panel_config.categories_display}"
        ),
        color=SEAMLESS_CONTAINER_COLOR
    )
    if panel_config.logs_channel_id:
        embed.add_field(name="Logs Channel", value=f"<#{panel_config.logs_channel_id}>", inline=True)
    return embed


class TicketPanelControlView(ui.View):
    """
    Exact button layout matching Screenshot 2:
    [Edit Name] [Edit Message]
    [Edit Placeholder]
    [Disable Panel] [Manage Categories]
    [Configure Logs]
    [Send Panel] [Delete Panel]
    """

    def __init__(self):
        super().__init__(timeout=None)

        # Update disable/enable button label and style based on state
        self.toggle_panel_btn.label = "Disable Panel" if panel_config.is_active else "Enable Panel"
        self.toggle_panel_btn.style = discord.ButtonStyle.danger if panel_config.is_active else discord.ButtonStyle.success

    # Row 0
    @ui.button(label="Edit Name", style=discord.ButtonStyle.secondary, row=0)
    async def edit_name_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EditNameModal())

    @ui.button(label="Edit Message", style=discord.ButtonStyle.secondary, row=0)
    async def edit_message_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EditMessageModal())

    # Row 1
    @ui.button(label="Edit Placeholder", style=discord.ButtonStyle.secondary, row=1)
    async def edit_placeholder_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(EditPlaceholderModal())

    # Row 2
    @ui.button(label="Disable Panel", style=discord.ButtonStyle.danger, row=2)
    async def toggle_panel_btn(self, interaction: discord.Interaction, button: ui.Button):
        panel_config.is_active = not panel_config.is_active
        panel_config.save()
        embed = build_ticket_panel_control_embed()
        view = TicketPanelControlView()
        await interaction.response.edit_message(embed=embed, view=view)

    @ui.button(label="Manage Categories", style=discord.ButtonStyle.primary, row=2)
    async def manage_categories_button(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="📋 Manage Ticket Categories",
            description="Select which categories should be active on the support panel dropdown below:",
            color=SEAMLESS_CONTAINER_COLOR
        )
        view = ManageCategoriesView()
        await interaction.response.edit_message(embed=embed, view=view)

    # Row 3
    @ui.button(label="Configure Logs", style=discord.ButtonStyle.primary, row=3)
    async def configure_logs_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(ConfigureLogsModal())

    # Row 4
    @ui.button(label="Send Panel", style=discord.ButtonStyle.success, row=4)
    async def send_panel_button(self, interaction: discord.Interaction, button: ui.Button):
        embed = create_panel_embed()
        view = TicketPanelView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            f"✅ **Support Ticket Panel Sent!** Active in {interaction.channel.mention}.",
            ephemeral=True
        )

    @ui.button(label="Delete Panel", style=discord.ButtonStyle.danger, row=4)
    async def delete_panel_button(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="⚠️ Delete / Reset Panel Configuration?",
            description="Are you sure you want to reset the panel configuration back to default HelzerX branding?",
            color=0xEF4444
        )
        view = DeleteConfirmView()
        await interaction.response.edit_message(embed=embed, view=view)


# ==========================================
# SETUP COG REGISTRATION
# ==========================================

class SetupCog(commands.Cog):
    """Cog handling exact *panel and !panel-setup ticket controls."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Supports *panel and !panel
    @commands.command(name="panel", aliases=["panel-setup"])
    @commands.has_permissions(administrator=True)
    async def panel_text_command(self, ctx: commands.Context):
        """Displays the exact Ticket Panel Control Dashboard."""
        embed = build_ticket_panel_control_embed()
        view = TicketPanelControlView()
        await ctx.send(embed=embed, view=view)

    # Supports /panel
    @app_commands.command(
        name="panel",
        description="Opens the official Ticket Panel Control Dashboard."
    )
    @require_admin()
    async def panel_slash_command(self, interaction: discord.Interaction):
        """Launches the Ticket Panel Dashboard."""
        embed = build_ticket_panel_control_embed()
        view = TicketPanelControlView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # Supports /panel-setup
    @app_commands.command(
        name="panel-setup",
        description="Opens the interactive Ticket Panel Control Dashboard."
    )
    @require_admin()
    async def panel_setup_slash(self, interaction: discord.Interaction):
        """Launches the Ticket Panel Dashboard."""
        embed = build_ticket_panel_control_embed()
        view = TicketPanelControlView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # Supports /panel-reset
    @app_commands.command(
        name="panel-reset",
        description="Resets ticket panel configuration to default HelzerX screenshot template."
    )
    @require_admin()
    async def panel_reset_command(self, interaction: discord.Interaction):
        global panel_config
        panel_config = CustomPanelConfig()
        panel_config.save()
        await interaction.response.send_message(
            "🔄 **Panel Reset**: Restored default HelzerX screenshot configuration.",
            ephemeral=True
        )

    # Supports /sync-commands
    @app_commands.command(
        name="sync-commands",
        description="Force instant synchronization of all slash commands to this server."
    )
    @require_admin()
    async def sync_commands(self, interaction: discord.Interaction):
        """Forces immediate guild slash command synchronization."""
        await interaction.response.defer(ephemeral=True)
        try:
            self.bot.tree.copy_global_to(guild=interaction.guild)
            synced = await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send(
                f"⚡ **Sync Successful**: Instantly synchronized `{len(synced)}` slash commands to **{interaction.guild.name}**.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
            await interaction.followup.send(f"❌ Synchronization failed: {e}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCog(bot))
