"""
HELZERX AI Support - AI Engine Slash Commands
Implements /ai-status, /ai-enable, /ai-disable.
"""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from bot.config import config
from bot.security.permissions import require_staff, require_admin
from bot.ai.client import ai_client
from bot.database.session import AsyncSessionLocal
from bot.database import crud


class AICog(commands.Cog):
    """Cog handling NVIDIA NIM AI provider management."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ai-status", description="Inspects NVIDIA NIM AI provider connection, latency, and tokens.")
    @require_staff()
    async def ai_status_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        health = await ai_client.check_health()
        status_color = config.BRAND_SUCCESS if health.get("healthy") else config.BRAND_DANGER

        embed = discord.Embed(
            title="NVIDIA NIM AI Engine Status",
            color=status_color
        )
        embed.add_field(name="Provider", value="NVIDIA NIM", inline=True)
        embed.add_field(name="Status", value=f"`{health.get('status')}`", inline=True)
        embed.add_field(name="Active Model", value=f"`{health.get('model')}`", inline=True)
        embed.add_field(name="Base URL", value=f"`{ai_client.base_url}`", inline=False)
        embed.add_field(name="Last Latency", value=f"`{ai_client.last_latency_ms:.1f}ms`", inline=True)
        embed.add_field(name="Prompt Tokens Used", value=f"`{ai_client.total_prompt_tokens:,}`", inline=True)
        embed.add_field(name="Completion Tokens", value=f"`{ai_client.total_completion_tokens:,}`", inline=True)

        if not health.get("healthy"):
            embed.add_field(name="Warning", value=health.get("message") or health.get("error", "Unknown"), inline=False)

        embed.set_footer(text=config.BRAND_FOOTER)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="ai-enable", description="Enables automated AI assistance for this ticket.")
    @require_staff()
    async def ai_enable_command(self, interaction: discord.Interaction):
        async with AsyncSessionLocal() as session:
            db_ticket = await crud.get_ticket_by_channel(session, interaction.channel.id)
            if not db_ticket:
                await interaction.response.send_message("❌ This channel is not an active ticket.", ephemeral=True)
                return

            db_ticket.ai_enabled = True
            await session.commit()

        await interaction.response.send_message("🤖 **AI Enabled**: NVIDIA NIM AI Support is now active in this ticket.")

    @app_commands.command(name="ai-disable", description="Disables automated AI assistance for this ticket.")
    @require_staff()
    async def ai_disable_command(self, interaction: discord.Interaction):
        async with AsyncSessionLocal() as session:
            db_ticket = await crud.get_ticket_by_channel(session, interaction.channel.id)
            if not db_ticket:
                await interaction.response.send_message("❌ This channel is not an active ticket.", ephemeral=True)
                return

            db_ticket.ai_enabled = False
            await session.commit()

        await interaction.response.send_message("👤 **AI Disabled**: Automated AI responses paused. Channel is in manual staff mode.")


async def setup(bot: commands.Bot):
    await bot.add_cog(AICog(bot))
