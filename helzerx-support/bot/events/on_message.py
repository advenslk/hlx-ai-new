"""
HELZERX AI Support - Message Event Listener
Intercepts messages in ticket channels, enforces rate limits & security sanitization, and runs conversational AI.
"""
from __future__ import annotations

import discord
from bot.config import config
from bot.database.session import AsyncSessionLocal
from bot.database import crud
from bot.security.guards import check_prompt_injection
from bot.security.sanitizer import sanitize_sensitive_data
from bot.security.rate_limiter import rate_limiter
from bot.ai.language_detector import detect_language
from bot.ai.prompts import build_ticket_ai_prompt
from bot.ai.client import ai_client
from bot.knowledge.manager import knowledge_manager
from bot.embeds.ticket_embeds import create_ai_response_embed
from bot.utils.logger import logger


async def handle_ticket_message(message: discord.Message) -> None:
    """Processes messages sent inside active ticket channels."""
    if message.author.bot or not message.guild or not isinstance(message.channel, discord.TextChannel):
        return

    # Check if channel is an active ticket
    async with AsyncSessionLocal() as session:
        db_ticket = await crud.get_ticket_by_channel(session, message.channel.id)
        if not db_ticket or db_ticket.status == "CLOSED":
            return

        is_customer = (db_ticket.creator and db_ticket.creator.discord_id == message.author.id)
        author_role = "customer" if is_customer else "staff"

        # 1. Sensitive Data Sanitization
        raw_content = message.content
        sanitized_content, was_sanitized = sanitize_sensitive_data(raw_content)

        if was_sanitized and config.MASK_SENSITIVE_DATA:
            try:
                # Optionally warn user in ephemeral or channel note
                await message.channel.send(
                    f"⚠️ {message.author.mention}, **Sensitive Data Redacted**: We detected a potential password, API key, or SSH secret in your message. For your security, credentials have been redacted in ticket logs. Never share sensitive keys.",
                    delete_after=12
                )
            except Exception:
                pass

        # 2. Prompt Injection Detection
        is_injection, injection_reason = check_prompt_injection(raw_content)
        if is_injection:
            logger.warning(f"Security Alert: Prompt injection attempt in ticket {db_ticket.ticket_code}: {injection_reason}")
            await crud.log_audit_event(
                session=session,
                action="SECURITY_ALERT_INJECTION",
                actor_id=message.author.id,
                actor_name=message.author.name,
                ticket_id=db_ticket.id,
                details=f"Reason: {injection_reason}"
            )
            await message.channel.send(
                "🛡️ **Security Notice**: Your message was flagged for containing restricted system override instructions. Support interactions are strictly logged and monitored.",
                delete_after=10
            )
            # Log sanitized message and exit without triggering AI
            await crud.save_ticket_message(
                session=session,
                ticket_id=db_ticket.id,
                author_id=message.author.id,
                author_name=message.author.name,
                author_role=author_role,
                content=sanitized_content,
                discord_message_id=message.id
            )
            await session.commit()
            return

        # 3. Rate Limiting Check (for customers)
        if is_customer:
            allowed, retry_after = rate_limiter.is_allowed(message.author.id)
            if not allowed:
                await message.channel.send(
                    f"⏳ **Rate Limit**: Please slow down. You can send another message in `{retry_after}` seconds.",
                    delete_after=6
                )
                return

        # 4. Save Customer/Staff Message to Database
        await crud.save_ticket_message(
            session=session,
            ticket_id=db_ticket.id,
            author_id=message.author.id,
            author_name=message.author.name,
            author_role=author_role,
            content=sanitized_content,
            has_sanitization=was_sanitized,
            discord_message_id=message.id
        )
        await session.commit()

        # If staff speaks, we do not trigger AI
        if not is_customer:
            return

        # If AI is disabled on this ticket, skip auto-response
        if not db_ticket.ai_enabled or not config.AI_AUTO_RESPONSE_ENABLED:
            return

        # 5. Build Context and Invoke AI Response
        async with message.channel.typing():
            detected_lang, _ = detect_language(sanitized_content)

            # Retrieve RAG context
            rag_context = knowledge_manager.search(sanitized_content, top_k=2)

            system_prompt = build_ticket_ai_prompt(
                ticket_code=db_ticket.ticket_code,
                category=db_ticket.category,
                priority=db_ticket.priority,
                customer_name=message.author.display_name,
                initial_subject=db_ticket.initial_subject or "",
                initial_description=db_ticket.initial_description or "",
                server_identifier=db_ticket.server_identifier or "",
                retrieved_knowledge=rag_context,
                detected_language=detected_lang
            )

            # Compile conversation history
            history_messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Grab previous messages from this ticket session
            for past_m in db_ticket.messages[-6:]:
                role = "assistant" if past_m.author_role == "ai" else "user"
                history_messages.append({"role": role, "content": past_m.content})

            history_messages.append({"role": "user", "content": sanitized_content})

            try:
                reply_text, p_toks, c_toks = await ai_client.generate_response(history_messages)

                # Persist AI answer
                await crud.save_ticket_message(
                    session=session,
                    ticket_id=db_ticket.id,
                    author_id=message.guild.me.id,
                    author_name="HELZERX AI Support",
                    author_role="ai",
                    content=reply_text,
                    detected_language=detected_lang,
                    tokens_prompt=p_toks,
                    tokens_completion=c_toks
                )
                db_ticket.ai_turn_count = (db_ticket.ai_turn_count or 0) + 1
                await session.commit()

                # Send AI message directly as normal text without embeds (human engineer style)
                if len(reply_text) <= 2000:
                    await message.channel.send(content=reply_text)
                else:
                    for i in range(0, len(reply_text), 1950):
                        await message.channel.send(content=reply_text[i:i+1950])

            except Exception as ai_err:
                logger.error(f"Failed to generate AI response for ticket {db_ticket.ticket_code}: {ai_err}")
