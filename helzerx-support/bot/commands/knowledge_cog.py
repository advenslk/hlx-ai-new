"""
HELZERX AI Support - Knowledge Base & RAG Slash Commands
Implements /knowledge-add, /knowledge-search, /knowledge-remove.
"""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from bot.config import config
from bot.security.permissions import require_staff, require_admin
from bot.knowledge.manager import knowledge_manager
from bot.database.session import AsyncSessionLocal
from bot.database import crud
from bot.database.models import KnowledgeDocument
from sqlalchemy import select


class KnowledgeCog(commands.Cog):
    """Cog for managing RAG documentation and FAQs."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="knowledge-search", description="Tests RAG semantic search across verified HELZERX documentation.")
    @app_commands.describe(query="Technical query, error message, or hosting question")
    @require_staff()
    async def knowledge_search_command(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(ephemeral=True)

        results = knowledge_manager.rag.search(query, top_k=3)
        if not results:
            await interaction.followup.send(f"🔍 No matching documentation found for: `{query}`", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Knowledge Search: {query[:50]}",
            color=config.BRAND_COLOR
        )

        for chunk, score in results:
            content_preview = chunk.content[:250].strip() + ("..." if len(chunk.content) > 250 else "")
            embed.add_field(
                name=f"{chunk.title} (Relevance Score: {score})",
                value=f"**Category:** `{chunk.category}`\n```markdown\n{content_preview}\n```",
                inline=False
            )

        embed.set_footer(text=config.BRAND_FOOTER)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="knowledge-add", description="Adds a new verified guide or FAQ to the HELZERX Knowledge Base.")
    @app_commands.describe(
        title="Document title",
        category="Category (e.g. minecraft, vps, technical, billing)",
        content="Markdown formatted documentation content",
        tags="Optional comma-separated tags"
    )
    @require_admin()
    async def knowledge_add_command(
        self,
        interaction: discord.Interaction,
        title: str,
        category: str,
        content: str,
        tags: Optional[str] = None
    ):
        await interaction.response.defer(ephemeral=True)

        # Index in memory
        knowledge_manager.add_document(
            title=title,
            category=category,
            content=content,
            tags=tags or ""
        )

        # Save to database
        async with AsyncSessionLocal() as session:
            slug = "".join(c for c in title.lower() if c.isalnum() or c == "-")[:80]
            doc = KnowledgeDocument(
                title=title,
                slug=f"{slug}-{int(interaction.id % 10000)}",
                category=category,
                content=content,
                tags=tags or "",
                is_verified=True
            )
            session.add(doc)
            await crud.log_audit_event(
                session=session,
                action="KNOWLEDGE_DOC_ADDED",
                actor_id=interaction.user.id,
                actor_name=interaction.user.name,
                details=f"Title: {title}, Cat: {category}"
            )
            await session.commit()

        await interaction.followup.send(
            f"✅ **Documentation Added**: Successfully indexed `{title}` for RAG context retrieval.",
            ephemeral=True
        )

    @app_commands.command(name="knowledge-remove", description="Removes a document from the HELZERX Knowledge Base.")
    @app_commands.describe(title_query="Title or slug of the document to remove")
    @require_admin()
    async def knowledge_remove_command(self, interaction: discord.Interaction, title_query: str):
        # Remove matching documents from list and rebuild index
        before_count = len(knowledge_manager.documents)
        knowledge_manager.documents = [
            d for d in knowledge_manager.documents
            if title_query.lower() not in d["title"].lower()
        ]
        removed_count = before_count - len(knowledge_manager.documents)

        # Rebuild RAG index
        knowledge_manager._init_index()

        await interaction.response.send_message(
            f"🗑️ Removed `{removed_count}` document(s) matching `{title_query}` from RAG index.",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(KnowledgeCog(bot))
