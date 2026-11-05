"""
HELZERX AI Support - Staff Operations Manager
Handles ticket claiming, staff assignment, confidential internal notes, and staff audit tracking.
"""
from __future__ import annotations

import discord
from typing import Optional

from bot.config import config
from bot.database.session import AsyncSessionLocal
from bot.database import crud
from bot.utils.logger import logger


class StaffManager:
    """Manages staff workflows and internal notes."""

    async def claim_ticket(
        self,
        channel: discord.TextChannel,
        staff_member: discord.Member | discord.User
    ) -> bool:
        """Assigns the ticket to the claiming staff member."""
        async with AsyncSessionLocal() as session:
            db_ticket = await crud.get_ticket_by_channel(session, channel.id)
            if not db_ticket:
                return False

            staff_user = await crud.get_or_create_user(
                session,
                discord_id=staff_member.id,
                username=staff_member.name,
                display_name=getattr(staff_member, "display_name", staff_member.name),
                is_staff=True
            )

            db_ticket.status = "CLAIMED"
            db_ticket.claimed_by_id = staff_user.id

            await crud.log_audit_event(
                session=session,
                action="TICKET_CLAIMED",
                actor_id=staff_member.id,
                actor_name=staff_member.name,
                ticket_id=db_ticket.id,
                details=f"Claimed by {staff_member.name}"
            )
            await session.commit()

        # Update channel topic
        try:
            current_topic = channel.topic or ""
            await channel.edit(topic=f"{current_topic} | Claimed by: {staff_member.display_name}")
        except Exception:
            pass

        return True

    async def assign_ticket(
        self,
        channel: discord.TextChannel,
        assigned_by: discord.Member | discord.User,
        target_staff: discord.Member
    ) -> bool:
        """Assigns a ticket to another staff member."""
        async with AsyncSessionLocal() as session:
            db_ticket = await crud.get_ticket_by_channel(session, channel.id)
            if not db_ticket:
                return False

            target_user = await crud.get_or_create_user(
                session,
                discord_id=target_staff.id,
                username=target_staff.name,
                display_name=target_staff.display_name,
                is_staff=True
            )

            db_ticket.status = "CLAIMED"
            db_ticket.claimed_by_id = target_user.id

            await crud.log_audit_event(
                session=session,
                action="TICKET_ASSIGNED",
                actor_id=assigned_by.id,
                actor_name=assigned_by.name,
                ticket_id=db_ticket.id,
                details=f"Assigned to {target_staff.name} by {assigned_by.name}"
            )
            await session.commit()

        return True

    async def add_note(
        self,
        channel_id: int,
        staff_member: discord.Member | discord.User,
        content: str
    ) -> bool:
        """Records a confidential internal note."""
        async with AsyncSessionLocal() as session:
            db_ticket = await crud.get_ticket_by_channel(session, channel_id)
            if not db_ticket:
                return False

            await crud.add_internal_note(
                session=session,
                ticket_id=db_ticket.id,
                staff_id=staff_member.id,
                staff_name=staff_member.name,
                content=content
            )

            await crud.log_audit_event(
                session=session,
                action="INTERNAL_NOTE_ADDED",
                actor_id=staff_member.id,
                actor_name=staff_member.name,
                ticket_id=db_ticket.id,
                details=f"Note length: {len(content)} chars"
            )
            await session.commit()

        # Log to staff log channel if configured
        if config.STAFF_LOG_CHANNEL_ID:
            guild = getattr(staff_member, "guild", None)
            if guild:
                log_chan = guild.get_channel(config.STAFF_LOG_CHANNEL_ID)
                if log_chan:
                    embed = discord.Embed(
                        title=f"🔒 Internal Note Added • {db_ticket.ticket_code}",
                        description=content,
                        color=config.BRAND_WARNING
                    )
                    embed.set_author(name=staff_member.display_name, icon_url=staff_member.display_avatar.url if hasattr(staff_member, "display_avatar") else None)
                    await log_chan.send(embed=embed)

        return True


staff_manager = StaffManager()
