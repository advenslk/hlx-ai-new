"""
HELZERX AI Support - Database CRUD Operations
Optimized query helpers for tickets, messages, internal notes, users, and audit logs.
"""
from __future__ import annotations

import datetime
from typing import Optional, List
from sqlalchemy import select, update, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.models import (
    User, Ticket, TicketMessage, InternalNote,
    TicketTranscript, CustomerFeedback, AuditLog, KnowledgeDocument
)
from bot.utils.logger import logger


async def get_or_create_user(
    session: AsyncSession,
    discord_id: int,
    username: str,
    display_name: Optional[str] = None,
    is_staff: bool = False
) -> User:
    """Finds user by Discord ID or creates a new record."""
    stmt = select(User).where(User.discord_id == discord_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            discord_id=discord_id,
            username=username,
            display_name=display_name or username,
            is_staff=is_staff
        )
        session.add(user)
        await session.flush()
    else:
        # Update username if changed
        if user.username != username or user.display_name != display_name:
            user.username = username
            user.display_name = display_name or username
            await session.flush()

    return user


async def create_ticket(
    session: AsyncSession,
    ticket_code: str,
    guild_id: int,
    creator_id: int,
    category: str,
    priority: str = "NORMAL",
    department: str = "Technical Support",
    subject: Optional[str] = None,
    description: Optional[str] = None,
    server_identifier: Optional[str] = None,
    channel_id: Optional[int] = None
) -> Ticket:
    """Creates a new ticket record."""
    ticket = Ticket(
        ticket_code=ticket_code,
        guild_id=guild_id,
        channel_id=channel_id,
        creator_id=creator_id,
        category=category,
        priority=priority,
        department=department,
        initial_subject=subject,
        initial_description=description,
        server_identifier=server_identifier,
        status="OPEN",
        ai_enabled=True
    )
    session.add(ticket)
    await session.flush()
    return ticket


async def get_ticket_by_channel(session: AsyncSession, channel_id: int) -> Optional[Ticket]:
    """Retrieves a ticket by its private channel ID."""
    stmt = (
        select(Ticket)
        .options(
            selectinload(Ticket.creator),
            selectinload(Ticket.claimed_by),
            selectinload(Ticket.messages),
            selectinload(Ticket.internal_notes)
        )
        .where(Ticket.channel_id == channel_id)
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def get_ticket_by_code(session: AsyncSession, ticket_code: str) -> Optional[Ticket]:
    """Retrieves a ticket by its reference code (e.g. HZX-8429)."""
    stmt = (
        select(Ticket)
        .options(
            selectinload(Ticket.creator),
            selectinload(Ticket.claimed_by),
            selectinload(Ticket.messages),
            selectinload(Ticket.internal_notes)
        )
        .where(Ticket.ticket_code == ticket_code)
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def check_active_ticket_exists(session: AsyncSession, creator_user_id: int, category: str) -> Optional[Ticket]:
    """Checks if a user already has an open ticket in the same category."""
    stmt = (
        select(Ticket)
        .where(
            Ticket.creator_id == creator_user_id,
            Ticket.category == category,
            Ticket.status.in_(["OPEN", "CLAIMED", "ESCALATED"])
        )
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def save_ticket_message(
    session: AsyncSession,
    ticket_id: int,
    author_id: int,
    author_name: str,
    author_role: str,
    content: str,
    detected_language: Optional[str] = None,
    tokens_prompt: int = 0,
    tokens_completion: int = 0,
    has_sanitization: bool = False,
    discord_message_id: Optional[int] = None
) -> TicketMessage:
    """Appends a message to the ticket conversation log."""
    msg = TicketMessage(
        ticket_id=ticket_id,
        discord_message_id=discord_message_id,
        author_id=author_id,
        author_name=author_name,
        author_role=author_role,
        content=content,
        detected_language=detected_language,
        tokens_prompt=tokens_prompt,
        tokens_completion=tokens_completion,
        has_sanitization=has_sanitization
    )
    session.add(msg)
    await session.flush()
    return msg


async def add_internal_note(
    session: AsyncSession,
    ticket_id: int,
    staff_id: int,
    staff_name: str,
    content: str
) -> InternalNote:
    """Adds a confidential staff note to the ticket."""
    note = InternalNote(
        ticket_id=ticket_id,
        staff_id=staff_id,
        staff_name=staff_name,
        content=content
    )
    session.add(note)
    await session.flush()
    return note


async def log_audit_event(
    session: AsyncSession,
    action: str,
    actor_id: int,
    actor_name: str,
    ticket_id: Optional[int] = None,
    details: Optional[str] = None
) -> AuditLog:
    """Records an immutable security/staff action in the audit log."""
    log_entry = AuditLog(
        action=action,
        actor_id=actor_id,
        actor_name=actor_name,
        ticket_id=ticket_id,
        details=details
    )
    session.add(log_entry)
    await session.flush()
    return log_entry


async def get_ticket_statistics(session: AsyncSession) -> dict:
    """Calculates operational metrics across all tickets."""
    total_tickets = await session.scalar(select(func.count(Ticket.id))) or 0
    open_tickets = await session.scalar(select(func.count(Ticket.id)).where(Ticket.status.in_(["OPEN", "CLAIMED", "ESCALATED"]))) or 0
    closed_tickets = await session.scalar(select(func.count(Ticket.id)).where(Ticket.status == "CLOSED")) or 0
    urgent_tickets = await session.scalar(select(func.count(Ticket.id)).where(Ticket.priority == "URGENT", Ticket.status != "CLOSED")) or 0

    return {
        "total": total_tickets,
        "open": open_tickets,
        "closed": closed_tickets,
        "urgent": urgent_tickets,
        "resolution_rate": round((closed_tickets / total_tickets * 100) if total_tickets > 0 else 100, 1)
    }
