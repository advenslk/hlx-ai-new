"""
HELZERX AI Support - Setup & Container Panel Builder
Provides interactive container builder dashboard (!panel-setup & /panel-setup),
live previews, customizable sections, and seamless container embeds.
"""
from __future__ import annotations

import discord
from discord import app_commands, ui
from discord.ext import commands
from typing import Optional

from bot.config import config
from bot.panel_config import panel_config, CustomPanelConfig
from bot.security.permissions import require_admin
from bot.embeds.ticket_embeds import create_panel_embed, SEAMLESS_CONTAINER_COLOR
from bot.views.panel_view import TicketPanelView
from bot.utils.logger import logger


# ==========================================
# MODALS FOR CONTAINER BUILDER
# ==========================================

class HeaderTitleModal(ui.Modal, title="Edit Header & Dropdown Placeholder"):
    title_input = ui.TextInput(
        label="Container Title",
        placeholder="e.g. 🎧 HelzerX Support Center 🎧",
        default=panel_config.title[:100],
        required=True,
        max_length=100
    )
    placeholder_input = ui.TextInput(
        label="Dropdown Placeholder",
        placeholder="e.g. Select a ticket category",
        default=panel_config.select_placeholder[:100],
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        panel_config.title = self.title_input.value.strip()
        panel_config.select_placeholder = self.placeholder_input.value.strip() or "Select a ticket category"
        panel_config.save()
        await interaction.response.send_message("✅ **Header & Placeholder Updated!**", ephemeral=True)


class IntroTextModal(ui.Modal, title="Edit Intro & Subtitle Text"):
    intro_input = ui.TextInput(
        label="Intro Description",
        style=discord.TextStyle.paragraph,
        placeholder="Need assistance? Our support team is here to help...",
        default=panel_config.description[:1000],
        required=True,
        max_length=1500
    )

    async def on_submit(self, interaction: discord.Interaction):
        panel_config.description = self.intro_input.value.strip()
        panel_config.save()
        await interaction.response.send_message("✅ **Intro Description Updated!**", ephemeral=True)


class CategoriesTextModal(ui.Modal, title="Edit Support Categories Section"):
    section_title = ui.TextInput(
        label="Section Heading",
        placeholder="e.g. Support Categories",
        default=panel_config.support_categories_title[:80],
        required=True,
        max_length=80
    )
    categories_list = ui.TextInput(
        label="Categories Bullet List",
        style=discord.TextStyle.paragraph,
        placeholder="• 👥 **General Support**\n• 📚 **Cloud & Hosting**...",
        default=panel_config.categories_list[:800],
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        panel_config.support_categories_title = self.section_title.value.strip()
        panel_config.categories_list = self.categories_list.value.strip()
        panel_config.save()
        await interaction.response.send_message("✅ **Support Categories Section Updated!**", ephemeral=True)


class NoteTextModal(ui.Modal, title="Edit Note Section"):
    note_heading = ui.TextInput(
        label="Note Heading",
        placeholder="e.g. Please Note",
        default=panel_config.note_title[:60],
        required=True,
        max_length=60
    )
    note_body = ui.TextInput(
        label="Note Description",
        style=discord.TextStyle.paragraph,
        placeholder="Submit one ticket per issue and keep all related communication within your ticket.",
        default=panel_config.note_text[:400],
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        panel_config.note_title = self.note_heading.value.strip()
        panel_config.note_text = self.note_body.value.strip()
        panel_config.save()
        await interaction.response.send_message("✅ **Note Section Updated!**", ephemeral=True)


class ImagesModal(ui.Modal, title="Set Top Logo & Bottom Banner"):
    top_logo_input = ui.TextInput(
        label="Top Logo URL (Optional)",
        placeholder="https://.../helzerx-logo-3d.png",
        default=panel_config.top_image_url[:250] if panel_config.top_image_url else "",
        required=False,
        max_length=250
    )
    bottom_banner_input = ui.TextInput(
        label="Bottom Banner Image URL (Optional)",
        placeholder="https://.../helzerx-banner.png",
        default=panel_config.bottom_banner_url[:250] if panel_config.bottom_banner_url else "",
        required=False,
        max_length=250
    )

    async def on_submit(self, interaction: discord.Interaction):
        panel_config.top_image_url = self.top_logo_input.value.strip()
        panel_config.bottom_banner_url = self.bottom_banner_input.value.strip()
        panel_config.save()
        await interaction.response.send_message("✅ **Banner & Logo URLs Saved!**", ephemeral=True)


class FooterModal(ui.Modal, title="Edit Footer Attribution"):
    footer1 = ui.TextInput(
        label="Footer Line 1 (Company Name)",
        placeholder="e.g. HelzerX Technologies",
        default=panel_config.footer_line1[:80],
        required=True,
        max_length=80
    )
    footer2 = ui.TextInput(
        label="Footer Line 2 (Copyright)",
        placeholder="e.g. © 2026 HelzerX Technologies (Pvt) Ltd. All rights reserved.",
        default=panel_config.footer_line2[:100],
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        panel_config.footer_line1 = self.footer1.value.strip()
        panel_config.footer_line2 = self.footer2.value.strip()
        panel_config.save()
        await interaction.response.send_message("✅ **Footer Attribution Updated!**", ephemeral=True)


# ==========================================
# INTERACTIVE CONTAINER BUILDER VIEW
# ==========================================

class ContainerPanelBuilderView(ui.View):
    """
    Interactive Container Customizer Dashboard inspired by container builder bots.
    Provides real-time modals to customize each section of the ticket panel.
    """

    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Edit Header & Title", style=discord.ButtonStyle.secondary, emoji="✏️", row=0)
    async def edit_header(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(HeaderTitleModal())

    @ui.button(label="Edit Intro Text", style=discord.ButtonStyle.secondary, emoji="📝", row=0)
    async def edit_intro(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(IntroTextModal())

    @ui.button(label="Edit Categories", style=discord.ButtonStyle.secondary, emoji="📋", row=0)
    async def edit_categories(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(CategoriesTextModal())

    @ui.button(label="Edit Note Box", style=discord.ButtonStyle.secondary, emoji="ℹ️", row=1)
    async def edit_note(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(NoteTextModal())

    @ui.button(label="Top Logo & Banner", style=discord.ButtonStyle.secondary, emoji="🖼️", row=1)
    async def edit_images(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(ImagesModal())

    @ui.button(label="Edit Footer", style=discord.ButtonStyle.secondary, emoji="🏷️", row=1)
    async def edit_footer(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(FooterModal())

    @ui.button(label="Live Preview", style=discord.ButtonStyle.primary, emoji="👁️", row=2)
    async def live_preview(self, interaction: discord.Interaction, button: ui.Button):
        embed = create_panel_embed()
        view = TicketPanelView()
        await interaction.response.send_message(
            content="🔍 **Live Container Panel Preview (Seamless Style):**",
            embed=embed,
            view=view,
            ephemeral=True
        )

    @ui.button(label="Publish to Channel", style=discord.ButtonStyle.success, emoji="🚀", row=2)
    async def publish_panel(self, interaction: discord.Interaction, button: ui.Button):
        embed = create_panel_embed()
        view = TicketPanelView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            f"✅ **Container Support Panel Published!** Active in {interaction.channel.mention}.",
            ephemeral=True
        )

    @ui.button(label="Reset Defaults", style=discord.ButtonStyle.danger, emoji="🔄", row=2)
    async def reset_defaults(self, interaction: discord.Interaction, button: ui.Button):
        global panel_config
        panel_config = CustomPanelConfig()
        panel_config.save()
        await interaction.response.send_message(
            "🔄 **Reset Complete!** Restored official HelzerX Support Center screenshot template.",
            ephemeral=True
        )


def build_builder_dashboard_embed() -> discord.Embed:
    """Builds the main control embed for the container panel customizer."""
    embed = discord.Embed(
        title="🛠️ HelzerX Container Panel Builder",
        description=(
            "Welcome to the **Interactive Support Panel Customizer**.\n"
            "Use the controls below to configure your server's support container message live. "
            "Click any button to edit text, images, or test previews."
        ),
        color=SEAMLESS_CONTAINER_COLOR
    )

    embed.add_field(
        name="📌 Current Configuration Status",
        value=(
            f"• **Title:** `{panel_config.title}`\n"
            f"• **Dropdown Placeholder:** `{panel_config.select_placeholder}`\n"
            f"• **Top Logo URL:** `{'Set' if panel_config.top_image_url else 'None'}`\n"
            f"• **Bottom Banner URL:** `{'Set' if panel_config.bottom_banner_url else 'None'}`\n"
            f"• **Side Color Line:** `Disabled (Seamless Container Style)`\n"
            f"• **Footer Line 1:** `{panel_config.footer_line1}`"
        ),
        inline=False
    )

    embed.add_field(
        name="⚡ Quick Actions",
        value=(
            "• `[👁️ Live Preview]` Test how it looks ephemerally.\n"
            "• `[🚀 Publish to Channel]` Post permanent panel with active category select dropdown.\n"
            "• `[🔄 Reset Defaults]` Revert all sections back to the official screenshot template."
        ),
        inline=False
    )

    embed.set_footer(text="HelzerX Support Bot • Container Builder V2")
    return embed


# ==========================================
# SETUP COG DEFINITION
# ==========================================

class SetupCog(commands.Cog):
    """Cog for administrator setup and container panel customizer."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Text Prefix Command: !panel-setup
    @commands.command(name="panel-setup")
    @commands.has_permissions(administrator=True)
    async def panel_setup_prefix(self, ctx: commands.Context):
        """Launches the interactive Container Builder Dashboard via text command."""
        embed = build_builder_dashboard_embed()
        view = ContainerPanelBuilderView()
        await ctx.send(embed=embed, view=view)

    # Slash Command: /panel-setup
    @app_commands.command(
        name="panel-setup",
        description="Opens the interactive Container Builder Dashboard to customize the support ticket panel."
    )
    @require_admin()
    async def panel_setup_slash(self, interaction: discord.Interaction):
        """Launches the interactive Container Builder Dashboard via slash command."""
        embed = build_builder_dashboard_embed()
        view = ContainerPanelBuilderView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # Slash Command: /panel
    @app_commands.command(
        name="panel",
        description="Posts the official HELZERX Support Ticket Panel to the current channel."
    )
    @require_admin()
    async def panel_command(self, interaction: discord.Interaction):
        """Directly sends the ticket container panel."""
        embed = create_panel_embed()
        view = TicketPanelView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Support panel successfully posted.", ephemeral=True)

    # Text Prefix Command: !panel
    @commands.command(name="panel")
    @commands.has_permissions(administrator=True)
    async def panel_prefix(self, ctx: commands.Context):
        """Directly sends the ticket container panel via text command."""
        embed = create_panel_embed()
        view = TicketPanelView()
        await ctx.send(embed=embed, view=view)

    # Slash Command: /panel-reset
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

    # Slash Command: /sync-commands
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

    @app_commands.command(name="setup", description="Initializes HELZERX bot configuration and verifies permissions.")
    @require_admin()
    async def setup_command(self, interaction: discord.Interaction):
        """Runs automated verification checks on roles and channels."""
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        checks = []

        if config.TICKET_CATEGORY_ID:
            cat = guild.get_channel(config.TICKET_CATEGORY_ID)
            checks.append(f"• Ticket Category: `{'Configured (' + cat.name + ')' if cat else 'Channel ID not found'}`")
        else:
            checks.append("• Ticket Category: `Not configured (will create at server root)`")

        valid_support = [r.name for r_id in config.SUPPORT_ROLE_IDS if (r := guild.get_role(r_id))]
        checks.append(f"• Support Roles: `{', '.join(valid_support) if valid_support else 'No matching roles configured'}`")

        valid_admin = [r.name for r_id in config.ADMIN_ROLE_IDS if (r := guild.get_role(r_id))]
        checks.append(f"• Admin Roles: `{', '.join(valid_admin) if valid_admin else 'None (uses Guild Administrator permission)'}`")

        if config.TRANSCRIPT_CHANNEL_ID:
            t_chan = guild.get_channel(config.TRANSCRIPT_CHANNEL_ID)
            checks.append(f"• Transcript Archive: `{'Configured (' + t_chan.name + ')' if t_chan else 'Not found'}`")

        embed = discord.Embed(
            title="HelzerX Support • System Setup Audit",
            description="\n".join(checks),
            color=SEAMLESS_CONTAINER_COLOR
        )
        embed.set_footer(text=config.BRAND_FOOTER)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="config", description="Inspects current active bot configuration and environment settings.")
    @require_admin()
    async def config_command(self, interaction: discord.Interaction):
        """Displays non-sensitive environment configuration without exposing provider details."""
        embed = discord.Embed(
            title="HelzerX Bot Configuration",
            color=SEAMLESS_CONTAINER_COLOR
        )
        embed.add_field(name="Diagnostic Engine", value="`Active (High-Speed Automated)`", inline=True)
        embed.add_field(name="Auto-Triage", value="`Enabled`" if config.AI_AUTO_RESPONSE_ENABLED else "`Disabled`", inline=True)
        embed.add_field(name="Rate Limit", value=f"`{config.RATE_LIMIT_PER_MINUTE} msgs/min`", inline=True)
        embed.add_field(name="Mask Sensitive Data", value=f"`{config.MASK_SENSITIVE_DATA}`", inline=True)
        embed.add_field(name="Database Mode", value="`PostgreSQL`" if "postgresql" in config.DATABASE_URL else "`SQLite (Dev/Fallback)`", inline=True)
        embed.set_footer(text=config.BRAND_FOOTER)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCog(bot))
