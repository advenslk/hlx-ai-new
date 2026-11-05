"""
HELZERX AI Support - Ticket Management Slash Commands
Implements /ticket, /claim, /assign, /close, /reopen, /transcript, /ticketinfo, /ticketstats.
"""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from bot.config import config, TICKET_CATEGORIES
from bot.security.permissions import require_staff, is_staff_check
from bot.tickets.manager import ticket_manager
from bot.staff.manager import staff_manager
from bot.tickets.transcript import generate_html_transcript
from bot.database.session import AsyncSessionLocal
from bot.database import crud
from bot.utils.logger import logger


class TicketCog(commands.Cog):
    """Cog handling ticket actions and statistics."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ticket", description="Creates a new HELZERX support ticket.")
    @app_commands.describe(
        category="Choose ticket department",
        subject="Brief summary of the issue",
        description="Detailed description of the issue"
    )
    @app_commands.choices(category=[
        app_commands.Choice(name=c.name, value=c.id) for c in TICKET_CATEGORIES.values()
    ])
    async def ticket_command(
        self,
        interaction: discord.Interaction,
        category: str,
        subject: str,
        description: str
    ):
        await interaction.response.defer(ephemeral=True)
        try:
            channel, code = await ticket_manager.create_ticket_channel(
                guild=interaction.guild,
                user=interaction.user,
                category_id=category,
                subject=subject,
                description=description
            )
            await interaction.followup.send(
                f"✅ Ticket created successfully: {channel.mention} (`{code}`)",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Could not create ticket: {e}", ephemeral=True)

    @app_commands.command(name="claim", description="Claims the current ticket as the primary responding staff member.")
    @require_staff()
    async def claim_command(self, interaction: discord.Interaction):
        success = await staff_manager.claim_ticket(interaction.channel, interaction.user)
        if success:
            await interaction.response.send_message(
                f"✋ **Ticket Claimed**: {interaction.user.mention} is assigned to this ticket.",
                ephemeral=False
            )
        else:
            await interaction.response.send_message("❌ This channel is not an active ticket.", ephemeral=True)

    @app_commands.command(name="assign", description="Assigns this ticket to another staff member.")
    @app_commands.describe(member="Support staff member to assign")
    @require_staff()
    async def assign_command(self, interaction: discord.Interaction, member: discord.Member):
        success = await staff_manager.assign_ticket(interaction.channel, interaction.user, member)
        if success:
            await interaction.response.send_message(
                f"📋 **Ticket Reassigned**: Ticket assigned to {member.mention} by {interaction.user.mention}.",
                ephemeral=False
            )
        else:
            await interaction.response.send_message("❌ This channel is not an active ticket.", ephemeral=True)

    @app_commands.command(name="close", description="Closes and archives this support ticket.")
    @app_commands.describe(reason="Optional reason for ticket closure")
    async def close_command(self, interaction: discord.Interaction, reason: Optional[str] = None):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("🔒 Processing ticket closure and generating transcript...", ephemeral=True)
        await ticket_manager.close_ticket(
            channel=interaction.channel,
            closed_by=interaction.user,
            reason=reason or "Closed via /close slash command"
        )

    @app_commands.command(name="reopen", description="Reopens a closed ticket.")
    @require_staff()
    async def reopen_command(self, interaction: discord.Interaction):
        async with AsyncSessionLocal() as session:
            db_ticket = await crud.get_ticket_by_channel(session, interaction.channel.id)
            if not db_ticket:
                await interaction.response.send_message("❌ Not a ticket channel.", ephemeral=True)
                return

            db_ticket.status = "OPEN"
            db_ticket.closed_at = None
            db_ticket.close_reason = None
            await crud.log_audit_event(
                session=session,
                action="TICKET_REOPENED",
                actor_id=interaction.user.id,
                actor_name=interaction.user.name,
                ticket_id=db_ticket.id
            )
            await session.commit()

        await interaction.response.send_message(
            f"🔓 **Ticket Reopened**: Ticket `{db_ticket.ticket_code}` is marked active again by {interaction.user.mention}."
        )

    @app_commands.command(name="transcript", description="Generates and exports an HTML transcript of this ticket.")
    @require_staff()
    async def transcript_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        async with AsyncSessionLocal() as session:
            db_ticket = await crud.get_ticket_by_channel(session, interaction.channel.id)
            if not db_ticket:
                await interaction.followup.send("❌ Channel is not a ticket.", ephemeral=True)
                return

            msgs_data = [
                {
                    "author_name": m.author_name,
                    "author_role": m.author_role,
                    "content": m.content,
                    "created_at": m.created_at
                }
                for m in db_ticket.messages
            ]

            _, file_path = generate_html_transcript(
                ticket_code=db_ticket.ticket_code,
                customer_name=db_ticket.creator.username if db_ticket.creator else "Customer",
                category=db_ticket.category,
                priority=db_ticket.priority,
                status=db_ticket.status,
                messages=msgs_data
            )

        await interaction.followup.send(
            content=f"📄 Transcript for `{db_ticket.ticket_code}`:",
            file=discord.File(file_path, filename=f"transcript_{db_ticket.ticket_code}.html"),
            ephemeral=True
        )

    @app_commands.command(name="ticketinfo", description="Displays full diagnostic info and metadata for this ticket.")
    async def ticketinfo_command(self, interaction: discord.Interaction):
        async with AsyncSessionLocal() as session:
            db_ticket = await crud.get_ticket_by_channel(session, interaction.channel.id)
            if not db_ticket:
                await interaction.response.send_message("❌ Not an active ticket channel.", ephemeral=True)
                return

            embed = discord.Embed(
                title=f"Ticket Information: {db_ticket.ticket_code}",
                color=config.BRAND_COLOR
            )
            embed.add_field(name="Status", value=f"`{db_ticket.status}`", inline=True)
            embed.add_field(name="Priority", value=f"`{db_ticket.priority}`", inline=True)
            embed.add_field(name="Category", value=db_ticket.category.capitalize(), inline=True)
            embed.add_field(name="Department", value=db_ticket.department or "General", inline=True)
            embed.add_field(name="AI Enabled", value="`Yes`" if db_ticket.ai_enabled else "`No`", inline=True)
            embed.add_field(name="AI Turn Count", value=str(db_ticket.ai_turn_count), inline=True)
            embed.add_field(name="Creator", value=f"<@{db_ticket.creator.discord_id}>" if db_ticket.creator else "Unknown", inline=True)
            embed.add_field(name="Assignee", value=f"<@{db_ticket.claimed_by.discord_id}>" if db_ticket.claimed_by else "Unassigned", inline=True)
            embed.add_field(name="Created", value=db_ticket.created_at.strftime("%Y-%m-%d %H:%M UTC"), inline=True)

            if db_ticket.server_identifier:
                embed.add_field(name="Service / Node", value=f"`{db_ticket.server_identifier}`", inline=False)

            if is_staff_check(interaction) and db_ticket.internal_notes:
                notes_summary = "\n".join([f"• [{n.staff_name}]: {n.content[:60]}" for n in db_ticket.internal_notes[-3:]])
                embed.add_field(name="Recent Internal Notes (Staff Only)", value=notes_summary, inline=False)

            embed.set_footer(text=config.BRAND_FOOTER)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ticketstats", description="Displays global ticketing operational metrics.")
    @require_staff()
    async def ticketstats_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        async with AsyncSessionLocal() as session:
            stats = await crud.get_ticket_statistics(session)

        embed = discord.Embed(
            title="HELZERX AI Support • Operational Statistics",
            color=config.BRAND_COLOR
        )
        embed.add_field(name="Total Tickets", value=f"`{stats['total']}`", inline=True)
        embed.add_field(name="Active Tickets", value=f"`{stats['open']}`", inline=True)
        embed.add_field(name="Resolved Tickets", value=f"`{stats['closed']}`", inline=True)
        embed.add_field(name="Urgent In Queue", value=f"`{stats['urgent']}`", inline=True)
        embed.add_field(name="Resolution Rate", value=f"`{stats['resolution_rate']}%`", inline=True)
        embed.set_footer(text=config.BRAND_FOOTER)
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))
