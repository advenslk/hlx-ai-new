"""
HELZERX AI Support - Ticket Lifecycle Manager
Orchestrates ticket creation, channel permissions, triage, AI assistance, closing, and transcripts.
"""
from __future__ import annotations

import asyncio
import discord
from typing import Tuple, Optional
from datetime import datetime, timezone

from bot.config import config, TICKET_CATEGORIES
from bot.database.session import AsyncSessionLocal
from bot.database import crud
from bot.ai.classifier import classify_ticket
from bot.ai.prompts import build_ticket_ai_prompt
from bot.ai.language_detector import detect_language
from bot.ai.client import ai_client
from bot.knowledge.manager import knowledge_manager
from bot.utils.helpers import generate_ticket_id, sanitize_channel_name
from bot.utils.logger import logger
from bot.embeds.ticket_embeds import (
    create_ticket_welcome_embed,
    create_ai_response_embed,
    create_escalation_embed,
    create_ticket_closed_embed
)
from bot.views.ticket_control_view import TicketControlView
from bot.tickets.transcript import generate_html_transcript


class TicketManager:
    """Core manager handling all ticket operations."""

    async def create_ticket_channel(
        self,
        guild: discord.Guild,
        user: discord.Member | discord.User,
        category_id: str,
        subject: str,
        description: str,
        server_identifier: Optional[str] = None
    ) -> Tuple[discord.TextChannel, str]:
        """
        Creates a private ticket channel with strict permissions,
        persists records, and triggers initial AI diagnosis.
        """
        cat_def = TICKET_CATEGORIES.get(category_id, TICKET_CATEGORIES["general"])

        # 1. Smart Classification
        classification = classify_ticket(subject, description, category_hint=category_id)
        priority = classification.priority

        async with AsyncSessionLocal() as session:
            # Prevent duplicate active tickets by the same user in this category
            db_user = await crud.get_or_create_user(
                session,
                discord_id=user.id,
                username=user.name,
                display_name=getattr(user, "display_name", user.name)
            )

            existing = await crud.check_active_ticket_exists(session, db_user.id, category_id)
            if existing:
                raise ValueError(
                    f"You already have an active ticket (`{existing.ticket_code}`) in the **{cat_def.name}** category. "
                    "Please resolve your existing ticket before opening a new one."
                )

            ticket_code = generate_ticket_id("HZX")

            # 2. Permission Overwrites
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                user: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    embed_links=True,
                    attach_files=True,
                    read_message_history=True
                ),
                guild.me: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    manage_channels=True,
                    embed_links=True,
                    attach_files=True,
                    manage_messages=True
                )
            }

            # Add Support Staff Roles
            for role_id in config.SUPPORT_ROLE_IDS + config.ADMIN_ROLE_IDS:
                role = guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        embed_links=True,
                        attach_files=True,
                        manage_messages=True
                    )

            # 3. Channel Provisioning
            category_channel = None
            if config.TICKET_CATEGORY_ID:
                category_channel = guild.get_channel(config.TICKET_CATEGORY_ID)

            chan_name = sanitize_channel_name(ticket_code, category_id, user.name)
            channel = await guild.create_text_channel(
                name=chan_name,
                category=category_channel,
                overwrites=overwrites,
                topic=f"HELZERX Support Ticket {ticket_code} | Creator: {user.name} | Category: {cat_def.name} | Priority: {priority}"
            )

            # 4. Save to Database
            db_ticket = await crud.create_ticket(
                session=session,
                ticket_code=ticket_code,
                guild_id=guild.id,
                creator_id=db_user.id,
                category=category_id,
                priority=priority,
                department=classification.department,
                subject=subject,
                description=description,
                server_identifier=server_identifier,
                channel_id=channel.id
            )

            # Initial message log
            await crud.save_ticket_message(
                session=session,
                ticket_id=db_ticket.id,
                author_id=user.id,
                author_name=user.name,
                author_role="customer",
                content=f"**Subject:** {subject}\n\n{description}"
            )

            await crud.log_audit_event(
                session=session,
                action="TICKET_CREATED",
                actor_id=user.id,
                actor_name=user.name,
                ticket_id=db_ticket.id,
                details=f"Code: {ticket_code}, Cat: {cat_def.name}, Priority: {priority}"
            )
            await session.commit()

        # 5. Send Welcome Embed with Controls
        welcome_embed = create_ticket_welcome_embed(
            ticket_code=ticket_code,
            creator=user,
            category_name=cat_def.name,
            priority=priority,
            subject=subject,
            server_identifier=server_identifier
        )
        control_view = TicketControlView()
        await channel.send(content=f"{user.mention}", embed=welcome_embed, view=control_view)

        # 6. Urgent Priority Notification
        if priority == "URGENT":
            urgent_msg = "🚨 **URGENT TICKET ALERT**: This issue has been classified as mission-critical. Staff has been notified."
            staff_mentions = " ".join([f"<@&{r_id}>" for r_id in config.SUPPORT_ROLE_IDS])
            if staff_mentions:
                urgent_msg = f"{staff_mentions} {urgent_msg}"
            await channel.send(urgent_msg)

        # 7. Start AI Support Session
        if config.AI_AUTO_RESPONSE_ENABLED:
            asyncio.create_task(
                self.run_initial_ai_triage(
                    channel=channel,
                    ticket_code=ticket_code,
                    user=user,
                    category_name=cat_def.name,
                    priority=priority,
                    subject=subject,
                    description=description,
                    server_identifier=server_identifier or ""
                )
            )

        return channel, ticket_code

    async def run_initial_ai_triage(
        self,
        channel: discord.TextChannel,
        ticket_code: str,
        user: discord.Member | discord.User,
        category_name: str,
        priority: str,
        subject: str,
        description: str,
        server_identifier: str
    ):
        """Asynchronously queries NVIDIA NIM and delivers initial troubleshooting."""
        try:
            async with channel.typing():
                # Detect language
                detected_lang, conf = detect_language(f"{subject} {description}")

                # Retrieve Knowledge Base articles (RAG)
                rag_context = knowledge_manager.search(f"{subject} {description}", top_k=2)

                system_prompt = build_ticket_ai_prompt(
                    ticket_code=ticket_code,
                    category=category_name,
                    priority=priority,
                    customer_name=user.display_name or user.name,
                    initial_subject=subject,
                    initial_description=description,
                    server_identifier=server_identifier,
                    retrieved_knowledge=rag_context,
                    detected_language=detected_lang
                )

                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"My issue is:\nSubject: {subject}\nDescription: {description}\nServer identifier: {server_identifier or 'None'}"
                    }
                ]

                reply_text, p_toks, c_toks = await ai_client.generate_response(messages)

                # Persist AI response
                async with AsyncSessionLocal() as session:
                    db_ticket = await crud.get_ticket_by_code(session, ticket_code)
                    if db_ticket:
                        await crud.save_ticket_message(
                            session=session,
                            ticket_id=db_ticket.id,
                            author_id=channel.guild.me.id,
                            author_name="HELZERX AI Support",
                            author_role="ai",
                            content=reply_text,
                            detected_language=detected_lang,
                            tokens_prompt=p_toks,
                            tokens_completion=c_toks
                        )
                        await session.commit()

                # Send AI message directly as normal text without embeds (human engineer style)
                if len(reply_text) <= 2000:
                    await channel.send(content=reply_text)
                else:
                    # Clean chunk splitting on newlines
                    for i in range(0, len(reply_text), 1950):
                        await channel.send(content=reply_text[i:i+1950])

        except Exception as e:
            logger.error(f"Error during AI triage for ticket {ticket_code}: {e}", exc_info=True)

    async def escalate_to_human(
        self,
        channel: discord.TextChannel,
        requested_by: discord.Member | discord.User,
        reason: str
    ):
        """Disables automated AI responses and alerts staff."""
        async with AsyncSessionLocal() as session:
            db_ticket = await crud.get_ticket_by_channel(session, channel.id)
            if db_ticket:
                db_ticket.status = "ESCALATED"
                db_ticket.ai_enabled = False
                await crud.log_audit_event(
                    session=session,
                    action="TICKET_ESCALATED",
                    actor_id=requested_by.id,
                    actor_name=requested_by.name,
                    ticket_id=db_ticket.id,
                    details=reason
                )
                await session.commit()

                code = db_ticket.ticket_code
            else:
                code = channel.name

        embed = create_escalation_embed(ticket_code=code, reason=reason)
        staff_pings = " ".join([f"<@&{r_id}>" for r_id in config.SUPPORT_ROLE_IDS])
        await channel.send(content=staff_pings if staff_pings else None, embed=embed)

    async def close_ticket(
        self,
        channel: discord.TextChannel,
        closed_by: discord.Member | discord.User,
        reason: Optional[str] = None
    ):
        """Marks ticket closed, exports HTML transcript, and archives channel."""
        async with AsyncSessionLocal() as session:
            db_ticket = await crud.get_ticket_by_channel(session, channel.id)
            if not db_ticket:
                await channel.send("❌ Error: Ticket record not found in database.")
                return

            db_ticket.status = "CLOSED"
            db_ticket.closed_at = datetime.utcnow()
            db_ticket.close_reason = reason or "Resolved"

            # Gather messages
            msgs_data = []
            for m in db_ticket.messages:
                msgs_data.append({
                    "author_name": m.author_name,
                    "author_role": m.author_role,
                    "content": m.content,
                    "created_at": m.created_at
                })

            customer_name = db_ticket.creator.username if db_ticket.creator else "Customer"
            html_content, file_path = generate_html_transcript(
                ticket_code=db_ticket.ticket_code,
                customer_name=customer_name,
                category=db_ticket.category,
                priority=db_ticket.priority,
                status="CLOSED",
                messages=msgs_data
            )

            # Save transcript record
            transcript_record = crud.TicketTranscript(
                ticket_id=db_ticket.id,
                ticket_code=db_ticket.ticket_code,
                file_path=str(file_path),
                html_content=html_content,
                message_count=len(msgs_data)
            )
            session.add(transcript_record)

            await crud.log_audit_event(
                session=session,
                action="TICKET_CLOSED",
                actor_id=closed_by.id,
                actor_name=closed_by.name,
                ticket_id=db_ticket.id,
                details=f"Reason: {reason or 'Normal resolution'}"
            )
            await session.commit()

        # Send closure embed
        closed_embed = create_ticket_closed_embed(
            ticket_code=db_ticket.ticket_code,
            closed_by_name=closed_by.display_name or closed_by.name,
            reason=reason,
            total_messages=len(msgs_data)
        )
        await channel.send(embed=closed_embed)

        # Upload transcript to transcript archive channel if configured
        if config.TRANSCRIPT_CHANNEL_ID:
            archive_chan = channel.guild.get_channel(config.TRANSCRIPT_CHANNEL_ID)
            if archive_chan:
                try:
                    await archive_chan.send(
                        content=f"📄 **Transcript for Ticket {db_ticket.ticket_code}** (Closed by {closed_by.mention}):",
                        file=discord.File(file_path, filename=f"transcript_{db_ticket.ticket_code}.html")
                    )
                except Exception as e:
                    logger.error(f"Failed to send transcript to archive channel: {e}")

        # Send deletion notification
        await channel.send("⏳ **Notice**: This channel will be permanently deleted in 5 seconds...")
        await asyncio.sleep(5)
        await channel.delete(reason=f"HELZERX Ticket {db_ticket.ticket_code} closed.")


ticket_manager = TicketManager()
